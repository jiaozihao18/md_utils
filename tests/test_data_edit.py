import unittest
import os
from md_utils.data_edit import main
from md_utils.md_common import diff_lines, silent_remove, capture_stderr, capture_stdout
import logging

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DISABLE_REMOVE = logger.isEnabledFor(logging.DEBUG)

__author__ = 'hmayes'

# Directories #

TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
SUB_DATA_DIR = os.path.join(DATA_DIR, 'data_edit')

# Input files #

DEF_INI = os.path.join(SUB_DATA_DIR, 'data_reorder.ini')
SERCA_INI = os.path.join(SUB_DATA_DIR, 'data_reorder_serca.ini')
BAD_DICT_INI = os.path.join(SUB_DATA_DIR, 'data_reorder_bad_dict.ini')
BAD_LIST_INI = os.path.join(SUB_DATA_DIR, 'data_bad_list.ini')
GLUP_INI = os.path.join(SUB_DATA_DIR, 'data_reorder_glup_glue.ini')
IMP_ATOMS_BAD_INI = os.path.join(SUB_DATA_DIR, 'data_print_impt_atoms_bad_input.ini')
IMP_ATOMS_TYPO_INI = os.path.join(SUB_DATA_DIR, 'data_print_impt_atoms_key_typo.ini')
GLUE_GLUP_IMP_ATOMS_INI = os.path.join(SUB_DATA_DIR, 'data_print_impt_atoms.ini')
GLUE_GLUP_OWN_ATOMS_INI = os.path.join(SUB_DATA_DIR, 'data_print_own_atoms.ini')
RETYPE_INI = os.path.join(SUB_DATA_DIR, 'data_retype.ini')
BAD_DATA_INI = os.path.join(SUB_DATA_DIR, 'data_reorder_bad_data.ini')
SORT_INI = os.path.join(SUB_DATA_DIR, 'data_sort.ini')
COMPARE_INI = os.path.join(SUB_DATA_DIR, 'data_compare.ini')
COMP_DIH_INI = os.path.join(SUB_DATA_DIR, 'data_compare_dih.ini')
COMP_DIH_ALT_INI = os.path.join(SUB_DATA_DIR, 'data_compare_dih_alt_order.ini')
COMP_FROM_LAMMPS_INI = os.path.join(SUB_DATA_DIR, 'data_compare_from_lammps.ini')
SORT_FROM_LAMMPS_INI = os.path.join(SUB_DATA_DIR, 'data_sort_highlight_from_lammps.ini')


# Output files

# noinspection PyUnresolvedReferences
DEF_OUT = os.path.join(SUB_DATA_DIR, '4.25_new.data')
GOOD_OUT = os.path.join(SUB_DATA_DIR, '4.25_new_good.data')
# noinspection PyUnresolvedReferences
SERCA_0_OUT = os.path.join(SUB_DATA_DIR, 'reus_0_edited_new.data')
SERCA_0_GOOD_OUT = os.path.join(SUB_DATA_DIR, 'reus_0_edited_new_good.data')
# noinspection PyUnresolvedReferences
SERCA_1_OUT = os.path.join(SUB_DATA_DIR, 'reus_1_edited_new.data')
SERCA_1_GOOD_OUT = os.path.join(SUB_DATA_DIR, 'reus_1_edited_new_good.data')
# noinspection PyUnresolvedReferences
GLUP_OUT = os.path.join(SUB_DATA_DIR, 'glup_autopsf_new.data')
GLUP_GOOD_OUT = os.path.join(SUB_DATA_DIR, 'glup_autopsf_new_good.data')
# noinspection PyUnresolvedReferences
GLUE_SELECT_OUT = os.path.join(SUB_DATA_DIR, 'glu_deprot_selected.txt')
GLUE_SELECT_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'glu_deprot_selected_good.txt')
GLUE_SELECT_OWN_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'glu_deprot_selected_owned_good.txt')
# noinspection PyUnresolvedReferences
GLUP_SELECT_OUT = os.path.join(SUB_DATA_DIR, 'glup_autopsf_new_good_selected.txt')
GLUP_SELECT_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'glup_autopsf_new_good_selected_good.txt')
GLUP_SELECT_OWN_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'glup_autopsf_new_good_selected_owned_good.txt')
# noinspection PyUnresolvedReferences
GLUP_RETYPE_OUT = os.path.join(SUB_DATA_DIR, 'glup_autopsf_reordered_to_retype_new.data')
GLUP_RETYPE_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'glup_autopsf_reordered_retyped_good.data')
# noinspection PyUnresolvedReferences
GLUP_SORT_OUT = os.path.join(SUB_DATA_DIR, 'glup_new_new.data')
GLUP_SORT_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'glup_new_sorted.data')
# noinspection PyUnresolvedReferences
COMP_OUT = os.path.join(SUB_DATA_DIR, 'diffs_glup_autopsf_reordered_retyped_good.txt')
COMP1_OUT = os.path.join(SUB_DATA_DIR, 'diffs_glup_to_compare.txt')
COMP1_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'diffs_glup_glue_good.txt')
COMP_DIH_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'diffs_glup_glue_dih_good.txt')
# noinspection PyUnresolvedReferences
COMP_DIH_ALT_OUT = os.path.join(SUB_DATA_DIR, 'diffs_glu_deprot_only_dih.txt')
COMP_DIH_ALT_OUT_GOOD = os.path.join(SUB_DATA_DIR, 'diffs_glup_glue_dih_alt_good.txt')
# noinspection PyUnresolvedReferences
COMP_FROM_LAMMPS = os.path.join(SUB_DATA_DIR, 'diffs_0.875_0_deprot.txt')
COMP_FROM_LAMMPS_GOOD = os.path.join(SUB_DATA_DIR, 'diffs_0.875_0_deprot_good.txt')
# noinspection PyUnresolvedReferences
SORT_FROM_LAMMPS = os.path.join(SUB_DATA_DIR, '0.875_0_deprot_new.data')
SORT_FROM_LAMMPS_GOOD = os.path.join(SUB_DATA_DIR, '0.875_0_deprot_new_good.data')
# noinspection PyUnresolvedReferences
SELECT_FROM_LAMMPS = os.path.join(SUB_DATA_DIR, '0.875_0_deprot_selected.txt')
SELECT_FROM_LAMMPS_GOOD = os.path.join(SUB_DATA_DIR, '0.875_0_deprot_selected_good.txt')


class TestDataEditFailWell(unittest.TestCase):
    def testHelp(self):
        test_input = ['-h']
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertFalse(output)
        with capture_stdout(main, test_input) as output:
            self.assertTrue("optional arguments" in output)

    def testNoArgs(self):
        with capture_stderr(main, []) as output:
            self.assertTrue("Could not read file" in output)
        with capture_stdout(main, []) as output:
            self.assertTrue("optional arguments" in output)

    def testBadIni(self):
        # Accidentally give it a non-config file
        with capture_stderr(main, ["-c", COMP1_OUT_GOOD]) as output:
            self.assertTrue("File contains no section headers" in output)

    def testNoIni(self):
        main(["-c", "ghost.ini"])

    def testBadFileList(self):
        with capture_stderr(main, ["-c", BAD_LIST_INI]) as output:
            self.assertTrue("Did not find a list of data files at the path" in output)

    def testBadDict(self):
        with capture_stderr(main, ["-c", BAD_DICT_INI]) as output:
            self.assertTrue("Expected exactly two comma-separated values" in output)
        silent_remove(DEF_OUT)


class TestDataEdit(unittest.TestCase):
    def testDefIni(self):
        try:
            main(["-c", DEF_INI])
            self.assertFalse(diff_lines(DEF_OUT, GOOD_OUT))
        finally:
            silent_remove(DEF_OUT, disable=DISABLE_REMOVE)

    def testGlupIni(self):
        try:
            main(["-c", GLUP_INI])
            self.assertFalse(diff_lines(GLUP_OUT, GLUP_GOOD_OUT))
        finally:
            silent_remove(GLUP_OUT, disable=DISABLE_REMOVE)

    def testImptAtomsBadInput(self):
        with capture_stderr(main, ["-c", IMP_ATOMS_BAD_INI]) as output:
            self.assertTrue("Problem with config vals on key print_dihedral_types: invalid literal for int()" in output)

    def testImptAtoms(self):
        try:
            main(["-c", GLUE_GLUP_IMP_ATOMS_INI])
            self.assertFalse(diff_lines(GLUE_SELECT_OUT, GLUE_SELECT_OUT_GOOD))
            self.assertFalse(diff_lines(GLUP_SELECT_OUT, GLUP_SELECT_OUT_GOOD))
        finally:
            [silent_remove(o_file, disable=DISABLE_REMOVE) for o_file in [GLUE_SELECT_OUT, GLUP_SELECT_OUT]]

    def testOwnAtoms(self):
        try:
            main(["-c", GLUE_GLUP_OWN_ATOMS_INI])
            self.assertFalse(diff_lines(GLUE_SELECT_OUT, GLUE_SELECT_OWN_OUT_GOOD))
            self.assertFalse(diff_lines(GLUP_SELECT_OUT, GLUP_SELECT_OWN_OUT_GOOD))
        finally:
            [silent_remove(o_file, disable=DISABLE_REMOVE) for o_file in [GLUE_SELECT_OUT, GLUP_SELECT_OUT]]

    def testKeyTypo(self):
        with capture_stderr(main, ["-c", IMP_ATOMS_TYPO_INI]) as output:
            self.assertTrue("Unexpected key 'print_interaction_involving_atoms' in configuration" in output)

    def testBadData(self):
        with capture_stderr(main, ["-c", BAD_DATA_INI]) as output:
            self.assertTrue("Problems reading data" in output)

    def testRetype(self):
        try:
            main(["-c", RETYPE_INI])
            self.assertFalse(diff_lines(GLUP_RETYPE_OUT, GLUP_RETYPE_OUT_GOOD))
        finally:
            silent_remove(GLUP_RETYPE_OUT, disable=DISABLE_REMOVE)

    def testSort(self):
        try:
            main(["-c", SORT_INI])
            self.assertFalse(diff_lines(GLUP_SORT_OUT, GLUP_SORT_OUT_GOOD))
        finally:
            silent_remove(GLUP_SORT_OUT, disable=DISABLE_REMOVE)

    def testCompare(self):
        try:
            main(["-c", COMPARE_INI])
            self.assertFalse(diff_lines(COMP1_OUT, COMP1_OUT_GOOD))
        finally:
            silent_remove(COMP1_OUT, disable=DISABLE_REMOVE)

    def testCompDih(self):
        # Test it is okay with sections in the 2nd but not first file
        with capture_stderr(main, ["-c", COMP_DIH_INI]) as output:
            self.assertTrue("WARNING:  Skipping section" in output)
        try:
            print(COMP_OUT, COMP_DIH_OUT_GOOD)
            self.assertFalse(diff_lines(COMP_OUT, COMP_DIH_OUT_GOOD))
        finally:
            silent_remove(COMP_OUT, disable=DISABLE_REMOVE)

    def testCompDihAlt(self):
        # Test it is okay with sections in the 1st but not 2nd file
        with capture_stderr(main, ["-c", COMP_DIH_ALT_INI]) as output:
            self.assertTrue("WARNING:  Skipping section" in output)
        try:
            self.assertFalse(diff_lines(COMP_DIH_ALT_OUT, COMP_DIH_ALT_OUT_GOOD))
        finally:
            silent_remove(COMP_DIH_ALT_OUT, disable=DISABLE_REMOVE)

    def testDataFromLammps(self):
        try:
            main(["-c", COMP_FROM_LAMMPS_INI])
            self.assertFalse(diff_lines(COMP_FROM_LAMMPS, COMP_FROM_LAMMPS_GOOD))
        finally:
            silent_remove(COMP_FROM_LAMMPS, disable=DISABLE_REMOVE)

    def testSortFromLammps(self):
        try:
            main(["-c", SORT_FROM_LAMMPS_INI])
            self.assertFalse(diff_lines(SORT_FROM_LAMMPS, SORT_FROM_LAMMPS_GOOD))
            self.assertFalse(diff_lines(SELECT_FROM_LAMMPS, SELECT_FROM_LAMMPS_GOOD))
        finally:
            silent_remove(SORT_FROM_LAMMPS, disable=DISABLE_REMOVE)
            silent_remove(SELECT_FROM_LAMMPS, disable=DISABLE_REMOVE)
