"""
Gait Control and Descending Drive Module for Spinal Projectome.
Reproduces Figure 4 of Komi et al., Nature Communications, 2026:
- LPGi glutamatergic drive injection
- Raphe serotonergic (5-HT) gain modulation
- Speed regulation and gait transitions (Walk, Trot, Bound)
- Descending drive parameter sweeps and phase statistics
"""

import numpy as np
import pandas as pd
from scipy import signal
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Union, Any

from network import Network
from simulation import SimulationConfig, SimulationResult, Simulator
from dynamics import (
    tanh_activation,
    euler_step_voltage,
    euler_step_adaptation,
    compute_spectral_analysis
)
from locomotion import (
    compute_pca_dynamics,
    compute_population_phases,
    generate_synthetic_emg
)


@dataclass
class DescendingDriveConfig:
    """
    Configuration for descending brainstem drive and neuromodulation.
    """
    # LPGi Glutamatergic Drive
    I_lpgi_base: float = 30.0          # Base excitatory drive current (pA)
    I_lpgi_ramp_start: float = 15.0     # Starting current for acceleration ramp (pA)
    I_lpgi_ramp_end: float = 50.0       # Ending current for acceleration ramp (pA)
    lpgi_targets: List[str] = field(default_factory=lambda: ['V2a-1', 'V2a-2', 'V0v', 'V3', 'MN'])
    
    # 5-HT Serotonergic Neuromodulatory Gain
    serotonin_gain_multiplier: float = 1.0   # Multiplier alpha for 5-HT7/2a expressing populations
    serotonin_targets: List[str] = field(default_factory=lambda: ['V2a-1', 'V2a-2', 'V1', 'V2b', 'V3'])
    
    # General Simulation Settings
    t_steps: int = 10000
    dt_ms: float = 1.0
    tau_V_ms: float = 50.0
    noise_ampl: float = 0.5
    seed: int = 42


def compute_coordination_phases(
    network: Network,
    rates: np.ndarray,
    dt_ms: float = 1.0,
    t_start_ms: int = 1000
) -> Dict[str, Any]:
    """
    Computes Left-Right (L-R) and Rostrocaudal / Flexor-Extensor (L2-L5) phase relationships
    using cross-correlation across steady-state neural activity.
    """
    start_idx = min(t_start_ms, rates.shape[0] // 2)
    rates_ss = rates[start_idx:, :]

    # 1. Left vs Right hemicord motor/population rates
    left_mask = (network.latera < 0)
    right_mask = (network.latera > 0)

    mn_mask = (network.types == 'MN')
    if np.any(mn_mask & left_mask) and np.any(mn_mask & right_mask):
        left_rate = np.mean(rates_ss[:, mn_mask & left_mask], axis=1)
        right_rate = np.mean(rates_ss[:, mn_mask & right_mask], axis=1)
    else:
        left_rate = np.mean(rates_ss[:, left_mask], axis=1)
        right_rate = np.mean(rates_ss[:, right_mask], axis=1)

    left_centered = left_rate - np.mean(left_rate)
    right_centered = right_rate - np.mean(right_rate)

    # Estimate cycle period from autocorrelation of left rate
    autocorr = signal.correlate(left_centered, left_centered, mode='full')
    lags = signal.correlation_lags(len(left_centered), len(left_centered))
    pos_lags = lags[lags > 0]
    pos_autocorr = autocorr[lags > 0]
    peaks, _ = signal.find_peaks(pos_autocorr, distance=max(int(100 / dt_ms), 10))
    if len(peaks) > 0:
        period_ms = float(pos_lags[peaks[0]] * dt_ms)
    else:
        period_ms = 500.0

    # Cross-correlation between Left and Right
    xcorr_lr = signal.correlate(left_centered, right_centered, mode='full')
    xlags_lr = signal.correlation_lags(len(left_centered), len(right_centered))
    valid_mask_lr = np.abs(xlags_lr * dt_ms) <= period_ms
    if np.any(valid_mask_lr):
        best_lag_lr = xlags_lr[valid_mask_lr][np.argmax(xcorr_lr[valid_mask_lr])]
        lr_phase_rad = float(np.mod(2.0 * np.pi * (best_lag_lr * dt_ms) / period_ms, 2.0 * np.pi))
    else:
        lr_phase_rad = np.pi

    # 2. Rostral (Flexor-dominant) vs Caudal (Extensor-dominant) phase
    z_mid = np.median(network.pos_z)
    rostral_mask = (network.pos_z < z_mid)
    caudal_mask = (network.pos_z >= z_mid)

    if np.any(rostral_mask):
        rostral_rate = np.mean(rates_ss[:, rostral_mask], axis=1)
    else:
        rostral_rate = np.zeros(rates_ss.shape[0], dtype=np.float64)

    if np.any(caudal_mask):
        caudal_rate = np.mean(rates_ss[:, caudal_mask], axis=1)
    else:
        caudal_rate = np.zeros(rates_ss.shape[0], dtype=np.float64)

    rostral_centered = rostral_rate - np.mean(rostral_rate)
    caudal_centered = caudal_rate - np.mean(caudal_rate)

    xcorr_fe = signal.correlate(rostral_centered, caudal_centered, mode='full')
    xlags_fe = signal.correlation_lags(len(rostral_centered), len(caudal_centered))
    valid_mask_fe = np.abs(xlags_fe * dt_ms) <= period_ms
    if np.any(valid_mask_fe):
        best_lag_fe = xlags_fe[valid_mask_fe][np.argmax(xcorr_fe[valid_mask_fe])]
        fe_phase_rad = float(np.mod(2.0 * np.pi * (best_lag_fe * dt_ms) / period_ms, 2.0 * np.pi))
    else:
        fe_phase_rad = np.pi

    return {
        'cycle_period_ms': period_ms,
        'delta_phi_lr': lr_phase_rad,
        'delta_phi_l2_l5': fe_phase_rad,
        'lr_phase_deg': float(np.degrees(lr_phase_rad)),
        'fe_phase_deg': float(np.degrees(fe_phase_rad))
    }


def classify_gait(
    frequency_hz: float,
    lr_phase_rad: float,
    fe_phase_rad: float = np.pi
) -> str:
    """
    Classifies locomotive state into canonical gait categories based on
    oscillation frequency and left-right / flexor-extensor phase relationships.

    Definitions from Komi et al. 2026:
      - Walk: Lower frequency (< 3.0 Hz) + Antiphase Left-Right (~pi rad = 180 deg)
      - Trot: Moderate/high frequency (3.0 - 5.5 Hz) + Antiphase Left-Right (~pi rad)
      - Bound: High frequency (> 5.5 Hz) + Synchronous Left-Right (~0 rad = 0 deg)
      - Transition: Intermediate phase / boundary state
    """
    # Normalize phase to [-pi, pi]
    lr_norm = (lr_phase_rad + np.pi) % (2 * np.pi) - np.pi
    lr_deg = np.degrees(np.abs(lr_norm))

    is_alternating = (lr_deg >= 120.0)
    is_synchronous = (lr_deg <= 60.0)

    if is_synchronous and frequency_hz >= 4.5:
        return "Bound"
    elif is_alternating and frequency_hz < 3.0:
        return "Walk"
    elif is_alternating and frequency_hz >= 3.0:
        return "Trot"
    else:
        return "Transition"


def simulate_gait_regime(
    network: Network,
    gait_name: str = "trot",
    t_steps: int = 10000,
    seed: int = 42
) -> Tuple[SimulationResult, Dict[str, Any]]:
    """
    Runs a full projectome simulation for a specific physiological gait regime:
      - 'walk': I_e = 20 pA, 5-HT gain = 1.0x (Slow left-right alternation)
      - 'trot': I_e = 30 pA, 5-HT gain = 1.0x (Fast left-right alternation)
      - 'bound': I_e = 45 pA, 5-HT gain = 1.75x (Left-right synchronous bounding)
    """
    gait_lower = gait_name.lower()
    if gait_lower == "walk":
        I_e = 20.0
        serotonin_mult = 1.0
    elif gait_lower == "trot":
        I_e = 30.0
        serotonin_mult = 1.0
    elif gait_lower == "bound":
        I_e = 45.0
        serotonin_mult = 1.75
    else:
        I_e = 30.0
        serotonin_mult = 1.0

    # Build per-neuron gain vector incorporating 5-HT modulation
    gains = np.array([network.parameters.celltypes[t].gain for t in network.types], dtype=np.float64)
    thresholds = np.array([network.parameters.celltypes[t].threshold for t in network.types], dtype=np.float64)
    f_maxs = np.array([network.parameters.celltypes[t].f_max for t in network.types], dtype=np.float64)

    if serotonin_mult != 1.0:
        ht_targets = ['V2a-1', 'V2a-2', 'V1', 'V2b', 'V3']
        for pop in ht_targets:
            mask = (network.types == pop)
            gains[mask] *= serotonin_mult

    rng = np.random.default_rng(seed)
    N = network.n_neurons
    W = network.conn_mat
    tau_V = 50.0
    dt = 1.0

    R = np.zeros((t_steps, N), dtype=np.float64)
    V = np.zeros((t_steps, N), dtype=np.float64)
    V[0, :] = rng.normal(-70.0, 3.0, size=N)
    I_noise = rng.normal(0.0, 0.5, size=(t_steps, N))

    for t in range(1, t_steps):
        i_rec = W @ R[t - 1, :]
        i_tot = i_rec + I_noise[t - 1, :] + I_e
        V[t, :] = euler_step_voltage(V[t - 1, :], i_tot, tau_V, dt=dt)
        R[t, :] = tanh_activation(V[t, :], thresholds, gains, f_maxs)

    pop_rates = {}
    for pop_name in network.parameters.celltypes.keys():
        pop_mask = (network.types == pop_name)
        if np.any(pop_mask):
            pop_rates[pop_name] = np.mean(R[:, pop_mask], axis=1)

    time_vector = np.arange(t_steps) * dt
    spec_analysis = compute_spectral_analysis(R, dt=dt * 0.001, t_start_ms=1000)

    cfg = SimulationConfig(
        t_steps=t_steps,
        dt_ms=dt,
        tau_V_ms=tau_V,
        I_e=I_e,
        noise_ampl=0.5,
        seed=seed
    )

    sim_res = SimulationResult(
        config=cfg,
        time_ms=time_vector,
        rates=R,
        voltage=V,
        population_rates=pop_rates,
        spectral_analysis=spec_analysis,
        final_voltage=V[-1, :],
        final_rates=R[-1, :],
        n_neurons=N
    )

    # Compute gait phases and metrics
    phases = compute_coordination_phases(network, R, dt_ms=dt, t_start_ms=1000)
    freq_hz = float(spec_analysis.get('dominant_frequency_hz', 0.0))
    lr_phase_rad = float(phases.get('delta_phi_lr', np.pi))
    fe_phase_rad = float(phases.get('delta_phi_l2_l5', np.pi))
    detected_gait = classify_gait(freq_hz, lr_phase_rad, fe_phase_rad)

    # Calculate overall RMS amplitude
    ss_rates = R[1000:, :]
    rms_amplitude = float(np.mean(np.sqrt(np.mean((ss_rates - np.mean(ss_rates, axis=0)) ** 2, axis=0))))

    metrics = {
        'gait_requested': gait_name,
        'gait_detected': detected_gait,
        'I_e': I_e,
        'serotonin_mult': serotonin_mult,
        'frequency_hz': freq_hz,
        'rms_amplitude_hz': rms_amplitude,
        'lr_phase_rad': lr_phase_rad,
        'lr_phase_deg': float(np.degrees(lr_phase_rad)),
        'fe_phase_rad': fe_phase_rad,
        'fe_phase_deg': float(np.degrees(fe_phase_rad)),
        'phases': phases
    }

    return sim_res, metrics


def simulate_descending_ramp(
    network: Network,
    I_start: float = 15.0,
    I_end: float = 50.0,
    t_steps: int = 10000,
    seed: int = 42
) -> Tuple[SimulationResult, np.ndarray]:
    """
    Simulates network dynamics under a continuously accelerating descending drive ramp:
      I_e(t) = I_start + (I_end - I_start) * (t / t_steps)
    """
    rng = np.random.default_rng(seed)
    N = network.n_neurons
    W = network.conn_mat
    tau_V = 50.0
    dt = 1.0

    thresholds = np.array([network.parameters.celltypes[t].threshold for t in network.types], dtype=np.float64)
    gains = np.array([network.parameters.celltypes[t].gain for t in network.types], dtype=np.float64)
    f_maxs = np.array([network.parameters.celltypes[t].f_max for t in network.types], dtype=np.float64)

    # Time-varying current ramp
    t_vec = np.arange(t_steps)
    I_ramp = I_start + (I_end - I_start) * (t_vec / float(t_steps))

    R = np.zeros((t_steps, N), dtype=np.float64)
    V = np.zeros((t_steps, N), dtype=np.float64)
    V[0, :] = rng.normal(-70.0, 3.0, size=N)
    I_noise = rng.normal(0.0, 0.5, size=(t_steps, N))

    for t in range(1, t_steps):
        i_rec = W @ R[t - 1, :]
        i_tot = i_rec + I_noise[t - 1, :] + I_ramp[t - 1]
        V[t, :] = euler_step_voltage(V[t - 1, :], i_tot, tau_V, dt=dt)
        R[t, :] = tanh_activation(V[t, :], thresholds, gains, f_maxs)

    pop_rates = {}
    for pop_name in network.parameters.celltypes.keys():
        pop_mask = (network.types == pop_name)
        if np.any(pop_mask):
            pop_rates[pop_name] = np.mean(R[:, pop_mask], axis=1)

    time_vector = np.arange(t_steps) * dt
    spec_analysis = compute_spectral_analysis(R, dt=dt * 0.001, t_start_ms=1000)

    cfg = SimulationConfig(
        t_steps=t_steps,
        dt_ms=dt,
        tau_V_ms=tau_V,
        I_e=float(np.mean(I_ramp)),
        noise_ampl=0.5,
        seed=seed
    )

    sim_res = SimulationResult(
        config=cfg,
        time_ms=time_vector,
        rates=R,
        voltage=V,
        population_rates=pop_rates,
        spectral_analysis=spec_analysis,
        final_voltage=V[-1, :],
        final_rates=R[-1, :],
        n_neurons=N
    )

    return sim_res, I_ramp


def run_descending_drive_sweep(
    network: Network,
    drive_levels: Optional[np.ndarray] = None,
    t_steps: int = 4000,
    seed: int = 42
) -> pd.DataFrame:
    """
    Performs a quantitative parameter sweep across descending drive levels (I_e in pA)
    evaluating frequency, amplitude, and left-right / flexor-extensor phase relationships.
    """
    if drive_levels is None:
        drive_levels = np.linspace(15.0, 50.0, 10)

    records = []
    for I_e in drive_levels:
        # Determine appropriate 5-HT gain multiplier across the drive ramp
        # High drive (> 40 pA) activates higher 5-HT neuromodulation
        if I_e >= 42.0:
            serotonin_mult = 1.75
        elif I_e >= 35.0:
            serotonin_mult = 1.3
        else:
            serotonin_mult = 1.0

        gains = np.array([network.parameters.celltypes[t].gain for t in network.types], dtype=np.float64)
        thresholds = np.array([network.parameters.celltypes[t].threshold for t in network.types], dtype=np.float64)
        f_maxs = np.array([network.parameters.celltypes[t].f_max for t in network.types], dtype=np.float64)

        if serotonin_mult != 1.0:
            for pop in ['V2a-1', 'V2a-2', 'V1', 'V2b', 'V3']:
                mask = (network.types == pop)
                gains[mask] *= serotonin_mult

        rng = np.random.default_rng(seed)
        N = network.n_neurons
        W = network.conn_mat
        tau_V = 50.0
        dt = 1.0

        R = np.zeros((t_steps, N), dtype=np.float64)
        V = np.zeros((t_steps, N), dtype=np.float64)
        V[0, :] = rng.normal(-70.0, 3.0, size=N)
        I_noise = rng.normal(0.0, 0.5, size=(t_steps, N))

        for t in range(1, t_steps):
            i_rec = W @ R[t - 1, :]
            i_tot = i_rec + I_noise[t - 1, :] + I_e
            V[t, :] = euler_step_voltage(V[t - 1, :], i_tot, tau_V, dt=dt)
            R[t, :] = tanh_activation(V[t, :], thresholds, gains, f_maxs)

        spec = compute_spectral_analysis(R, dt=dt * 0.001, t_start_ms=1000)
        phases = compute_coordination_phases(network, R, dt_ms=dt, t_start_ms=1000)

        freq_hz = float(spec.get('dominant_frequency_hz', 0.0))
        lr_phase = float(phases.get('delta_phi_lr', np.pi))
        fe_phase = float(phases.get('delta_phi_l2_l5', np.pi))
        
        ss_rates = R[1000:, :]
        rms_amp = float(np.mean(np.sqrt(np.mean((ss_rates - np.mean(ss_rates, axis=0)) ** 2, axis=0))))
        peak_amp = float(np.percentile(ss_rates, 99))
        gait_name = classify_gait(freq_hz, lr_phase, fe_phase)

        records.append({
            'I_e': I_e,
            'serotonin_multiplier': serotonin_mult,
            'frequency_hz': freq_hz,
            'rms_amplitude_hz': rms_amp,
            'peak_amplitude_hz': peak_amp,
            'lr_phase_rad': lr_phase,
            'lr_phase_deg': float(np.degrees(lr_phase)),
            'fe_phase_rad': fe_phase,
            'fe_phase_deg': float(np.degrees(fe_phase)),
            'gait_state': gait_name
        })

    return pd.DataFrame(records)
