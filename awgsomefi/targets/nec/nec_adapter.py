from collections import defaultdict
import time

from TargetDriver.controllers import client_nec
from TargetDriver.controllers.controller import MCUError

RESETLESS_LIMIT = 16

def nec_disable():
    nec_reset_self()
    nec_shutdown()

def nec_reenable():
    try:
        nec_reset_self()
    except MCUError:
        nec_reset_self()
    nec_initialize()

def nec_short_checksum(block, startaddr, length=4, *args, **kwargs):
    """
    Run short checksum (will glitch)
    """
    #nec_reset_self()
    nec_initialize()
    start = block * 0x100 + startaddr
    with client_nec.NEC_78K0R() as client:
        checksum = client.short_checksum(start, start+length)
    print("GOT CHECKSUM", hex(checksum))
    nec_shutdown()
    return checksum

def mass_verify(block, couplet1, couplet2, data_block):
    nec_initialize()
    with client_nec.NEC_78K0R() as client:
        correct_bytes = client.mass_verify(block, couplet1, couplet2, data_block)
    nec_shutdown()
    return correct_bytes

def nec_initialize():
    """
    Turn off reeds
    Turn on reeds
    Get into FMPI
    """
    with client_nec.NEC_78K0R() as client:
        client.init_dut()
    return 0

def nec_checksum(startaddr, length=256, glitch=True, *args, **kwargs) -> list[int]:
    """
    Get checksum: glitch mode triggers after UART
    """
    with client_nec.NEC_78K0R() as client:
        checksum = client.checksum_full(startaddr, glitch=glitch, length=length)
    return checksum

def nec_reset_self():
    """
    Reset mcu
    """
    with client_nec.NEC_78K0R() as client:
        client.reset_self()

def nec_reset_dut():
    """
    Reset mcu
    """
    with client_nec.NEC_78K0R() as client:
        client.reset_dut()

def nec_shutdown():
    """
    Turn off reeds (safely)
    """
    with client_nec.NEC_78K0R() as client:
        ret = client.disable_dut()
    print("Shutting down")
    return ret


def nec_verify(addr, data):
    with client_nec.NEC_78K0R() as client:
        return client.verify(addr, data)

def nec_test_verify(addr):
    """
    Verify multiple of 4 blocks
    """
    with client_nec.NEC_78K0R() as client:
        counter = 0
        for i in range(1, 256//4):
            if counter >= 16:
                client.reset_self()
                client.init_dut()
                counter = 0
            ret = client.verify(addr, client_nec.firmware[0: i*4])
            print(i*4)
            counter += 1
            assert ret == 0
    return 0

def nec_leak_histogram(tries, idx, length=256):
    nec_initialize()
    reference_checksum = nec_checksum(idx*0x100, glitch=False, length=length)
    #nec_shutdown()

    def checksum_diff(checksum):
        #print(hex(checksum))
        if checksum != reference_checksum:
            difference = checksum - reference_checksum
            option1 = difference % (1 << 16)

            if option1 <= 0x1fe:
                print("positive possible:", hex(option1))
                return option1, checksum

        return 0, checksum

    nec_initialize()
    checksums = []
    try:
        for i in range(tries//100):
            print(f"Glitching batch {i}")
            checksums += list(nec_checksum(idx*0x100, glitch=True, length=length))
    except KeyboardInterrupt:
        print("Exiting")

    finally:
        nec_reset_self()
        nec_shutdown()

    return [checksum_diff(x) for x in checksums]


def nec_leak(tries, idx=4, length=256) -> list[int]:
    nec_initialize()
    reference_checksum = nec_checksum(idx*0x100, glitch=False, length=length)
    #nec_shutdown()


    error_count = []
    def checksum_diff(checksum):
        if checksum != reference_checksum:
            difference = checksum - reference_checksum
            option1 = difference % (1 << 16)

            if option1 <= 0x1fe:
                print("positive possible:", hex(option1))
                return option1

            if checksum == 0xffff:
                error_count.append(1)
                print("ERROR")

        return 0

    nec_initialize()

    checksums = []
    try:
        for i in range(tries//10):
            print(f"Glitching batch {i}")
            checksums += nec_checksum(idx*0x100, glitch=True, length=length)
    except KeyboardInterrupt:
        print("Exiting")

    finally:
        nec_reset_self()
        nec_shutdown()

    diffs = set(checksum_diff(checksum) for checksum in checksums)
    diffs.add(0)
    diffs.remove(0)
    print("diffs", diffs)
    print("Errors:", f"{sum(error_count)}/{len(checksums)}")
    return sorted(diffs)

def nec_leak_score(tries, expectation, idx=4, length=256, second_expectation=set()):
    nec_reenable()
    reference_checksum = nec_checksum(idx*0x100, glitch=False, length=length)

    def checksum_diff(checksum):
        # Reset
        if checksum == 0xffff:
            return 1.1

        if checksum != reference_checksum:
            difference = checksum - reference_checksum
            option1 = difference % (1 << 16)
            option2 = (-difference) % (1 << 16)

            if option1 <= 0x1fe:
                print("positive possible:", hex(option1))
                # Full poitns
                if option1 in expectation:
                    return 0
                #hits1[hex(option1)][offset] += 1
            
                # Half poitns
                if option1 in second_expectation:
                    return 1/2

        # Normal
        return 1

    score = 0
    count = 0
    nec_reenable()

    try:
        for i in range(tries//10):
            print(f"Glitching batch {i}")
            checksums: list[int] = nec_checksum(idx*0x100, glitch=True, length=length)
            score += sum(checksum_diff(checksum) for checksum in checksums)
            count += len(checksums)
            if checksums.count(0xffff) >= len(checksums)/3:
                print("Too many rests", f"{checksums.count(0xffff)}/{len(checksums)}")
                break
    except KeyboardInterrupt:
        print("Exiting")

    finally:
        nec_disable()

    return score/count

def nec_leak_score_vector(tries, expectation, idx=4, length=256, timelimit=False):
    nec_reenable()
    reference_checksum = nec_checksum(idx*0x100, glitch=False, length=length)

    fps = defaultdict(int)

    # no effect, Success0, Success1, FP, Reset
    score = [0, 0, 0, 0, 0]
    starting = time.time()

    def checksum_diff(checksum):
        # Reset
        if checksum == 0xffff:
            score[4] += 1

        elif checksum != reference_checksum:
            difference = checksum - reference_checksum
            option1 = difference % (1 << 16)

            if option1 <= 0x1fe:
                print("positive possible:", hex(option1))
                # Full poitns
                if option1 == expectation[0]:
                    score[1] += 1
                elif option1 == expectation[1]:
                    score[2] += 1
                else:
                    fps[option1] += 1
                    score[3] += 1
                #hits1[hex(option1)][offset] += 1
            else:
                # Normal
                score[0] += 1

            
        else:
        # Normal
            score[0] += 1

    nec_reenable()
    try:
        for i in range(tries//10):
            print(f"Glitching batch {i}")
            checksums = nec_checksum(idx*0x100, glitch=True, length=length)
            for c in checksums:
                checksum_diff(c)

            if timelimit and time.time() - starting >= 60*10:
                print("We're done here: 10 minutes passed")
                break

            if score[4] >= sum(score)/3:
                print("Too many rests", f"{score[4]}/{sum(score)}")
                break

    except KeyboardInterrupt:
        print("Exiting")

    finally:
        nec_disable()

    return score, fps
