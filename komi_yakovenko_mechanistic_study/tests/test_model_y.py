"""
Tests for Model Y (Yakovenko Feedforward Kinematic Reconstruction).
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from model_y import ModelY


def test_model_y_grid_dimensions_and_counts():
    m_y = ModelY(recruitment_mode='graded', n_cycles=2)
    assert m_y.grid.shape == (30, 200)
    assert np.all(m_y.grid >= 0.0)
    assert np.max(m_y.grid) > 100.0


def test_model_y_center_of_activity():
    m_y = ModelY(recruitment_mode='graded', n_cycles=1)
    assert len(m_y.r_cm_level) == 100
    assert len(m_y.r_cm_mm) == 100
    assert len(m_y.velocity_mm_s) == 100
    assert np.all(m_y.r_cm_level >= 0.0)
    assert np.all(m_y.r_cm_level <= 100.0)
    # Verify stance dwell in caudal cord (level > 50)
    stance_mean = np.mean(m_y.r_cm_level[30:90])
    assert stance_mean > 60.0
