#!/usr/bin/python3

import sys
import pathlib
import argparse

from ftm.modules import hv, laser, attenuator, scope
import ftm.commands.scans.efficiency_voltage
import ftm.commands.scans.efficiency_laser
import ftm.commands.scans.threshold
import ftm.commands.analysis.efficiency
import ftm.commands.analysis.efficiency_laser
import ftm.commands.analysis.threshold
import ftm.commands.legacy

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True, dest="command")
    
    # "scan" command
    scan_parser = subparsers.add_parser("scan")
    scan_subparsers = scan_parser.add_subparsers(required=True, dest="subcommand")
    # "analyze" command
    analyze_parser = subparsers.add_parser("analyze")
    analyze_subparsers = analyze_parser.add_subparsers(required=True, dest="subcommand")
    # "plot" command
    plot_parser = subparsers.add_parser("plot")
    plot_subparsers = plot_parser.add_subparsers(required=True, dest="subcommand")
    # "import" command
    import_parser = subparsers.add_parser("import")
    import_subparsers = import_parser.add_subparsers(required=True, dest="subcommand")

    # "scan efficiency voltage" subcommand
    parser_scan_efficiency = scan_subparsers.add_parser("efficiency-voltage")
    parser_scan_efficiency.add_argument("config", type=pathlib.Path, help="Configuration file in YAML format")
    parser_scan_efficiency.add_argument("output", type=pathlib.Path, help="Output csv file")
    parser_scan_efficiency.set_defaults(func=lambda args: ftm.commands.scans.efficiency_voltage.scan(args.config, args.output))
    # "scan threshold" subcommand
    parser_scan_efficiency = scan_subparsers.add_parser("threshold")
    parser_scan_efficiency.add_argument("config", type=pathlib.Path, help="Configuration file in YAML format")
    parser_scan_efficiency.add_argument("output", type=pathlib.Path, help="Output csv file")
    parser_scan_efficiency.set_defaults(func=lambda args: ftm.commands.scans.threshold.scan(args.config, args.output))
    # "scan efficiency laser" subcommand
    parser_scan_efficiency = scan_subparsers.add_parser("efficiency-laser")
    parser_scan_efficiency.add_argument("config", type=pathlib.Path, help="Configuration file in YAML format")
    parser_scan_efficiency.add_argument("output", type=pathlib.Path, help="Output csv file")
    parser_scan_efficiency.set_defaults(func=lambda args: ftm.commands.scans.efficiency_laser.scan(args.config, args.output))
 
    # "analyze efficiency" subcommand
    #parser_analyze_efficiency = analyze_subparsers.add_parser("efficiency")
    #parser_analyze_efficiency.add_argument("input", type=pathlib.Path, help="Result of the efficiency scan")
    #parser_analyze_efficiency.add_argument("output", type=pathlib.Path, help="Output of the analysis")
    #parser_analyze_efficiency.set_defaults(func=lambda args: ftm.commands.analysis.efficiency.analyze(args.input, args.output))
    # "analyze efficiency-laser" subcommand
    parser_analyze_efficiency = analyze_subparsers.add_parser("efficiency-laser")
    parser_analyze_efficiency.add_argument("input", type=pathlib.Path, help="Raw result of the efficiency scan")
    parser_analyze_efficiency.add_argument("output", type=pathlib.Path, help="Output of the analysis")
    parser_analyze_efficiency.add_argument("threshold", type=float, help="Threshold in mV")
    parser_analyze_efficiency.add_argument("--plot", type=pathlib.Path, help="Plot directory", default=None)
    parser_analyze_efficiency.set_defaults(func=lambda args: ftm.commands.analysis.efficiency_laser.analyze(args.input, args.output, args.threshold, args.plot))
    # "analyze threshold" subcommand
    parser_analyze_threshold = analyze_subparsers.add_parser("threshold")
    parser_analyze_threshold.add_argument("input", type=pathlib.Path, help="Result of the threshold scan")
    parser_analyze_threshold.add_argument("output", type=pathlib.Path, help="Output of the analysis")
    parser_analyze_threshold.set_defaults(func=lambda args: ftm.commands.analysis.threshold.analyze(args.input, args.output))
    # "plot efficiency-laser" subcommand
    parser_plot_efficiency = plot_subparsers.add_parser("efficiency-laser")
    parser_plot_efficiency.add_argument("input", type=pathlib.Path, help="Analyzed result of the efficiency scan")
    parser_plot_efficiency.add_argument("output", type=pathlib.Path, help="Output file path")
    parser_plot_efficiency.set_defaults(func=lambda args: ftm.commands.analysis.efficiency_laser.plot(args.input, args.output))

    # "import scan" subcommand
    parser_import_scan = import_subparsers.add_parser("scan")
    parser_import_scan.add_argument("input", type=pathlib.Path, help="Input directory with current sweep data")
    parser_import_scan.add_argument("output", type=pathlib.Path, help="Output file path")
    parser_import_scan.set_defaults(func=lambda args: ftm.commands.legacy.import_scan(args.input, args.output))
    # "import gain" subcommand
    parser_import_gain = import_subparsers.add_parser("gain")
    parser_import_gain.add_argument("input", type=pathlib.Path, help="Input gain ROOT file")
    parser_import_gain.add_argument("output", type=pathlib.Path, help="Output file path")
    parser_import_gain.set_defaults(func=lambda args: ftm.commands.legacy.import_gain(args.input, args.output))


    # Parse the command line
    args = parser.parse_args()
    return args.func(args)

if __name__=='__main__':
    status = main()
    sys.exit(status)
