import yaml
import os
import glob

from .parsers import parsers

cwd = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(cwd, "configurations")

def read_yaml(filepath):
    glitch_params = {}
    with open(filepath) as fd:
        try:
            glitch_params = yaml.safe_load(fd)
        except yaml.YAMLError as e:
            print(f"Failed to load configuration {os.path.basename(filepath)}: {e}")
    return glitch_params

def read_configs():
    config_result = {}
    configs = glob.glob(os.path.join(config_path, "*.yaml"))
    for config in configs:
        parsed_config = read_yaml(config)
        if parsed_config is not None:
            key_name = os.path.splitext(os.path.basename(config))[0]
            config_result[key_name] = parsed_config
    return config_result

raw_configurations = read_configs()
configurations = {
    name: parser(raw_configurations)
    for name, parser in parsers.items()
}
print("Loaded", configurations)
