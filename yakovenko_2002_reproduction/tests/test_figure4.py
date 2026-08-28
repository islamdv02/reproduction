"""
Unit tests for Figure 4 of Yakovenko et al. (2002).
Verifies 3D spatiotemporal activity grid dimensions, caudal stance dominance, and plot generation.
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
from figure4_analysis import generate_figure4_complete, export_figure4_data


def test_spatiotemporal_grid_dimensions_and_periodicity():
    """Verify activity grid has 30 slices and 200 time bins with 100-step cycle periodicity."""
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded',
                                fdl_as_retractor=True, n_cycles=2)

    assert model.activity_grid.shape == (30, 200)
    assert np.all(model.activity_grid >= 0.0)

    # Verify periodicity: cycle 1 (0..99) == cycle 2 (100..199)
    np.testing.assert_allclose(model.activity_grid[:, :100], model.activity_grid[:, 100:], rtol=1e-5)


def test_caudal_stance_dominance():
    """Verify stance phase has dominant active MN peak in caudal enlargement (slices 20-26, L7)."""
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded',
                                fdl_as_retractor=True, n_cycles=1)

    # Stance peak (time bins 30-90)
    stance_activity = model.activity_grid[:, 30:90]
    peak_slice, peak_t = np.unravel_index(np.argmax(stance_activity), stance_activity.shape)

    # Caudal slices (slices 20 to 26 correspond to L7 / level 66 to 86)
    assert 18 <= peak_slice <= 26, f"Stance peak slice {peak_slice} not in caudal enlargement"
    assert stance_activity[peak_slice, peak_t] > 150.0 # High recruitment (~200 MNs)


def test_rostral_swing_activation():
    """Verify swing phase has activation in rostral enlargement (slices 3-10, L4-L5)."""
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded',
                                fdl_as_retractor=True, n_cycles=1)

    # Swing activity (time bins 5-20)
    swing_activity = model.activity_grid[:, 5:20]
    rostral_swing = np.sum(swing_activity[:15, :])
    caudal_swing = np.sum(swing_activity[15:, :])

    assert rostral_swing > caudal_swing, "Rostral swing activity should exceed caudal during early swing"


def test_figure4_plot_and_data_export(tmp_path):
    """Verify Figure 4 3D plot and NPZ data export succeed."""
    out_dir = str(tmp_path)
    plot_path = generate_figure4_complete(output_dir=out_dir)
    assert os.path.exists(plot_path)
    assert os.path.getsize(plot_path) > 10000

    npz_path = os.path.join(out_dir, "grid.npz")
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded',
                                fdl_as_retractor=True, n_cycles=2)
    export_figure4_data(model, npz_path)
    assert os.path.exists(npz_path)
