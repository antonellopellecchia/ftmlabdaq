#!/usr/bin/python3

import os
import time
import numpy as np
import pandas as pd

import commands.scans.configure as configure

from modules import scope

def scan(configuration_file, output_file):
    """Efficiency scan as a function of laser pulse energy and amplification voltage"""

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    setup = configure.parse_setup(configuration_file)
    scope_controller = scope.ScopeLecroy(setup['scope']['host'])

    acquisition_time = setup['measurement']['acquisition_time']
    channel = setup['measurement']['channel']

    print('')
    print('-----------------------')
    print('Starting measurement...')

    thresh_start = setup['measurement']['threshold']['start']
    thresh_end = setup['measurement']['threshold']['end']
    thresh_step = setup['measurement']['threshold']['step']
    thresh_range = np.arange(thresh_start, thresh_end, thresh_step)

    measurement_dict = {
        'threshold': list(),
        'rate': list(),
    }

    scope_controller.trigger_mode = 'NORM'
    print(f'Trigger mode {scope_controller.trigger_mode}')
    scope_controller.configure()

    for threshold in thresh_range:
        scope_controller.set_threshold(channel, threshold)

        print(f"Taking data with threshold {threshold} mV")
        rate = 0
        current_time = time.time()
        while time.time()-current_time < acquisition_time:
            # wait for scope to trigger and poll continuously:
            while not scope_controller.triggered:
                time.sleep(1e-7)
                if time.time()-current_time > acquisition_time: break
            rate += 1
        rate /= acquisition_time
        
        measurement_dict['threshold'].append(threshold)
        measurement_dict['rate'].append(rate)

        print('Finished taking data')
        measurement_df = pd.DataFrame(measurement_dict)
        measurement_df.to_csv(output_file, sep=';', index=False)
        print('Output file updated.')
        print('')

    print('Measurement finished.')

    measurement_df = pd.DataFrame(measurement_dict)
    measurement_df.to_csv(output_file, sep=';', index=False)
    print('Output file saved.')

    return 0