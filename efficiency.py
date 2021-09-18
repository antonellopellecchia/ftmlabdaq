#!/usr/bin/python3

import os, sys
import pathlib
import yaml
import argparse
from modules import hv, laser, attenuator, scope

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=pathlib.Path, help="Configuration file in YAML format")
    args = parser.parse_args()

    with open(args.config, "r") as stream:
        try: setup = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return 1
    
    hv_controller = hv.Board('CAEN', setup['hv']['port'])
    #attenuator_controller = attenuator.Attenuator(setup['attenuator']['host'], setup['attenuator']['port'])
    scope_controller = scope.Scope('LECROY', setup['scope']['host'])

    channel = setup['hv']['channel']
    print('VSET:', hv_controller.get_vset(channel=channel))
    print('VMON:', hv_controller.get_vmon(channel=channel))
    
    return 0

if __name__=='__main__':
    status = main()
    sys.exit(status)