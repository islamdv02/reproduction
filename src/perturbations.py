"""
Spinal Network Perturbation and Lesion Module.
Implements genetic ablation and functional silencing experiments matching
Figure 5 of Komi et al., Nature Communications, 2026:
- V1 inhibitory interneuron manipulation (rostral inhibitory lobe removal)
- V0 commissural interneuron manipulation (contralateral projectome removal)
- Structural genetic ablation (synaptic weight matrix zeroing)
- Functional silencing (hyperpolarizing current injection)
"""

import copy
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Union

from network import Network
from simulation import SimulationConfig, Simulator, SimulationResult
from dynamics import compute_spectral_analysis
from gait_control import compute_coordination_phases, classify_gait
from locomotion import generate_synthetic_emg


def create_ablated_network(
    network: Network,
    target_populations: List[str]
) -> Network:
    """
    Creates a structurally ablated copy of the network matching MATLAB @Network/MakeLesion.m.
    Zeroes all presynaptic and postsynaptic connections for the specified cell types:
      W[:, target] = 0 and W[target, :] = 0
    """
    ablated_net = copy.deepcopy(network)
    target_mask = np.isin(ablated_net.types, target_populations)

    # Zero all synaptic connections to and from the target population
    ablated_net.conn_mat[:, target_mask] = 0.0
    ablated_net.conn_mat[target_mask, :] = 0.0

    # Update sparsity metric
    ablated_net.sparsity = float(np.count_nonzero(ablated_net.conn_mat == 0) / ablated_net.conn_mat.size)
    setattr(ablated_net, 'ablated_populations', list(target_populations))
    setattr(ablated_net, 'target_mask', target_mask)

    return ablated_net


def simulate_silencing(
    network: Network,
    target_populations: List[str],
    I_hyper: float = -30.0,
    I_e_base: float = 30.0,
    t_steps: int = 10000,
    seed: int = 42
) -> SimulationResult:
    """
    Simulates functional optogenetic/pharmacogenetic silencing by injecting
    a hyperpolarizing bias current into the target cell populations.
    """
    target_mask = np.isin(network.types, target_populations)
    N = network.n_neurons

    # Build custom per-neuron external drive vector
    I_ext = np.full(N, I_e_base, dtype=np.float64)
    I_ext[target_mask] += I_hyper

    cfg = SimulationConfig(
        t_steps=t_steps,
        dt_ms=1.0,
        I_e=I_e_base,
        noise_ampl=0.5,
        seed=seed
    )

    rng = np.random.default_rng(seed)
    V = np.zeros((t_steps, N), dtype=np.float64)
    R = np.zeros((t_steps, N), dtype=np.float64)
    V[0, :] = rng.normal(cfg.V_init_mean, cfg.V_init_std, size=N)
    I_noise = rng.normal(0.0, cfg.noise_ampl, size=(t_steps, N))

    thresholds = np.asarray([network.parameters.celltypes[t].threshold for t in network.types], dtype=np.float64)
    gains = np.asarray([network.parameters.celltypes[t].gain for t in network.types], dtype=np.float64)
    f_maxs = np.asarray([network.parameters.celltypes[t].f_max for t in network.types], dtype=np.float64)

    W = network.conn_mat
    tau_V = cfg.tau_V_ms
    dt = cfg.dt_ms

    from dynamics import tanh_activation, euler_step_voltage

    for t in range(1, t_steps):
        i_rec = W @ R[t - 1, :]
        i_tot = i_rec + I_noise[t - 1, :] + I_ext
        V[t, :] = euler_step_voltage(V[t - 1, :], i_tot, tau_V, dt=dt)
        R[t, :] = tanh_activation(V[t, :], thresholds, gains, f_maxs)

    time_ms = np.arange(t_steps, dtype=np.float64) * dt
    pop_rates = {}
    for pop in np.unique(network.types):
        p_mask = (network.types == pop)
        pop_rates[str(pop)] = np.mean(R[:, p_mask], axis=1)

    spec = compute_spectral_analysis(R, dt=dt/1000.0, t_start_ms=min(1000, t_steps//2))

    return SimulationResult(
        config=cfg,
        time_ms=time_ms,
        rates=R,
        voltage=V,
        population_rates=pop_rates,
        spectral_analysis=spec,
        final_voltage=V[-1, :],
        final_rates=R[-1, :],
        n_neurons=N
    )


def simulate_perturbation_condition(
    network: Network,
    condition: str = "control",
    perturbation_mode: str = "ablation",
    t_steps: int = 10000,
    I_e: float = 30.0,
    seed: int = 42
) -> Tuple[SimulationResult, Dict[str, Any], Network]:
    """
    Executes a single perturbation condition (control, v1, v0).
    Returns (SimulationResult, metrics_dict, active_network).
    """
    if condition == "control":
        active_net = network
        cfg = SimulationConfig(t_steps=t_steps, I_e=I_e, noise_ampl=0.5, seed=seed)
        sim = Simulator(cfg)
        sim_res = sim.run(active_net, verbose=False)
        target_pops = []
    elif condition == "v1":
        target_pops = ['V1']
        if perturbation_mode == "ablation":
            active_net = create_ablated_network(network, target_pops)
            cfg = SimulationConfig(t_steps=t_steps, I_e=I_e, noise_ampl=0.5, seed=seed)
            sim = Simulator(cfg)
            sim_res = sim.run(active_net, verbose=False)
        else:
            active_net = network
            sim_res = simulate_silencing(network, target_pops, I_hyper=-30.0, I_e_base=I_e, t_steps=t_steps, seed=seed)
    elif condition == "v0":
        target_pops = ['V0v', 'V0d']
        if perturbation_mode == "ablation":
            active_net = create_ablated_network(network, target_pops)
            cfg = SimulationConfig(t_steps=t_steps, I_e=I_e, noise_ampl=0.5, seed=seed)
            sim = Simulator(cfg)
            sim_res = sim.run(active_net, verbose=False)
        else:
            active_net = network
            sim_res = simulate_silencing(network, target_pops, I_hyper=-30.0, I_e_base=I_e, t_steps=t_steps, seed=seed)
    else:
        raise ValueError(f"Unknown perturbation condition: {condition}")

    # Compute spectral and phase metrics
    spec = compute_spectral_analysis(sim_res.rates, dt=0.001, t_start_ms=2000)
    freq_hz = float(spec['dominant_frequency_hz'])

    # Compute burst RMS amplitude
    steady_rates = sim_res.rates[2000:, :]
    mean_rates = np.mean(steady_rates, axis=0)
    rms_amplitude = float(np.mean(np.sqrt(np.mean((steady_rates - mean_rates) ** 2, axis=0))))

    # Compute coordination phases
    phases = compute_coordination_phases(
        network=active_net,
        rates=sim_res.rates,
        dt_ms=1.0,
        t_start_ms=2000
    )

    lr_phase_rad = float(phases.get('lr_phase_rad', phases.get('delta_phi_lr', np.pi)))
    fe_phase_rad = float(phases.get('fe_phase_rad', phases.get('delta_phi_l2_l5', np.pi)))
    lr_phase_deg = float(phases.get('lr_phase_deg', np.degrees(lr_phase_rad)))
    fe_phase_deg = float(phases.get('fe_phase_deg', np.degrees(fe_phase_rad)))

    detected_gait = classify_gait(freq_hz, lr_phase_rad, fe_phase_rad)

    metrics = {
        'condition': condition,
        'mode': perturbation_mode,
        'target_populations': target_pops,
        'frequency_hz': freq_hz,
        'rms_amplitude_hz': rms_amplitude,
        'lr_phase_rad': lr_phase_rad,
        'lr_phase_deg': lr_phase_deg,
        'fe_phase_rad': fe_phase_rad,
        'fe_phase_deg': fe_phase_deg,
        'gait_detected': detected_gait,
        'I_e': I_e,
        'sparsity': active_net.sparsity
    }

    return sim_res, metrics, active_net


def run_figure5_perturbation_suite(
    network: Network,
    perturbation_mode: str = "ablation",
    t_steps: int = 10000,
    seed: int = 42
) -> Dict[str, Tuple[SimulationResult, Dict[str, Any], Network]]:
    """
    Runs the complete set of Figure 5 perturbation experiments:
    1. Control baseline
    2. V1 perturbation
    3. V0 perturbation
    """
    suite_results = {}
    for cond in ['control', 'v1', 'v0']:
        res, metrics, net_active = simulate_perturbation_condition(
            network=network,
            condition=cond,
            perturbation_mode=perturbation_mode,
            t_steps=t_steps,
            I_e=30.0,
            seed=seed
        )
        suite_results[cond] = (res, metrics, net_active)

    return suite_results
