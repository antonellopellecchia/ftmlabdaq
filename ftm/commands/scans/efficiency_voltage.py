#!/usr/bin/python3

import time
import numpy as np
import pandas as pd

import ftm.commands.scans.configure as configure

from ftm.modules import hv, laser, attenuator, scope

def scan(configuration_file, output_file):
    """Efficiency scan as a function of laser pulse energy and amplification voltage"""

    setup = configure.parse_setup(configuration_file)
    hv_controller = hv.BoardCaen(setup['hv']['port'])
    attenuator_controller = attenuator.Attenuator(setup['attenuator']['host'], setup['attenuator']['port'])
    scope_controller = scope.ScopeLecroy(setup['scope']['host'])

    channel_drift = setup['hv']['drift']
    channel_anode = setup['hv']['anode']
    print('VMON drift:', hv_controller.get_vmon(channel=channel_drift))
    print('VMON anode:', hv_controller.get_vmon(channel=channel_anode))

    print('Attenuation:', attenuator_controller.get_attenuation())
    attenuator_controller.set_attenuation(50)
    print('Attenuation:', attenuator_controller.get_attenuation())
    
    # Actual efficiency measurement
    print('')
    print('-----------------------')
    print('Starting measurement...')

    att_start = setup['measurement']['attenuation']['start']
    att_end = setup['measurement']['attenuation']['end']
    att_step = setup['measurement']['attenuation']['step']
    att_range = np.arange(att_start, att_end, att_step)

    drift_field = setup['measurement']['drift_field']
    ampl_start = setup['measurement']['amplification']['start']
    ampl_end = setup['measurement']['amplification']['end']
    ampl_step = setup['measurement']['amplification']['step']
    ampl_range = np.arange(ampl_start, ampl_end, ampl_step)

    measurement_dict = {
        'amplification': list(),
        'attenuation': list(),
        'efficiency': list(),
        'charge': list(),
    }

    scope_controller.trigger_mode = 'NORM'
    print(f'Trigger mode {scope_controller.trigger_mode}')
    scope_controller.configure()

    for amplification in ampl_range:

        vset_anode = amplification
        vset_drift = vset_anode + drift_field
        print(f'Setting {vset_anode} V to anode and {vset_drift} to drift...')
        hv_controller.set_voltage(channel_drift, vset_drift)
        hv_controller.set_voltage(channel_anode, vset_anode)
        time.sleep(10)

        for attenuation in att_range:
            print(f'Setting attenuation to {attenuation}%...')
            attenuator_controller.set_attenuation(attenuation)
            time.sleep(2) # wait for servo in attenuator to move
            actual_attenuation = attenuator_controller.get_attenuation()
            print(f'Attenuation set to {actual_attenuation:1.2f}%.')

            vmon_anode = hv_controller.get_vmon(channel_anode)
            vmon_drift = hv_controller.get_vmon(channel_drift)
            print(f'{vmon_anode} V on anode, {vmon_drift} V on drift')
            if abs(vmon_anode-vset_anode)>10 or abs(vmon_drift-vset_drift)>10:
                print('WARNING: trip?')

            print('Taking data...')

            """Take nsignals waveforms, compare amplitude with a threshold
            and save ratio counts over threshold/nsignals"""
            nsignals = setup['measurement']['nsignals']
            threshold = setup['measurement']['threshold']
            count_over_thr = 0
            charge_avg = 0
            for isignal in range(nsignals):
                # wait for scope to trigger and poll continuously:
                while not scope_controller.triggered: time.sleep(1e-3)
                waveform = scope_controller.get_waveform(setup['measurement']['signal'])
                #print(f'Triggered {isignal}, length {len(waveform)}, baseline {waveform.baseline}')
                waveform = waveform.subtract_baseline()

                #waveform.save_figure(f'wfs/{isignal}.png')
                if waveform.min < threshold: count_over_thr += 1
                charge_avg += waveform.charge

            efficiency = count_over_thr/nsignals
            charge_avg /= nsignals
            
            measurement_dict['amplification'].append(amplification)
            measurement_dict['attenuation'].append(actual_attenuation)
            measurement_dict['efficiency'].append(efficiency)
            measurement_dict['charge'].append(charge_avg)

            #time.sleep(30)
            print('Finished taking data')
            measurement_df = pd.DataFrame(measurement_dict)
            measurement_df.to_csv(output_file, sep=';', index=False)
            print('Output file updated.')
            print('')

    print('Measurement finished.')

    attenuator_controller.set_attenuation(attenuation)
    print('Laser attenuation set to 0.')

    measurement_df = pd.DataFrame(measurement_dict)
    measurement_df.to_csv(output_file, sep=';', index=False)
    print('Output file saved.')

    return 0
