import os, re
import pathlib

import numpy as np
import pandas as pd
import uproot

def read_legacy(input_file, sep="\t"):
    with open(input_file) as istream: text = istream.read()
    points = text.split(sep)
    return list(map(float, points))

def import_scan(input_directory, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    input_files = os.listdir(input_directory)
    input_files = sorted([ f for f in input_files if pathlib.Path(f).suffix==".csv" ])

    #currents_dict = {
    #    "vdrift": list(),
    #    "vampl": list(),
    #    "att": list(),
    #    "source_status": list(),
    #    "time": list(),
    #    "current": list()
    #}
    current_data = list()
    for input_file in input_files:
        # read only picoammeter current files:
        filename_match = re.search("(\d+)_(\d+)_(\d+)_(\w+)_ammeter.csv", input_file)
        if not filename_match: continue
        
        # parse run settings:
        vdrift, vampl, att = map(float, filename_match.group(1, 2, 3))
        source_status = filename_match.group(4)

        if not source_status in ["on", "off"]:
            raise ValueError(f"Unknown source status: {source_status}")
        source_status = source_status=="on"

        print("Reading run", vdrift, vampl, att, source_status)
        # fill data dict:
        currents = read_legacy(input_directory/input_file)
        current_data += [
            (vdrift, vampl, att, source_status, t, current)
            for t, current in enumerate(currents)
        ]
        #currents_dict["current"] += currents
        #currents_dict["vdrift"] += vdrift*np.ones(len(currents))
        #currents_dict["vampl"] += vampl*np.ones(len(currents))
        #currents_dict["att"] += att*np.ones(len(currents))
        #currents_dict["source_status"] += source_status*np.ones(len(currents), dtype=bool)
        #currents_dict["time"] += np.arange(len(currents))

    currents_df = pd.DataFrame.from_records(current_data, columns=["vdrift", "vampl", "att", "source_status", "time", "current"])
    currents_df.to_csv(output_file, index=False, sep=";")

def import_gain(input_file, output_file):
    with uproot.open(input_file) as root_file:
        print(root_file["Graph;1"])
