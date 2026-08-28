"""
Comprehensive unit tests for anatomy module in Yakovenko et al. (2002).
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from anatomy import CatLumbosacralAnatomy, MUSCLE_NAMES, MUSCLE_CATEGORIES, JOINT_GROUPS


def test_anatomy_basic_parameters():
    anat = CatLumbosacralAnatomy()
    assert anat.length_mm == 28.8
    assert anat.n_slices == 30
    assert anat.slice_matrix.shape == (27, 30)


def test_table1_counts_consistency():
    anat = CatLumbosacralAnatomy()
    t1 = anat.get_table1_counts(fdl_as_retractor=True)
    assert t1['all']['total'] == 4034
    assert t1['extensor']['total'] == 2366
    assert t1['retractor']['total'] == 907
    assert t1['flexor']['total'] == 761


def test_centers_of_mass_presence():
    anat = CatLumbosacralAnatomy()
    for m in MUSCLE_NAMES:
        assert m in anat.centers_of_mass_level
        assert m in anat.centers_of_mass_mm
        assert 0.0 <= anat.centers_of_mass_level[m] <= 100.0
        assert 0.0 <= anat.centers_of_mass_mm[m] <= 28.8
