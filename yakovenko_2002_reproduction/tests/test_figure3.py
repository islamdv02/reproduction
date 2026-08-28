"""
Unit tests for Figure 3 of Yakovenko et al. (2002).
Verifies 27 muscle EMG profiles, normalization to 100%, 30% swing duration, and profile shapes.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from emg_profiles import build_all_emg_profiles, CatHindlimbEMG
from figure3_analysis import generate_figure3_complete


def test_emg_profiles_count_and_length():
    """Verify all 27 muscles have profiles with 100 time points."""
    emg_ret = build_all_emg_profiles(fdl_as_retractor=True)
    assert len(emg_ret) == 27
    for m, p in emg_ret.items():
        assert len(p) == 100
        assert np.min(p) >= 0.0
        assert np.max(p) <= 100.0
        assert np.max(p) == pytest.approx(100.0, abs=1e-1) # Normalization


def test_flexor_vs_extensor_timing_separation():
    """Verify flexors are active in swing (0-30%) and extensors are active in stance (30-100%)."""
    emg = CatHindlimbEMG(fdl_as_retractor=True)

    # TA (Tibialis anterior - Flexor)
    ta_swing = np.mean([emg.get_emg('TA', t) for t in range(0, 30)])
    ta_stance = np.mean([emg.get_emg('TA', t) for t in range(35, 95)])
    assert ta_swing > 40.0
    assert ta_stance < 5.0

    # Soleus (Extensor)
    sol_swing = np.mean([emg.get_emg('Soleus', t) for t in range(0, 20)])
    sol_stance = np.mean([emg.get_emg('Soleus', t) for t in range(30, 90)])
    assert sol_swing < 5.0
    assert sol_stance > 50.0


def test_retractor_biphasic_and_stance_swing_burst():
    """Verify retractors (BFp, ST, Gracilis) have intense burst around stance-swing transition (85-100% / 0-10%)."""
    emg = CatHindlimbEMG(fdl_as_retractor=True)

    for m in ['BFp', 'ST', 'Gracilis', 'SMp']:
        burst_val = np.max([emg.get_emg(m, t) for t in [90, 92, 95, 98, 0, 2]])
        assert burst_val >= 80.0, f"Retractor {m} does not burst at stance-swing transition"


def test_fdl_dual_profile_modes():
    """Verify FDL retractor mode differs from FDL extensor mode."""
    p_ret = build_all_emg_profiles(fdl_as_retractor=True)
    p_ext = build_all_emg_profiles(fdl_as_retractor=False)

    # In retractor mode, FDL peaks at stance-swing transition (~95%)
    assert p_ret['FDL'][95] > 80.0
    assert p_ret['FDL'][50] < 5.0

    # In extensor mode, FDL is active during mid-stance (~55%)
    assert p_ext['FDL'][55] > 80.0


def test_figure3_plot_generation(tmp_path):
    """Verify composite Figure 3 plot generates successfully."""
    out_dir = str(tmp_path)
    plot_path = generate_figure3_complete(output_dir=out_dir)
    assert os.path.exists(plot_path)
    assert os.path.getsize(plot_path) > 10000
