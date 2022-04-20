import yaml

from ftm.modules import hv, laser, attenuator, scope

def parse_setup(configuration_file):
    with open(configuration_file, "r") as stream:
        try: setup = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return 1
    return setup
