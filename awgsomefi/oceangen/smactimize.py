import matplotlib.pyplot as plt

from awgsomefi.awgctrl.devices.awggeneric import ChannelID

from awgsomefi.awgctrl.parameters.wave import ArbWave
from awgsomefi.awgctrl import AWG
from awgsomefi.config import config
from awgsomefi.parameters.optimization_params import SmacParams
from awgsomefi.parameters.voltage import VoltageBound
from awgsomefi.parameters.waveform import GlitchParams

from . import glitch

from smac import HyperparameterOptimizationFacade as HPOFacade, Scenario
from ConfigSpace import Configuration, ConfigurationSpace, Float, Integer, conditions

class NECOpt:

    def __init__(self, channel: ChannelID, timing, target) -> None:
        self.channel = channel
        self.timing = timing
        self.target = target
        self.opt_config: SmacParams = config['optimization']['smac']
        self.awg: AWG = config['lab']['AWG']

    @property
    def configspace(self) -> ConfigurationSpace:
        cs: ConfigurationSpace = ConfigurationSpace(seed=3)
        cons = []

        minn, maxn = self.opt_config.point_count

        cs.add_hyperparameters([Integer("n", (minn, maxn))])

        device_voltages = self.awg.channel_voltages[self.channel]
        for i in range(maxn):
            cs.add_hyperparameters([Float(f"v{i}", (device_voltages.low, device_voltages.high))])
            if minn <= i:
                cons.append(conditions.GreaterThanCondition(child=cs[f'v{i}'], parent=cs['n'], value=i))


            cs.add_hyperparameters([Integer(f"t{i}", self.opt_config.segment_length)])
            if minn <= i-1:
                cons.append(conditions.GreaterThanCondition(child=cs[f't{i}'], parent=cs['n'], value=i-1))

        timing_offset = Integer("offset", (-200, 200), default=0)
        cs.add_hyperparameters([timing_offset])

        cs.add_conditions(cons)

        return cs

    def train(self, cs: Configuration, seed: int = 3):
        timing_offset = cs["offset"]
        n = cs['n']

        device_voltages: VoltageBound = self.awg.channel_voltages[self.channel]

        voltages: list[float] = [cs[f"v{i}"] for i in range(n)]
        rand_segments: list[float] = [cs[f"t{i}"] for i in range(n+1)]
    
        glitch_params = glitch.generate_modular_params(
                self.channel,
                voltages,
                rand_segments,
                self.opt_config.slew_limit / 100 # Convert from /100ns to /1ns
        )
    
        waveform, _ = glitch.generate_hermite_spline(self.channel, glitch_params.norm_ts, glitch_params.voltages, plot=False)
        try_glitch = ArbWave.from_period(period=glitch_params.period, waveform=waveform, phase=0)
    
        self.awg.setup_arbitrary(self.channel, "nec_glitch", try_glitch)
        self.awg.set_trig_delay(self.channel, self.timing + timing_offset)
    
        print("Params:", glitch_params)
        print("at time", timing_offset)
    
        score_vec, _ = self.target(10)

        tries = sum(score_vec)
        print(f"Success Single:", f"{score_vec[1]}/{tries}")
        print(f"Success Double:", f"{score_vec[2]}/{tries}")
        print(f"False Positive Count:", f"{score_vec[3]}/{tries}")
        print(f"Errors:", f"{score_vec[4]}/{tries}")
        print()
    
        return dict(
                single=1-(score_vec[1]/tries),
                double=1-(score_vec[2]/tries),
                fp=score_vec[3]/tries,
                reset=score_vec[4]/tries,
        )


def smac_view_nec(channel: int, target, timing):
    """
        Print results of previous run
    """
    model = NECOpt(channel, timing, target)

    smac_conf: SmacParams = config['optimization']['smac']
    n_calls = smac_conf.initial_points
    calls = smac_conf.total_points

    scenario = Scenario(
            model.configspace, deterministic=False, n_trials=calls,
            objectives=["single", "double", "fp", "reset"],
            seed=3
    )
    initial_design = HPOFacade.get_initial_design(scenario, n_configs=n_calls)

    smac = HPOFacade(
            scenario, model.train ,initial_design=initial_design, overwrite=False,
            multi_objective_algorithm=HPOFacade.get_multi_objective_algorithm(
                scenario,
                objective_weights = [20, 18, 1, 2]
            )
    )
    #configs = smac.runhistory.get_configs()
    #print("conf", configs)


    incumbents = smac.intensifier.get_incumbents()
    singles = []
    doubles = []
    print("Testing", len(incumbents))
    for c in incumbents:
        #print(smac.runhistory.average_cost(i))
        out = model.train(c)
        singles.append(out['single'])
        doubles.append(out['double'])

    plt.scatter(singles, doubles)
    plt.xlabel("Singles")
    plt.ylabel("Doubles")
    plt.show()


    #print("best",incumbents)

    return incumbents

def smac_optimize_nec(channel: ChannelID, target, timing):
    """
    ncalls: Number of random calls
    calls: Total calls in the optimization
    """
    smac_conf: SmacParams = config['optimization']['smac']


    n_calls = smac_conf.initial_points
    calls = smac_conf.total_points

    model = NECOpt(channel, timing, target)
    scenario = Scenario(
            model.configspace, deterministic=False, n_trials=calls,
            objectives=["single", "double", "fp", "reset"],
            seed=3
    )
    initial_design = HPOFacade.get_initial_design(scenario, n_configs=n_calls)

    smac = HPOFacade(
            scenario, model.train ,initial_design=initial_design, overwrite=True,
            multi_objective_algorithm=HPOFacade.get_multi_objective_algorithm(
                scenario,
                # Many single byte glitches, fewer double byte glitches, few false positives few resets
                objective_weights = [20, 18, 1, 2]
            )
    )
    incumbents = smac.optimize()
    print("config:", incumbents)

    #default_cost = smac.validate(model.configspace.get_default_configuration())
    #print(f"Default cost: {default_cost}")

    for incumbent in incumbents:
        incumbent_cost = smac.validate(incumbent)
        print(f"Incumbent cost: {incumbent_cost}")

    return incumbents
