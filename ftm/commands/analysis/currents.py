import os

import pandas as pd
from matplotlib import pyplot as plt

labels = {
    "att": "Laser attenuator (a.u.)",
    "vampl": "Amplification voltage (V)",
    "power": "Laser power (µJ)",
    "current": "Current (nA)"
}

def analyze_scan(input_file, output_directory, plot_directory=None, variable="att"):

    def analyze_currents(df):
        df_on = df[df["source_status"]==True]
        df_off = df[df["source_status"]==False]
        
        mean_df_on = df_on.mean(axis=0)
        mean_df_off = df_off.mean(axis=0)
        mean_df_on["current"] -= -1.1810635e-09
        return mean_df_on.drop("source_status")

    os.makedirs(output_directory, exist_ok=True)
    if plot_directory: os.makedirs(plot_directory, exist_ok=True)

    currents_df = pd.read_csv(input_file, sep=";")
    currents_group = currents_df.groupby(variable)
    output_df = currents_group.apply(analyze_currents)

    output_df.to_csv(output_directory/"results.csv")

    #output_dict = { variable: list(), "current": list() }
    #for value, df in currents_group:
    #    output_dict[variable].append(value)

    #    df_on = currents_df[currents_df["source_status"]=="on"]
    #    df_off = currents_df[currents_df["source_status"]=="off"]
    #    output_dict["current"].append(df_on.mean() - df_off.mean())

    #output_df = pd.DataFrame.from_dict(output_dict)
    #output_df.to_csv(output_directory/"results.csv")

    if plot_directory:
        scan_fig, scan_ax = plt.figure(figsize=(12,9)), plt.axes()
        scan_ax.plot(output_df[variable], output_df["current"])
        scan_ax.set_xlabel(labels[variable])
        scan_ax.set_ylabel(labels["current"])
        scan_fig.savefig(plot_directory/"current.png")

