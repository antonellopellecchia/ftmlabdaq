import yaml

from modules import hv, laser, attenuator, scope

def configure(configuration_file):
    with open(configuration_file, "r") as stream:
        try: setup = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return 1
    
    hv_controller = hv.BoardCaen(setup['hv']['port'])
    attenuator_controller = attenuator.Attenuator(setup['attenuator']['host'], setup['attenuator']['port'])
    scope_controller = scope.ScopeLecroy(setup['scope']['host'])

    return setup, hv_controller, attenuator_controller, scope_controller