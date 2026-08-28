"""
Tests for 8 Controlled Experiments in ControlsSuite.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from controls_suite import ControlsSuite


def test_all_8_controls():
    runner = ControlsSuite(rng_seed=42)
    res = runner.run_all_8_controls()

    assert len(res) == 9 # Baseline + 8 Controls
    assert 'Baseline_Model_KY' in res
    assert 'Ctrl_1_No_Spatial_Structure' in res
    assert 'Ctrl_2_Shuffled_Coordinates' in res
    assert 'Ctrl_3_Random_Wiring' in res
    assert 'Ctrl_4_Zero_Directional_Bias' in res
    assert 'Ctrl_5_Unbalanced_EI' in res
    assert 'Ctrl_6_Isotropic_Kernels' in res
    assert 'Ctrl_7_No_Commissural' in res
    assert 'Ctrl_8_Feedforward_Model_Y' in res
