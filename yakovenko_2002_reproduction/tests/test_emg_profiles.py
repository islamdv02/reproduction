"""
Comprehensive unit tests for EMG profiles module in Yakovenko et al. (2002).
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from emg_profiles import CatHindlimbEMG, build_all_emg_profiles


def test_emg_initialization():
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    assert len(emg.muscle_names) == 27
    assert emg.emg_matrix.shape == (27, 100)


def test_emg_get_function():
    emg = CatHindlimbEMG()
    for m in emg.muscle_names:
        v0 = emg.get_emg(m, 0.0)
        v50 = emg.get_emg(m, 50.0)
        assert 0.0 <= v0 <= 100.0
        assert 0.0 <= v50 <= 100.0
