def loop_escape_objective(target, tries, only_score=True, test_full=False, callback=None, success=4):
    """
    `target` should be a glitching function returning one of four values when executed:
    0: No glitch
    1: Successful loop escape
    2: Device reset
    3: Unknown (optional. Indicates external error)
    """
    # fail, success, reset, unknown
    final_res = [0, 0, 0, 0, 0]
    for _ in range(tries):
        res: int = target()
        final_res[res] += 1

        if callback is not None and sum(final_res) > 6:
            callback(res)

        print(f"\r{final_res}", end='')

        # If reset too many times with no successes, give up
        if not test_full and final_res[2] > tries//4 and final_res[1] + final_res[4] == 0:
            break
    print()


    # TODO: Different possible score calculations
    #       This one finds rate of success
    score = final_res[success]/sum(final_res)

    # If we didn't find any glitches, punish resets
    # Dividing by 10 to make the penalty less severe
    if only_score and score == 0:
        algo = 1 + (final_res[2]/sum(final_res))/10
        score = 1 - algo


    # 0 is perfect
    # 1 is no resets
    # 1.1 is all resets

    if only_score:
        return 1 - score
    else:
        return 1 - score, final_res
