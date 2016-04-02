#!/usr/bin/env python
"""
Creates pdb data files from lammps data files, given a template pdb file.
"""

from __future__ import print_function
import ConfigParser
from collections import defaultdict
import copy
import logging
import re
import sys
import argparse

from md_utils.md_common import InvalidDataError, warning, process_cfg, create_out_fname, list_to_file

__author__ = 'hmayes'


# Logging
logger = logging.getLogger('data2pdb')
logging.basicConfig(filename='data2pdb.log', filemode='w', level=logging.DEBUG)
# logging.basicConfig(level=logging.INFO)

# Error Codes
# The good status code
GOOD_RET = 0
INPUT_ERROR = 1
IO_ERROR = 2
INVALID_DATA = 3

# Constants #

# Config File Sections
MAIN_SEC = 'main'

# Config keys
PDB_TPL_FILE = 'pdb_tpl_file'
DATA_FILES = 'data_list_file'
ATOM_TYPE_DICT_FILE = 'atom_type_dict_file'
CENTER_ATOM = 'center_to_atom_num'
# PDB file info
PDB_LINE_TYPE_LAST_CHAR = 'pdb_line_type_last_char'
PDB_ATOM_NUM_LAST_CHAR = 'pdb_atom_num_last_char'
PDB_ATOM_TYPE_LAST_CHAR = 'pdb_atom_type_last_char'
PDB_RES_TYPE_LAST_CHAR = 'pdb_res_type_last_char'
PDB_MOL_NUM_LAST_CHAR = 'pdb_mol_num_last_char'
PDB_X_LAST_CHAR = 'pdb_x_last_char'
PDB_Y_LAST_CHAR = 'pdb_y_last_char'
PDB_Z_LAST_CHAR = 'pdb_z_last_char'
PDB_FORMAT = 'pdb_print_format'
LAST_PROT_ID = 'last_prot_atom'
OUT_BASE_DIR = 'output_directory'
MAKE_DICT_BOOL = 'make_dictionary_flag'

# data file info

# Defaults
DEF_CFG_FILE = 'data2pdb.ini'
# Set notation
DEF_CFG_VALS = {DATA_FILES: 'data_list.txt', ATOM_TYPE_DICT_FILE: 'atom_dict.csv',
                PDB_FORMAT: '{:s}{:s}{:s}{:s}{:4d}    {:8.3f}{:8.3f}{:8.3f}{:s}',
                PDB_LINE_TYPE_LAST_CHAR: 6,
                PDB_ATOM_NUM_LAST_CHAR: 11,
                PDB_ATOM_TYPE_LAST_CHAR: 17,
                PDB_RES_TYPE_LAST_CHAR: 22,
                PDB_MOL_NUM_LAST_CHAR: 28,
                PDB_X_LAST_CHAR: 38,
                PDB_Y_LAST_CHAR: 46,
                PDB_Z_LAST_CHAR: 54,
                LAST_PROT_ID: 0,
                OUT_BASE_DIR: None,
                MAKE_DICT_BOOL: False,
                }
REQ_KEYS = {PDB_TPL_FILE: str,
            }

# From data template file
NUM_ATOMS = 'num_atoms'
HEAD_CONTENT = 'head_content'
ATOMS_CONTENT = 'atoms_content'
TAIL_CONTENT = 'tail_content'

# For data template file processing
SEC_HEAD = 'head_section'
SEC_ATOMS = 'atoms_section'
SEC_TAIL = 'tail_section'


def read_cfg(f_loc, cfg_proc=process_cfg):
    """
    Reads the given configuration file, returning a dict with the converted values supplemented by default values.

    :param f_loc: The location of the file to read.
    :param cfg_proc: The processor to use for the raw configuration values.  Uses default values when the raw
        value is missing.
    :return: A dict of the processed configuration file's data.
    """
    config = ConfigParser.ConfigParser()
    good_files = config.read(f_loc)
    if not good_files:
        raise IOError('Could not read file {}'.format(f_loc))
    main_proc = cfg_proc(dict(config.items(MAIN_SEC)), DEF_CFG_VALS, REQ_KEYS)
    return main_proc


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = argparse.ArgumentParser(description='Creates pdb files from lammps data, given a template pdb file and'
                                                 'a dictionary of CHARMM and LAMMPS types for verifying that the atom'
                                                 'types on the corresponding lines align.'
                                                 'The required input file provides the location of the '
                                                 'template file, the file with a list of data files to convert, and '
                                                 'the dictionary file (CSV, with charmm type (exactly as it in the PDB)'
                                                 'followed by the lammps type (int).')
    parser.add_argument("-c", "--config", help="The location of the configuration file in ini "
                                               "format. See the example file /test/test_data/data2pdb/data2pdb.ini. "
                                               "The default file name is pdb2data.ini, located in the "
                                               "base directory where the program as run.",
                        default=DEF_CFG_FILE, type=read_cfg)
    args = None
    try:
        args = parser.parse_args(argv)
    except IOError as e:
        warning("Problems reading file:", e)
        parser.print_help()
        return args, IO_ERROR
    except KeyError as e:
        warning("Input data missing:", e)
        parser.print_help()
        return args, INPUT_ERROR

    return args, GOOD_RET


def process_pdb_tpl(cfg):
    tpl_loc = cfg[PDB_TPL_FILE]
    tpl_data = {HEAD_CONTENT: [], ATOMS_CONTENT: [], TAIL_CONTENT: []}

    atom_id = 0

    with open(tpl_loc) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            line_head = line[:cfg[PDB_LINE_TYPE_LAST_CHAR]]

            # head_content to contain Everything before 'Atoms' section
            # also capture the number of atoms
            if line_head == 'REMARK' or line_head == 'CRYST1':
                tpl_data[HEAD_CONTENT].append(line)

            # atoms_content to contain everything but the xyz
            elif line_head == 'ATOM  ':

                # By renumbering, handles the case when a PDB template has ***** after atom_id 99999.
                # For renumbering, making sure prints in the correct format, including num of characters:
                atom_id += 1
                if atom_id > 99999:
                    atom_num = format(atom_id, 'x')
                else:
                    atom_num = '{:5d}'.format(atom_id)
                # Alternately, use this:
                # atom_num = line[cfg[PDB_LINE_TYPE_LAST_CHAR]:cfg[PDB_ATOM_NUM_LAST_CHAR]]

                atom_type = line[cfg[PDB_ATOM_NUM_LAST_CHAR]:cfg[PDB_ATOM_TYPE_LAST_CHAR]]
                res_type = line[cfg[PDB_ATOM_TYPE_LAST_CHAR]:cfg[PDB_RES_TYPE_LAST_CHAR]]
                # There is already a try when calling the subroutine, so maybe I don't need to?
                mol_num = int(line[cfg[PDB_RES_TYPE_LAST_CHAR]:cfg[PDB_MOL_NUM_LAST_CHAR]])
                pdb_x = float(line[cfg[PDB_MOL_NUM_LAST_CHAR]:cfg[PDB_X_LAST_CHAR]])
                pdb_y = float(line[cfg[PDB_X_LAST_CHAR]:cfg[PDB_Y_LAST_CHAR]])
                pdb_z = float(line[cfg[PDB_Y_LAST_CHAR]:cfg[PDB_Z_LAST_CHAR]])
                last_cols = line[cfg[PDB_Z_LAST_CHAR]:]

                line_struct = [line_head, atom_num, atom_type, res_type, mol_num, pdb_x, pdb_y, pdb_z, last_cols]
                tpl_data[ATOMS_CONTENT].append(line_struct)

            # tail_content to contain everything after the 'Atoms' section
            else:
                tpl_data[TAIL_CONTENT].append(line)

    if logger.isEnabledFor(logging.DEBUG):
        f_name = create_out_fname('reproduced_tpl', ext='.pdb', base_dir=cfg[OUT_BASE_DIR])
        list_to_file(tpl_data[HEAD_CONTENT] + tpl_data[ATOMS_CONTENT] + tpl_data[TAIL_CONTENT],
                     f_name,
                     list_format=cfg[PDB_FORMAT])

    return tpl_data


def make_dict(cfg, data_tpl_content):
    atoms_pat = re.compile(r"^Atoms.*")
    num_atoms_pat = re.compile(r"(\d+).*atoms$")
    matched_atom_types = {}
    atom_type_dict = defaultdict(list)
    non_unique_charmm = []
    with open(cfg[DATA_FILES]) as f:
        for data_file in f:
            data_file = data_file.strip()
            with open(data_file) as d:
                section = SEC_HEAD
                atom_id = 0
                num_atoms = None
                for line in d:
                    line = line.strip()
                    # not currently keeping anything from the header; just check num atoms
                    if section == SEC_HEAD:
                        if atoms_pat.match(line):
                            section = SEC_ATOMS
                        elif num_atoms is None:
                            atoms_match = num_atoms_pat.match(line)
                            if atoms_match:
                                # regex is 1-based
                                num_atoms = int(atoms_match.group(1))

                    elif section == SEC_ATOMS:
                        if len(line) == 0:
                            continue
                        split_line = line.split()

                        lammps_atom_type = int(split_line[2])
                        charmm_atom_type = data_tpl_content[ATOMS_CONTENT][atom_id][2] + \
                                           data_tpl_content[ATOMS_CONTENT][atom_id][3]

                        # Making the dictionary; use charmm as unique key. Do this first to verify library.
                        if charmm_atom_type in matched_atom_types:
                            # Check that we don't have conflicting matching
                            if lammps_atom_type != matched_atom_types[charmm_atom_type]:
                                if charmm_atom_type not in non_unique_charmm:
                                    print('Verify that this charmm type can have multiple lammps types: ',
                                          charmm_atom_type)
                                    print('First collision for this charmm type occurred on atom:', atom_id + 1)
                                    non_unique_charmm.append(charmm_atom_type)
                        else:
                            matched_atom_types[charmm_atom_type] = lammps_atom_type

                        atom_type_dict[lammps_atom_type].append(charmm_atom_type)

                        atom_id += 1
                        # Check after increment because the counter started at 0
                        if atom_id == num_atoms:
                            # Since the tail will come only from the template, nothing more is needed.
                            break
            print('Finished looking for dictionary values in file ', data_file)
    # # Write dictionary
    # # TODO: Save dictionary as a JASON file, then use it in processing the data files.
    # For now, just do the check above.
    # with open(cfg[ATOM_TYPE_DICT_FILE], 'w') as d_file:
    #     for line in atom_type_dict.items():
    #         print(line)
    #         # d_file.write('%s,%d' % line + '\n')

    print('Completed making dictionary.')
    return atom_type_dict


def process_data_files(cfg, data_tpl_content):
    atoms_pat = re.compile(r"^Atoms.*")
    num_atoms_pat = re.compile(r"(\d+).*atoms$")
    # Don't want to change the original template data when preparing to print the new file:
    pdb_data_section = copy.deepcopy(data_tpl_content[ATOMS_CONTENT])
    with open(cfg[DATA_FILES]) as f:
        for data_file in f:
            data_file = data_file.strip()
            with open(data_file) as d:
                section = SEC_HEAD
                atom_id = 0
                num_atoms = None

                for line in d:
                    line = line.strip()
                    # not currently keeping anything from the header; just check num atoms
                    if section == SEC_HEAD:
                        if atoms_pat.match(line):
                            section = SEC_ATOMS
                        elif num_atoms is None:
                            atoms_match = num_atoms_pat.match(line)
                            if atoms_match:
                                # regex is 1-based
                                num_atoms = int(atoms_match.group(1))
                                if num_atoms != len(data_tpl_content[ATOMS_CONTENT]):
                                    raise InvalidDataError('The number of atoms listed in the data file {} ({}) does '
                                                           'not equal the number of atoms in the template file ({}).'
                                                           ''.format(num_atoms, len(data_tpl_content[ATOMS_CONTENT]),
                                                                     data_file))

                    # atoms_content to contain only xyz; also perform some checking
                    elif section == SEC_ATOMS:
                        if len(line) == 0:
                            continue
                        split_line = line.split()

                        # Not currently checking molecule number; the number may be wrong and the data still correct,
                        # as PDB numbering starts over at zero a few times (due to restrictions on number of digits in
                        # mol_num) but not the data file
                        # mol_num = int(split_line[1])

                        # TODO: Later, do a check on atom_type based on reading the dictionary.
                        # For now, the checking was in making the dictionary.
                        # atom_type = int(split_line[2])

                        pdb_data_section[atom_id][5:8] = map(float, split_line[4:7])
                        atom_id += 1
                        # Check after increment because the counter started at 0
                        if atom_id == num_atoms:
                            # Since the tail will come only from the template, nothing more is needed.
                            break

            # Now that finished reading the file...
            if atom_id != num_atoms:
                raise InvalidDataError('The number of atoms read from the file {} ({}) does not equal '
                                       'the listed number of atoms ({}).'.format(data_file, atom_id, num_atoms))

            f_name = create_out_fname(data_file, ext='.pdb', base_dir=cfg[OUT_BASE_DIR])
            list_to_file(data_tpl_content[HEAD_CONTENT] + pdb_data_section + data_tpl_content[TAIL_CONTENT],
                         f_name,
                         list_format=cfg[PDB_FORMAT])

            print('Completed writing {}'.format(f_name))
    return


def main(argv=None):
    # Read input
    args, ret = parse_cmdline(argv)
    if ret != GOOD_RET:
        return ret

    cfg = args.config

    # Read template and data files
    try:
        pdb_tpl_content = process_pdb_tpl(cfg)
        # TODO: Test and use dictionary
        if cfg[MAKE_DICT_BOOL]:
            atom_type_dict = make_dict(cfg, pdb_tpl_content)
            print(atom_type_dict)
        process_data_files(cfg, pdb_tpl_content)
    except IOError as e:
        warning("Problems reading file:", e)
        return IO_ERROR
    except InvalidDataError as e:
        warning("Problems reading data template:", e)
        return INVALID_DATA

    return GOOD_RET  # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)
