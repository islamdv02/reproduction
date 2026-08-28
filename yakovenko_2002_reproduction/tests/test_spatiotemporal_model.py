"""
Comprehensive unit tests for spatiotemporal model in Yakovenko et al. (2002).
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from anatomy import CatLumbosacralAnatomy
from emg_profiles import CatHindlimbEMG
from spatiotemporal_model import SpatiotemporalModel


def test_model_activity_integration():
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG()
    model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded', n_cycles=2)

    assert model.activity_grid.shape == (30, 200)
    assert np.all(model.activity_grid >= 0.0)
    assert np.max(model.activity_grid) > 100.0


def test_center_of_mass_velocity_consistency():
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG()
    model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded', n_cycles=1)

    assert len(model.velocity_mm_s) == 100
    assert not np.any(np.isnan(model.velocity_mm_s))
    assert not np.any(np.isinf(model.velocity_mm_s))
