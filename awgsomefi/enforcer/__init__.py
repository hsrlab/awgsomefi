from gym.envs.registration import register

register(
    id="Glitch-v0",
    entry_point='awgsomefi.enforcer.envs:GlitchEnv',
    reward_threshold=0.5,
    nondeterministic=True,
)

register(
    id="Glitch-scopless-v0",
    entry_point='awgsomefi.enforcer.envs:GlitchEnvScopeless',
    reward_threshold=0.5,
    nondeterministic=True,
)
