import os
import pandas as pd
import matplotlib.pyplot as plt
import mplhep

plt.style.use(mplhep.style.CMS)

def analyze(input_file, output_file):
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
    
    fig.savefig(output_file)