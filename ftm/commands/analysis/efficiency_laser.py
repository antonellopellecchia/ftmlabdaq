import os
import struct

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplhep

from ftm.modules.scope import Waveform

plt.style.use(mplhep.style.CMS)

def plot(input_file, output_dir):
    """Plot efficiency as a function of laser pulse intensity for each amplification voltage"""

    os.makedirs(output_dir, exist_ok=True)

    print("Reading input csv...")
    input_df = pd.read_csv(input_file)
    print("Calculating efficiency...")
    attenuation_groups = input_df.groupby("attenuation")
    result_dict = {
        "attenuation": list(),
        "amplification": list(),
        "amplitude": list(),
        "efficiency": list(),
        "err_efficiency": list()
    }
    for attenuation,df in attenuation_groups:
        result_dict["attenuation"].append(df["attenuation"].mean())
        result_dict["amplification"].append(df["amplification"].mean())
        result_dict["amplitude"].append(df["amplitude"].mean())
        fired, total = df[df["fired"]==True].size, df.size
        result_dict["efficiency"].append(fired/total)
        result_dict["err_efficiency"].append( fired/total * np.sqrt(1/fired + 1/total) )
    result_df = pd.DataFrame.from_dict(result_dict)
    result_df.to_csv(output_dir/"result.csv")

    eff_fig, eff_ax = plt.figure(figsize=(12,9)), plt.axes()
    eff_ax.errorbar(result_df["attenuation"], result_df["efficiency"], yerr=result_df["err_efficiency"], fmt=".", color="black")
    eff_ax.set_xlabel("Attenuator servo step (a.u.)")
    eff_ax.set_ylabel("Efficiency")
    eff_fig.savefig(output_dir/"efficiency.png")

def analyze(input_file, result_dir, threshold, plot_dir=None):
    """ unpack and analyze raw file """
   
    os.makedirs(result_dir, exist_ok=True)
    if plot_dir: os.makedirs(plot_dir/"signals", exist_ok=True)

    with open(input_file, "rb") as istream: iraw = istream.read()
   
    output_dict = {
        "attenuation": list(),
        "amplification": list(),
        "fired": list(),
        "amplitude": list()
    }

    offset = 0
    i = 0
    while True:
        """ unpack event """
        try:
            amplification, actual_attenuation, size_waveform_raw = struct.unpack_from(">ffi", iraw, offset)
        except struct.error: break # file finished, stop unpacking
        offset += struct.calcsize(">ffi")
        waveform_raw = iraw[offset:offset+size_waveform_raw]
        offset += size_waveform_raw
        print(f"\rRead {offset} bytes over {len(iraw)}...          ", end="")
        waveform = Waveform.unpack(waveform_raw, "IEEE488.2")

        output_dict["attenuation"].append(actual_attenuation)
        output_dict["amplification"].append(amplification)
        output_dict["fired"].append(waveform.max>threshold)
        output_dict["amplitude"].append(waveform.amplitude)

        # plot and count options:
        if plot_dir and i%1000==0: waveform.save_figure(plot_dir/f"signals/{amplification}V_{actual_attenuation}att.png")
        i += 1
    print("\nUnpacking completed.")
    
    output_df = pd.DataFrame.from_dict(output_dict)
    output_df.to_csv(result_dir/"output.csv")

    print("Analysis completed.")
