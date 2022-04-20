#!/usr/bin/python3

import os, time, struct
import numpy as np
import pandas as pd
from tqdm import tqdm

import ftm.commands.scans.configure as configure
from ftm.modules import hv, laser, attenuator, scope

def scan(configuration_file, output_file):
    """Efficiency scan as a function of laser pulse energy and amplification voltage"""

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    print(os.path.basename(output_file))
    setup = configure.parse_setup(configuration_file)
    hv_controller = hv.BoardCaen(setup['hv']['port'])
    attenuator_controller = attenuator.Attenuator(setup['attenuator']['host'], setup['attenuator']['port'])
    scope_controller = scope.ScopeLecroy(setup['scope']['host'])

    channel_drift = setup['hv']['drift']
    channel_anode = setup['hv']['anode']
    print('VMON drift:', hv_controller.get_vmon(channel=channel_drift))
    print('VMON anode:', hv_controller.get_vmon(channel=channel_anode))

    print('Attenuation:', attenuator_controller.get_raw())
    attenuator_controller.set_raw(5200)
    time.sleep(2)
    print('Attenuation:', attenuator_controller.get_raw())
    
    # Actual efficiency measurement
    print('')
    print('-----------------------')
    print('Starting measurement...')

    att_start = setup['measurement']['attenuation_raw']['start']
    att_end = setup['measurement']['attenuation_raw']['end']
    att_step = setup['measurement']['attenuation_raw']['step']
    att_range = np.arange(att_start, att_end, att_step)

    drift_field = setup['measurement']['drift_field']
    ampl_start = setup['measurement']['amplification']['start']
    ampl_end = setup['measurement']['amplification']['end']
    ampl_step = setup['measurement']['amplification']['step']
    ampl_range = np.arange(ampl_start, ampl_end, ampl_step)

    
    #= {
    #    'amplification': list(),
    #    'attenuation': list(),
    #    'efficiency': list(),
    #    'charge': list(),
    #}

    scope_controller.trigger_mode = 'NORM'
    print(f'Trigger mode {scope_controller.trigger_mode}')
    scope_controller.configure()

    #with open("a.out", "wb") as fout:
    #    waveform_raw = scope_controller.get_waveform_raw(setup['measurement']['signal'])
    #    print(len(waveform_raw))
    #    fout.write(waveform_raw)
    #    fout.write(struct.pack(">if", 10, 42.3))
    #return 0

    for amplification in ampl_range:

        vset_anode = amplification
        vset_drift = drift_field
        print(f'Setting {vset_anode} V to anode and {vset_drift} to drift...')
        hv_controller.set_voltage(channel_drift, vset_drift)
        hv_controller.set_voltage(channel_anode, vset_anode)
        time.sleep(10)

        for attenuation in att_range:
            print(f'Setting attenuation to {attenuation}...')
            attenuator_controller.set_raw(attenuation)
            time.sleep(2) # wait for servo in attenuator to move
            actual_attenuation = attenuator_controller.get_raw()
            print(f'Attenuation set to {actual_attenuation:1.2f}.')

            vmon_anode = hv_controller.get_vmon(channel_anode)
            vmon_drift = hv_controller.get_vmon(channel_drift)
            print(f'{vmon_anode} V on anode, {vmon_drift} V on drift')
            if abs(vmon_anode-vset_anode)>10 or abs(vmon_drift-vset_drift)>10:
                print('WARNING: trip?')

            print('Taking data...')

            """Take nsignals waveforms and save as raw"""
            nsignals = setup['measurement']['nsignals']
            threshold = setup['measurement']['threshold']
            count_over_thr = 0
            charge_avg = 0
            for isignal in tqdm(range(nsignals)):
                # wait for scope to trigger and poll continuously:
                while not scope_controller.triggered: time.sleep(1e-3)
                
	        # save data to raw file:
                waveform_raw = scope_controller.get_waveform_raw(setup['measurement']['signal'])
                with open(output_file, "ab") as ostream:
                    ostream.write(struct.pack(">ffi", amplification, actual_attenuation, len(waveform_raw)))
                    ostream.write(waveform_raw) 
            #measurement_raw += "\n" 
            #measurement_raw += str(amplification)
            #measurement_raw += str(actual_attenuation)
            #measurement_raw += waveform_raw

            time.sleep(30)
            print('Finished taking data')
            print('')

    print('Measurement finished.')

    attenuator_controller.set_attenuation(0)
    print('Laser attenuation set to 0.')

    return 0
