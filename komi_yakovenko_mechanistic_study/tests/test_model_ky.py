"""
Tests for Model K-Y (Komi Recurrent Balanced Projectome Model on Cat Anatomy).
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from model_ky import ModelKY


def test_model_ky_simulation_and_grid():
    m_ky = ModelKY(n_neurons=400, rng_seed=42, duration_ms=1000.0, warmup_ms=200.0)
    assert m_ky.rates.shape[0] == 400
    assert m_ky.grid.shape[0] == 30
    assert len(m_ky.r_cm_level) == len(m_ky.times_ms)
    assert np.all(m_ky.r_cm_level >= 0.0)
    assert np.all(m_ky.r_cm_level <= 100.0)


def test_model_ky_dynamics_metrics():
    m_ky = ModelKY(n_neurons=400, rng_seed=42, duration_ms=1000.0, warmup_ms=200.0)
    assert m_ky.phase_unfolder.planar_variance > 0.0
    assert m_ky.wave.velocity_mm_s > 0.0
    assert 0.0 <= m_ky.projectome.mexican_hat_index <= 1.0
