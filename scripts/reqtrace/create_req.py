#!/usr/bin/env python3

import csv
import sys
import argparse

HEADER = """
/**
@page Requirements
@tableofcontents
@section Requirements

"""

FOOTER = """
*/
"""


args = None

def parse_csv(filename):
    grouped = dict()
    with open(filename) as fp:
            cr = csv.DictReader(fp)
            for row in cr:
                group = row['group']
                if row['normative'] == "FALSE":
                    continue
                if not grouped.get(group, None):
                    grouped[group] = []

                uid = row.get('uid')
                text = row.get('text').rstrip()
                name = row.get('header').rstrip()
                grouped[group].append({'id': uid, 'req': text, 'name': name})
    return grouped


SRS_HEADER = """
=====================
Software Requirements
=====================

This is the Software Requirements Specification.


Software capabilities
=====================
"""

"""
Saying hello
------------
.. item:: SRS_0001 Software saying hello
   :fulfills: SYS_0001

   The system will say hello, as stated in :item:`SYS_0001`


Saying goodbye
--------------
.. item:: SRS_0002 Software saying goodbye
   :fulfills: SYS_0002

   The systems will say goodbye

"""

def write_srs(grouped, filename):
    with open(filename, "w") as req:
        req.write(SRS_HEADER)

        for r in grouped.keys():
            comp = grouped[r]
            dashes = len(r) * "-"
            req.write(f"\n{r}\n{dashes}\n\n")
            for c in comp:
                id = c.get('id')
                name = c.get('name')
                reqtext = c.get('req')

                req.write(f".. item:: {id} {name}\n")
                req.write("\n")
                req.write(f"   {reqtext}\n\n")


def write_dox(grouped, filename):
    with open(filename, "w") as req:
        req.write(HEADER)

        for r in grouped.keys():
            comp = grouped[r]
            req.write("\n@section {}\n\n".format(r))
            for c in comp:
                req.write("@subsection {} {}: {}\n{}\n\n\n".format(c['id'], c['id'], c['name'], c['req']))

        req.write(FOOTER)


def parse_args():
    parser = argparse.ArgumentParser(
                description="Generate Requirement in various formats.")

    parser.add_argument('-c', '--csv-file',
            help="Requirements file in CSV format")

    parser.add_argument('-d', '--dox-file',
            help="Output file in DOX format for Doxygen.")

    parser.add_argument('--srs-file',
            help="Output file in RST format for Sphinx.")

    return parser.parse_args()

def main():
    global args
    args = parse_args()

    grouped = dict()
    if args.csv_file:
        print("Parsing CSV file...")
        grouped = parse_csv(args.csv_file)

    if grouped:
        if args.dox_file is not None:
            print(f"Writing DOX file {args.dox_file}...")
            write_dox(grouped, args.dox_file)

        if args.srs_file is not None:
            print(f"Writing SRS file {args.srs_file}...")
            write_srs(grouped, args.srs_file)

    else:
        print("Nothing to do...")

if __name__ == "__main__":
    main()
