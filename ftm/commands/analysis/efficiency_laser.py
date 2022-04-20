import os
import struct
import pandas as pd
import matplotlib.pyplot as plt
import mplhep

from ftm.modules.scope import Waveform

plt.style.use(mplhep.style.CMS)

def plot(input_file, output_dir):
    """Plot efficiency as a function of laser pulse intensity for each amplification voltage"""

    def plot_efficiency(df):
        amplification = df.iloc[0]["amplification"]
        ax.plot(df["attenuation"], df["efficiency"], 'o-', label=f"{amplification} V")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    efficiency_df = pd.read_csv(input_file, sep=";")

    fig, ax = plt.figure(), plt.axes()
    efficiency_df.groupby(["amplification"]).apply(plot_efficiency)

    ax.set_xlabel("Laser pulse energy (µJ)")
    ax.set_ylabel("Efficiency")
    ax.legend(title="Amplification voltage")
    
    fig.savefig(os.path.join(output_dir, "efficiency.pny"))

def analyze(input_file, output_file, plot_dir=None):
    """ unpack and analyze raw file """
    
    if plot_dir: os.makedirs(plot_dir, exist_ok=True)

    with open(input_file, "rb") as istream: iraw = istream.read()
    
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
        if plot_dir and i%1000==0: waveform.save_figure(plot_dir/f"{amplification}V_{actual_attenuation}att.png")
        i += 1

    print("\nAnalysis completed.")
