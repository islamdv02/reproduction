"""
Tests for Figures 1 through 8 plotting pipeline in the mechanistic study.
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
from controls_suite import ControlsSuite
import figure_plotting as fp


def test_all_figures_pipeline(tmp_path):
    out_dir = str(tmp_path)

    m_y = ModelY()
    p1 = fp.plot_fig1_yakovenko_reference(m_y, output_dir=out_dir)
    assert os.path.exists(p1)

    m_ky = ModelKY(n_neurons=300, rng_seed=42, duration_ms=600.0, warmup_ms=100.0)
    p2 = fp.plot_fig2_komi_yakovenko_network(m_ky, output_dir=out_dir)
    assert os.path.exists(p2)

    p3 = fp.plot_fig3_activity_comparison(m_y, m_ky, output_dir=out_dir)
    assert os.path.exists(p3)

    p4 = fp.plot_fig4_center_of_activity_comparison(m_y, m_ky, output_dir=out_dir)
    assert os.path.exists(p4)

    decomp = WaveDecomposer(m_y, m_ky)
    p5 = fp.plot_fig5_wave_comparison(decomp, output_dir=out_dir)
    assert os.path.exists(p5)

    p6 = fp.plot_fig6_connectivity_projectome(m_ky, output_dir=out_dir)
    assert os.path.exists(p6)

    controls_runner = ControlsSuite(rng_seed=42)
    controls_res = controls_runner.run_all_8_controls()
    p7 = fp.plot_fig7_controls(controls_res, output_dir=out_dir)
    assert os.path.exists(p7)

    p8 = fp.plot_fig8_mechanistic_summary(output_dir=out_dir)
    assert os.path.exists(p8)
