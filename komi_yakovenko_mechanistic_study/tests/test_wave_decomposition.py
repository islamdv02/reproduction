"""
Tests for Wave Decomposition (Wave A, Wave B, Wave C).
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from model_y import ModelY
from model_ky import ModelKY
from wave_decomposition import WaveDecomposer


def test_wave_decomposition_metrics():
    m_y = ModelY()
    m_ky = ModelKY(n_neurons=400, rng_seed=42, duration_ms=1000.0, warmup_ms=200.0)
    decomp = WaveDecomposer(m_y, m_ky)

    assert decomp.wave_a_displacement_mm > 5.0
    assert 0.5 <= decomp.wave_b_caudal_stance_fraction <= 0.9
    assert decomp.wave_c_propagation_velocity > 0.0

    summary = decomp.get_summary_dict()
    assert 'Wave_A_Activity_Migration' in summary
    assert 'Wave_B_Stance_Swing_Shift' in summary
    assert 'Wave_C_Emergent_Traveling_Wave' in summary
