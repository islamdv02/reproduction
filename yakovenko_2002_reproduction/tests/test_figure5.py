"""
Unit tests for Figure 5 of Yakovenko et al. (2002).
Verifies 4 recruitment sensitivity modes (5A, 5B, 5C, 5D), center-of-mass metrics, and velocities.
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
from figure5_analysis import generate_figure5_complete, export_figure5_trajectories_csv


def test_four_recruitment_modes_execution():
    """Verify all four parametric recruitment modes compute valid activity grids and trajectories."""
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)

    modes = ['graded', 'step', 'phys_40_15', 'inv_15_40']
    for mode in modes:
        model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode=mode, n_cycles=2)
        assert model.activity_grid.shape == (30, 200)
        assert len(model.r_cm_level) == 200
        assert len(model.velocity_mm_s) == 200
        assert np.all(model.r_cm_level >= 0.0)
        assert np.all(model.r_cm_level <= 100.0)


def test_center_of_mass_displacement_and_range():
    """
    Verify center of mass displacement covers ~38-42 levels (~10.9-12.0 mm),
    representing ~50% of the maximum possible range of 21.5 mm.
    """
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded', n_cycles=1)

    assert 35.0 <= model.displacement_levels <= 45.0, f"Displacement levels {model.displacement_levels} outside expected range ~38"
    assert 10.0 <= model.displacement_mm <= 13.0, f"Displacement mm {model.displacement_mm} outside expected range ~10.9 mm"

    # Percentage of maximal range (21.5 mm)
    pct_range = (model.displacement_mm / 21.5) * 100
    assert 45.0 <= pct_range <= 60.0, f"Percentage of range {pct_range}% outside expected ~51%"


def test_migration_velocities_at_transitions():
    """
    Verify peak migration velocities reach high values at phase transitions
    (swing-to-stance ~200-400 mm/s and retraction-to-swing ~300-500 mm/s).
    """
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    model = SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded', n_cycles=1)

    assert model.peak_velocity_swing_stance >= 150.0
    assert model.peak_velocity_retract_swing >= 250.0


def test_figure5_plot_and_csv_export(tmp_path):
    """Verify Figure 5 composite plot and trajectory CSV export succeed."""
    out_dir = str(tmp_path)
    plot_path = generate_figure5_complete(output_dir=out_dir)
    assert os.path.exists(plot_path)
    assert os.path.getsize(plot_path) > 10000

    csv_path = os.path.join(out_dir, "trajectories.csv")
    anat = CatLumbosacralAnatomy()
    emg = CatHindlimbEMG(fdl_as_retractor=True)
    models = {
        '5A': SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='graded'),
        '5B': SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='step'),
        '5C': SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='phys_40_15'),
        '5D': SpatiotemporalModel(anatomy=anat, emg=emg, recruitment_mode='inv_15_40'),
    }
    df = export_figure5_trajectories_csv(models, csv_path)
    assert os.path.exists(csv_path)
    assert len(df) == 100
