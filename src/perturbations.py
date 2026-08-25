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


def create_transverse_lesion(
    network: Network,
    z_pos_um: float = 4000.0,
    filter_type: Optional[str] = None,
    filter_latera: Optional[int] = None
) -> Network:
    """
    Creates a structurally lesioned copy of the network by severing connections
    crossing a transverse plane at z_pos_um, matching BergLab's @Network/MakeLesion.m.
    
    A pair (i, j) is severed if one neuron is rostral to z_pos_um and the other is caudal:
      crossing = (z_i < z_pos and z_j > z_pos) or (z_i > z_pos and z_j < z_pos)
      W[crossing] = 0
    """
    lesioned_net = copy.deepcopy(network)
    N = lesioned_net.n_neurons
    pos_z = lesioned_net.pos_z

    filter_mask = np.ones(N, dtype=bool)
    if filter_type is not None:
        filter_mask &= (lesioned_net.types == filter_type)
    if filter_latera is not None:
        filter_mask &= (lesioned_net.latera == filter_latera)

    source = (pos_z < z_pos_um) & filter_mask
    target = (pos_z > z_pos_um) & filter_mask

    # Outer product boolean crossing mask: presynaptic i, postsynaptic j
    crossing = (source[:, None] & target[None, :]) | (target[:, None] & source[None, :])
    lesion_mask = crossing & (lesioned_net.conn_mat != 0.0)

    lesioned_net.conn_mat[lesion_mask] = 0.0
    lesioned_net.sparsity = float(np.count_nonzero(lesioned_net.conn_mat == 0) / lesioned_net.conn_mat.size)
    setattr(lesioned_net, 'lesion_mask', lesion_mask)
    setattr(lesioned_net, 'z_lesion_um', z_pos_um)
    setattr(lesioned_net, 'n_lesioned_synapses', int(np.count_nonzero(lesion_mask)))

    return lesioned_net


def regrow_population_connections(
    lesioned_network: Network,
    target_population: str,
    latera: Optional[int] = None,
    rebalance: bool = False
) -> Network:
    """
    Selectively restores synaptic connections for a specified neuronal population
    across the lesion gap, matching BergLab's @Network/RegrowPop.m.
    
    Restored synaptic weights are set to the mean nonzero absolute weight of the target population:
      W[restore] = mean(|nonzeros(W[:, target])|) * sign(transmitter)
    """
    regrown_net = copy.deepcopy(lesioned_network)
    if not hasattr(regrown_net, 'lesion_mask'):
        raise ValueError("Network does not have a lesion_mask. Call create_transverse_lesion first.")

    lesion_mask = regrown_net.lesion_mask
    pop_mask = (regrown_net.types == target_population)
    
    # Identify connections in lesion mask originating from target_population
    # Note: In connectivity matrix W, W[post, pre] or W[target, source]
    # In BergLab MATLAB: restore = obj.Lesion & (Latera') & (obj.Types == pop)'
    # where presynaptic columns match pop
    restore = lesion_mask & pop_mask[None, :]
    if latera is not None:
        lat_mask = (regrown_net.latera == latera)
        restore = restore & lat_mask[None, :]

    # Calculate mean nonzero weight for the target population
    pop_weights = regrown_net.conn_mat[:, pop_mask]
    nonzero_w = pop_weights[pop_weights != 0.0]
    if len(nonzero_w) > 0:
        mean_weight = float(np.mean(np.abs(nonzero_w)))
    else:
        mean_weight = 0.5 * getattr(regrown_net.parameters, 'gc', 0.5)

    excitatory_pops = {'V2a-2', 'V2a-1', 'V0v', 'V3', 'MN'}
    trans_val = 1.0 if target_population in excitatory_pops else -1.0
    regrown_net.conn_mat[restore] = mean_weight * trans_val
    regrown_net.lesion_mask[restore] = False

    if rebalance:
        from connectivity import balance_connectivity
        regrown_net.conn_mat = balance_connectivity(regrown_net.conn_mat, regrown_net.latera)

    regrown_net.sparsity = float(np.count_nonzero(regrown_net.conn_mat == 0) / regrown_net.conn_mat.size)
    setattr(regrown_net, 'regrown_population', target_population)
    setattr(regrown_net, 'n_restored_synapses', int(np.count_nonzero(restore)))

    return regrown_net


def simulate_lesion_and_regrowth_suite(
    network: Network,
    z_pos_um: float = 4000.0,
    regrowth_populations: Optional[List[str]] = None,
    t_steps: int = 10000,
    I_e: float = 30.0,
    seed: int = 42
) -> Dict[str, Tuple[SimulationResult, Dict[str, Any], Network]]:
    """
    Executes simulations for Control, Transverse Lesion, and Targeted Regrowth conditions.
    """
    if regrowth_populations is None:
        regrowth_populations = ['V2a-2', 'V1', 'V0v', 'V3']

    results = {}

    # 1. Control baseline
    cfg = SimulationConfig(t_steps=t_steps, I_e=I_e, noise_ampl=0.5, seed=seed)
    sim = Simulator(cfg)
    ctrl_res = sim.run(network, verbose=False)
    ctrl_spec = compute_spectral_analysis(ctrl_res.rates, dt=0.001, t_start_ms=2000)
    ctrl_phases = compute_coordination_phases(network, ctrl_res.rates, dt_ms=1.0, t_start_ms=2000)
    results['control'] = (ctrl_res, {
        'condition': 'control',
        'frequency_hz': float(ctrl_spec['dominant_frequency_hz']),
        'rms_amplitude_hz': float(np.mean(np.sqrt(np.mean((ctrl_res.rates[2000:] - np.mean(ctrl_res.rates[2000:], axis=0))**2, axis=0)))),
        'lr_phase_deg': float(ctrl_phases.get('lr_phase_deg', 180.0)),
        'fe_phase_deg': float(ctrl_phases.get('fe_phase_deg', 180.0)),
        'sparsity': network.sparsity
    }, network)

    # 2. Transverse Lesion
    lesioned_net = create_transverse_lesion(network, z_pos_um=z_pos_um)
    lesion_res = sim.run(lesioned_net, verbose=False)
    lesion_spec = compute_spectral_analysis(lesion_res.rates, dt=0.001, t_start_ms=2000)
    lesion_phases = compute_coordination_phases(lesioned_net, lesion_res.rates, dt_ms=1.0, t_start_ms=2000)
    results['lesion'] = (lesion_res, {
        'condition': 'lesion',
        'z_lesion_um': z_pos_um,
        'n_lesioned': lesioned_net.n_lesioned_synapses,
        'frequency_hz': float(lesion_spec['dominant_frequency_hz']),
        'rms_amplitude_hz': float(np.mean(np.sqrt(np.mean((lesion_res.rates[2000:] - np.mean(lesion_res.rates[2000:], axis=0))**2, axis=0)))),
        'lr_phase_deg': float(lesion_phases.get('lr_phase_deg', 0.0)),
        'fe_phase_deg': float(lesion_phases.get('fe_phase_deg', 0.0)),
        'sparsity': lesioned_net.sparsity
    }, lesioned_net)

    # 3. Regrowth conditions
    for pop in regrowth_populations:
        regrown_net = regrow_population_connections(lesioned_net, target_population=pop)
        regrowth_res = sim.run(regrown_net, verbose=False)
        regrowth_spec = compute_spectral_analysis(regrowth_res.rates, dt=0.001, t_start_ms=2000)
        regrowth_phases = compute_coordination_phases(regrown_net, regrowth_res.rates, dt_ms=1.0, t_start_ms=2000)
        cond_name = f"regrowth_{pop}"
        results[cond_name] = (regrowth_res, {
            'condition': cond_name,
            'target_population': pop,
            'n_restored': regrown_net.n_restored_synapses,
            'frequency_hz': float(regrowth_spec['dominant_frequency_hz']),
            'rms_amplitude_hz': float(np.mean(np.sqrt(np.mean((regrowth_res.rates[2000:] - np.mean(regrowth_res.rates[2000:], axis=0))**2, axis=0)))),
            'lr_phase_deg': float(regrowth_phases.get('lr_phase_deg', 180.0)),
            'fe_phase_deg': float(regrowth_phases.get('fe_phase_deg', 180.0)),
            'sparsity': regrown_net.sparsity
        }, regrown_net)

    return results

