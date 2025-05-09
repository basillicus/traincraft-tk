#!/usr/bin/env python3

import os

import argparse
from ase.io import read, write
from ase.io.aims import write_aims
import numpy as np

'''
Reads the geometry and polarizability from an aims.out files in the prefix folders and generates a train.xyz file that contains the polarizabilities
'''

# Read the arguments
parser = argparse.ArgumentParser(
    prog='fhi_convert_polarizabilities_aims2train.py',
    description='Reads polarizabilities from aims.out files in the prefix folders and generates a train.xyz file',
)

inputfile = 'aims.out'
outputfile = 'train.xyz'
# outputfile_extxyz = 'sampled.extxyz'

parser.add_argument('-i', '--inputfile', default=inputfile,
                    help='input file: aims.out . Read in the aims outputfile to extract the forces (and maybe polarizabilities)')
parser.add_argument('-o', '--outputfile', default=outputfile,
                    help='output file: train.xyz file.')
parser.add_argument('-p', '--prefix', default='md_sample_',
                    help='Prefix of the folders. [md_sample_]')
parser.add_argument('-n', '--samples', default=0,
                    help='Total number of geometries to sample. If == 0, all will be included [0]')
parser.add_argument('-k', '--no_fake_dipole', action="store_false", default=True,
                    help='Patch to include a fake dipole, when it is not calculated. MACE needs dipole and polarizavility. Use this and  set dipole_weight to 0 when training MACE')

parser.add_argument(
    "-l", "--list", default=None, help="File with  a list of files to be read]"
)

args = parser.parse_args()
inputfile = args.inputfile
outfile = args.outputfile
num_samples = int(args.samples)
prefix_folder = args.prefix
list_of_files = args.list
fake_dipole = args.no_fake_dipole

if list_of_files:
    with open(list_of_files, "r") as f:
        files = f.readlines()
        print(
            f"Reading {inputfile} files in path given in {list_of_files} ...",
            end="",
            flush=True,
        )
    subdirs = [os.path.dirname(file) for file in files]
else:
    print(f'Reading {inputfile} files in folders with prefix {prefix_folder} ...', end='', flush=True)
    # Get a list of subdirectories (folders) within the current directory
    subdirs = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith(prefix_folder)]
print('Done!')

indices = range(len(subdirs))
if num_samples > 0:
    indices = np.random.choice(len(subdirs), num_samples, replace=False)

final_samples = len(indices)
print(f'Writing {outputfile} with a total of {final_samples} samples ...', end='', flush=True)
# Loop over each subdir and read a files inside it
for i in indices:
    path = os.path.join(subdirs[i], inputfile)
    if os.path.exists(path):
        polarizability_tensor = []

        with open(path) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 'Polarizability (Bohr^3) :' in line:    # Line when using DFPT_centralised (new module)
                    for n in range(3):
                        polarizability_tensor.append(lines[i+1+n].split()[0:3])
                    polarizability_tensor = np.array(polarizability_tensor, dtype=float)
                # Full Polarizability tensor for crystals
                if 'DFPT for dielectric_constant:' in line:
                    for n in range(3):
                        polarizability_tensor.append(lines[i+1+n].split()[0:3])
                    polarizability_tensor = np.array(polarizability_tensor, dtype=float)
            if len(polarizability_tensor) == 0:
                print('File ', f.name, ' contains no polarizability')
                continue
            iaims = read(path)
            iaims.info['REF_polarizability'] = polarizability_tensor.flatten()
            if fake_dipole:
                iaims.info['REF_dipole'] = np.array([1.0,2.0,3.0])

            write(outputfile, iaims, append=True)
print('Done!')
