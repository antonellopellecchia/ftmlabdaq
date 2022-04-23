import os
import pandas as pd
import matplotlib.pyplot as plt
import mplhep

plt.style.use(mplhep.style.CMS)


def analyze(input_file, output_file):
    """Plot signal rate as a function of oscilloscope threshold"""

    def plot_efficiency(df):
        amplification = df.iloc[0]["amplification"]
        ax.plot(df["attenuation"], df["efficiency"], "o-", label=f"{amplification} V")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    thr_scan_df = pd.read_csv(input_file, sep=";")

    fig, ax = plt.figure(), plt.axes()
    ax.plot(abs(thr_scan_df["threshold"]), thr_scan_df["rate"], "o")
    ax.set_yscale("log")

    ax.set_xlabel("Threshold (mV)")
    ax.set_ylabel("Event rate (Hz)")

    fig.savefig(output_file)
