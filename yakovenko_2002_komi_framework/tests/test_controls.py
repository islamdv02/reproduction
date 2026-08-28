"""
Tests for Controls A, B, C, D and parameter sensitivity sweeps.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from controls import ControlsAndSensitivityRunner


def test_control_experiments():
    runner = ControlsAndSensitivityRunner(rng_seed=42)
    res = runner.run_control_experiments()

    assert 'Control_A_Main' in res
    assert 'Control_B_Shuffled' in res
    assert 'Control_C_Unstructured' in res
    assert 'Control_D_Unbalanced' in res

    for c_name, c_dict in res.items():
        assert 'planar_variance' in c_dict
        assert 'mexican_hat_index' in c_dict
        assert 'wave_velocity_mm_s' in c_dict
