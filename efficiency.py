#!/usr/bin/python3

import os, sys
import pathlib
import yaml
import argparse
import time
import numpy as np

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
    
    hv_controller = hv.BoardCaen(setup['hv']['port'])
    attenuator_controller = attenuator.Attenuator(setup['attenuator']['host'], setup['attenuator']['port'])
    scope_controller = scope.ScopeLecroy(setup['scope']['host'])

    channel = setup['hv']['channel']
    print('VSET:', hv_controller.get_vset(channel=channel))
    print('VMON:', hv_controller.get_vmon(channel=channel))

    print('Attenuation:', attenuator_controller.get_attenuation())
    attenuator_controller.set_attenuation(50)
    print('Attenuation:', attenuator_controller.get_attenuation())
    
    # Actual efficiency measurement
    print('')
    print('-----------------------')
    print('Starting measurement...')

    att_beginning = setup['measurement']['beginning']
    att_end = setup['measurement']['end']
    att_step = setup['measurement']['step']
    att_range = np.arange(att_beginning, att_end, att_step)

    efficiency_points, attenuation_points = list(), list()

    for attenuation in att_range:
        print(f'Setting attenuation to {attenuation}%...')
        attenuator_controller.set_attenuation(attenuation)
        time.sleep(2) # wait for servo in attenuator to move
        actual_attenuation = attenuator_controller.get_attenuation()
        print(f'Attenuation set to {actual_attenuation:1.2f}%.')

        vmon = hv_controller.get_vmon(channel=channel)
        print(f'VMON {vmon} V on channel {channel}')

        # do stuff here...
        print('Taking data...')

        """Take nsignals waveforms, compare amplitude with a threshold
        and save ratio counts over threshold/nsignals"""
        nsignals = setup['measurement']['nsignals']
        threshold = setup['measurement']['threshold']
        count_over_thr = 0
        for isignal in range(nsignals):
            # wait for scope to trigger and poll continuously:
            while not scope.triggered: time.sleep(1e-3)
            waveform = scope.waveform
            if waveform.min < threshold: count_over_thr += 1
        efficiency = count_over_thr/nsignals
        
        attenuation_points.append(actual_attenuation)
        efficiency_points.append(efficiency)
        print(efficiency_points)

        #time.sleep(30)
        print('Finished taking data')
        print('')

    print('Measurement finished.')



    return 0

if __name__=='__main__':
    status = main()
    sys.exit(status)