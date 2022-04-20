#!/usr/bin/python3

import sys
import pathlib
import argparse

from modules import hv, laser, attenuator, scope
import commands.scans.efficiency_voltage
import commands.scans.efficiency_laser
import commands.scans.threshold
import commands.analysis.efficiency
import commands.analysis.threshold

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True, dest="command")
    
    # "scan" command
    scan_parser = subparsers.add_parser("scan")
    scan_subparsers = scan_parser.add_subparsers(required=True, dest="subcommand")
    # "analyze" command
    analyze_parser = subparsers.add_parser("analyze")
    analyze_subparsers = analyze_parser.add_subparsers(required=True, dest="subcommand")

    # "scan efficiency voltage" subcommand
    parser_scan_efficiency = scan_subparsers.add_parser("efficiency-voltage")
    parser_scan_efficiency.add_argument("config", type=pathlib.Path, help="Configuration file in YAML format")
    parser_scan_efficiency.add_argument("output", type=pathlib.Path, help="Output csv file")
    parser_scan_efficiency.set_defaults(func=lambda args: commands.scans.efficiency_voltage.scan(args.config, args.output))
    # "scan threshold" subcommand
    parser_scan_efficiency = scan_subparsers.add_parser("threshold")
    parser_scan_efficiency.add_argument("config", type=pathlib.Path, help="Configuration file in YAML format")
    parser_scan_efficiency.add_argument("output", type=pathlib.Path, help="Output csv file")
    parser_scan_efficiency.set_defaults(func=lambda args: commands.scans.threshold.scan(args.config, args.output))
    # "scan efficiency laser" subcommand
    parser_scan_efficiency = scan_subparsers.add_parser("efficiency-laser")
    parser_scan_efficiency.add_argument("config", type=pathlib.Path, help="Configuration file in YAML format")
    parser_scan_efficiency.add_argument("output", type=pathlib.Path, help="Output csv file")
    parser_scan_efficiency.set_defaults(func=lambda args: commands.scans.efficiency_laser.scan(args.config, args.output))
 
    # "analyze efficiency" subcommand
    parser_analyze_efficiency = analyze_subparsers.add_parser("efficiency")
    parser_analyze_efficiency.add_argument("input", type=pathlib.Path, help="Result of the efficiency scan")
    parser_analyze_efficiency.add_argument("output", type=pathlib.Path, help="Output of the analysis")
    parser_analyze_efficiency.set_defaults(func=lambda args: commands.analysis.efficiency.analyze(args.input, args.output))
    # "analyze efficiency-laser" subcommand
    parser_analyze_efficiency = analyze_subparsers.add_parser("efficiency-laser")
    parser_analyze_efficiency.add_argument("input", type=pathlib.Path, help="Raw result of the efficiency scan")
    parser_analyze_efficiency.add_argument("output", type=pathlib.Path, help="Output of the analysis")
    parser_analyze_efficiency.set_defaults(func=lambda args: commands.analysis.efficiency_laser.analyze(args.input, args.output))
    # "analyze threshold" subcommand
    parser_analyze_threshold = analyze_subparsers.add_parser("threshold")
    parser_analyze_threshold.add_argument("input", type=pathlib.Path, help="Result of the threshold scan")
    parser_analyze_threshold.add_argument("output", type=pathlib.Path, help="Output of the analysis")
    parser_analyze_threshold.set_defaults(func=lambda args: commands.analysis.threshold.analyze(args.input, args.output))

    # Parse the command line
    args = parser.parse_args()
    return args.func(args)

if __name__=='__main__':
    status = main()
    sys.exit(status)
