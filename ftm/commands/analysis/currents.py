import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

laser_rate = 100
labels = {
    "att": "Laser attenuator (a.u.)",
    "vampl": "Amplification voltage (V)",
    "power": "Laser power (µJ)",
    "current": "Current (nA)",
    "charge": "Primary charge (fC)",
}


def analyze_scan(
    input_file, output_directory, variable="att", plot_directory=None, gain_file=None
):
    def analyze_currents(df):
        df_on = df[df["source_status"] == True]
        df_off = df[df["source_status"] == False]

        mean_df_on = df_on.mean(axis=0)
        mean_df_off = df_off.mean(axis=0)
        mean_df_on["err_current"] = df_on["current"].std(axis=0)
        mean_df_off["err_current"] = df_off["current"].std(axis=0)
        return mean_df_on.drop("source_status")

    os.makedirs(output_directory, exist_ok=True)
    if plot_directory:
        os.makedirs(plot_directory, exist_ok=True)

    currents_df = pd.read_csv(input_file, sep=";")
    currents_group = currents_df.groupby(variable)
    output_df = currents_group.apply(analyze_currents)
    output_df["current"] -= max(output_df["current"])

    if gain_file:
        gain_df = pd.read_csv(gain_file, sep=";")
        constant, slope = gain_df["constant"].unique(), gain_df["slope"].unique()
        output_df["gain"] = np.exp(constant + slope * (output_df["vampl"] + 10))
        output_df["charge"] = -output_df["current"] / output_df["gain"] / laser_rate
        output_df["err_charge"] = (
            output_df["err_current"] / output_df["gain"] / laser_rate
        )

    output_df.to_csv(output_directory / "results.csv", sep=";")

    if plot_directory:
        current_fig, current_ax = plt.figure(figsize=(12, 9)), plt.axes()
        current_ax.errorbar(
            output_df[variable],
            -output_df["current"] * 1e9,
            yerr=output_df["err_current"] * 1e9,
            fmt=".",
        )
        current_ax.set_xlabel(labels[variable])
        current_ax.set_ylabel(labels["current"])
        current_fig.savefig(plot_directory / "current.png")

        if gain_file:
            charge_fig, charge_ax = plt.figure(figsize=(12, 9)), plt.axes()
            charge_ax.errorbar(
                output_df[variable],
                output_df["charge"] * 1e15,
                yerr=output_df["err_charge"] * 1e15,
                fmt=".",
            )
            charge_polynomial = np.polyfit(
                output_df[variable], output_df["charge"], deg=5
            )
            charge_ax.plot(
                output_df[variable],
                np.polyval(charge_polynomial, output_df[variable]) * 1e15,
                color="red",
            )
            charge_ax.set_xlabel(labels[variable])
            charge_ax.set_ylabel(labels["charge"])
            charge_fig.savefig(plot_directory / "charge.png")
