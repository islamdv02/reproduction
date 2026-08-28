"""
Tests for Figures 1 through 8 plotting pipeline.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from phase_analysis import PhaseUnfolder
from projectome_analysis import ProjectomeAnalyzer
from traveling_wave import TravelingWaveAnalyzer
from gain_modulation import DecoupledGainController
from controls import ControlsAndSensitivityRunner
import figure_generators as fg


def test_all_figure_generation_pipeline(tmp_path):
    out_dir = str(tmp_path)

    net = YakovenkoKomiSpatialNetwork(n_neurons=200, rng_seed=42)
    p1 = fg.plot_fig1_spatial_mapping(net, output_dir=out_dir)
    assert os.path.exists(p1)

    conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=42)
    p2 = fg.plot_fig2_connectome_balancing(conn, output_dir=out_dir)
    assert os.path.exists(p2)

    dyn = RecurrentRateDynamics(conn, rng_seed=42)
    times, rates, _ = dyn.simulate(duration_ms=600.0, warmup_ms=100.0)
    pu = PhaseUnfolder(rates, times)
    p3 = fg.plot_fig3_dynamics_and_pca(rates, times, pu, output_dir=out_dir)
    assert os.path.exists(p3)

    wave = TravelingWaveAnalyzer(net, rates, times)
    p4 = fg.plot_fig4_traveling_waves_bilateral(wave, output_dir=out_dir)
    assert os.path.exists(p4)

    proj = ProjectomeAnalyzer(conn)
    p5 = fg.plot_fig5_net_projectome_mexican_hat(proj, output_dir=out_dir)
    assert os.path.exists(p5)

    gain_ctrl = DecoupledGainController(net)
    p6 = fg.plot_fig6_decoupled_gain_control(gain_ctrl, output_dir=out_dir)
    assert os.path.exists(p6)

    controls_runner = ControlsAndSensitivityRunner(rng_seed=42)
    controls_res = controls_runner.run_control_experiments()
    p7 = fg.plot_fig7_controls_and_sensitivity(controls_res, output_dir=out_dir)
    assert os.path.exists(p7)

    p8 = fg.plot_fig8_cross_paper_comparison(output_dir=out_dir)
    assert os.path.exists(p8)
