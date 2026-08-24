"""
Spinal Projectome Simulation Engine
Orchestrates network simulation runs, parameter configuration,
and result extraction for baseline locomotion.
Faithfully reproduces Komi et al., Nature Communications, 2026.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import json
import os

from network import Network
from dynamics import (
    tanh_activation,
    euler_step_voltage,
    euler_step_adaptation,
    compute_spectral_analysis
)


@dataclass
class SimulationConfig:
    """
    Simulation hyper-parameters and initial conditions.
    """
    t_steps: int = 10000
    dt_ms: float = 1.0
    tau_V_ms: float = 50.0
    I_e: float = 30.0
    noise_ampl: float = 0.5
    V_init_mean: float = -70.0
    V_init_std: float = 3.0
    seed: int = 5
    adaptation: bool = False
    Ca: float = 1.25
    tau_a_adapting_ms: float = 3000.0
    tau_a_nonadapting_ms: float = 10000.0

    def to_dict(self) -> Dict[str, Union[int, float, bool]]:
        return {
            't_steps': self.t_steps,
            'dt_ms': self.dt_ms,
            'tau_V_ms': self.tau_V_ms,
            'I_e': self.I_e,
            'noise_ampl': self.noise_ampl,
            'V_init_mean': self.V_init_mean,
            'V_init_std': self.V_init_std,
            'seed': self.seed,
            'adaptation': self.adaptation,
            'Ca': self.Ca,
            'tau_a_adapting_ms': self.tau_a_adapting_ms,
            'tau_a_nonadapting_ms': self.tau_a_nonadapting_ms
        }


@dataclass
class SimulationResult:
    """
    Container for simulation outputs, time courses, and spectral metrics.
    """
    config: SimulationConfig
    time_ms: np.ndarray
    rates: np.ndarray                    # Shape: (t_steps, N)
    voltage: np.ndarray                  # Shape: (t_steps, N)
    population_rates: Dict[str, np.ndarray]  # Type -> (t_steps,)
    spectral_analysis: Dict[str, Union[float, np.ndarray]]
    final_voltage: np.ndarray            # Shape: (N,)
    final_rates: np.ndarray              # Shape: (N,)
    n_neurons: int = 0

    def save_checkpoint(self, output_dir: str, prefix: str = "baseline_simulation"):
        """Saves simulation parameters, metrics, and state summaries to disk."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save metadata / config / metrics
        meta = {
            'n_neurons': self.n_neurons,
            'config': self.config.to_dict(),
            'dominant_frequency_hz': self.spectral_analysis.get('dominant_frequency_hz', 0.0),
            'peak_power': self.spectral_analysis.get('peak_power', 0.0),
            'amplitude_hz': self.spectral_analysis.get('amplitude_hz', 0.0),
            'mean_rate_hz': self.spectral_analysis.get('mean_rate_hz', 0.0),
            'std_rate_hz': self.spectral_analysis.get('std_rate_hz', 0.0),
        }
        with open(os.path.join(output_dir, f"{prefix}_metadata.json"), 'w') as f:
            json.dump(meta, f, indent=2)

        # Save numpy trajectories fast
        np.savez(
            os.path.join(output_dir, f"{prefix}_results.npz"),
            time_ms=self.time_ms,
            rates=self.rates,
            voltage=self.voltage,
            final_voltage=self.final_voltage,
            final_rates=self.final_rates
        )


class Simulator:
    """
    Simulation executor for spinal neural projectome networks.
    """
    def __init__(self, config: Optional[SimulationConfig] = None):
        if config is None:
            config = SimulationConfig()
        self.config = config

    def run(self, network: Network, verbose: bool = True) -> SimulationResult:
        """
        Executes Forward Euler simulation on the provided network instance.
        """
        cfg = self.config
        rng = np.random.default_rng(cfg.seed)
        
        N = network.n_neurons
        W = network.conn_mat
        t_steps = cfg.t_steps

        # Extract cell-type specific properties for all neurons
        thresholds = np.array([network.parameters.celltypes[t].threshold for t in network.types])
        gains = np.array([network.parameters.celltypes[t].gain for t in network.types])
        f_maxs = np.array([network.parameters.celltypes[t].f_max for t in network.types])

        # Pre-allocate trajectory buffers
        R = np.zeros((t_steps, N), dtype=np.float64)
        V = np.zeros((t_steps, N), dtype=np.float64)
        a = np.zeros((t_steps, N), dtype=np.float64)

        # Initial conditions matching Simulate.m
        V[0, :] = rng.normal(cfg.V_init_mean, cfg.V_init_std, size=N)
        R[0, :] = 0.0

        # Pre-allocate additive Gaussian noise
        I_noise = rng.normal(0.0, cfg.noise_ampl, size=(t_steps, N))
        I_e_val = cfg.I_e
        tau_V = cfg.tau_V_ms
        dt = cfg.dt_ms

        # Adaptation time constants if enabled
        tau_a = np.full(N, cfg.tau_a_nonadapting_ms, dtype=np.float64)

        # Time-stepping integration loop
        for t in range(1, t_steps):
            # 1. Recurrent synaptic current: I_rec = W * R(t-1)
            i_rec = W @ R[t - 1, :]

            # 2. Total current: I_tot = I_rec + I_noise + I_e
            i_tot = i_rec + I_noise[t - 1, :] + I_e_val

            # 3. Leaky integrator voltage update
            V[t, :] = euler_step_voltage(V[t - 1, :], i_tot, tau_V, dt=dt)

            # 4. Optional spike-frequency adaptation update
            if cfg.adaptation:
                a[t, :] = euler_step_adaptation(a[t - 1, :], R[t - 1, :], ca=cfg.Ca, tau_a=tau_a, dt=dt)

            # 5. Firing rate activation
            V_eff = V[t, :] - a[t, :]
            R[t, :] = tanh_activation(V_eff, thresholds, gains, f_maxs)

        # Extract population-averaged rates
        pop_rates = {}
        for pop_name in network.parameters.celltypes.keys():
            pop_mask = (network.types == pop_name)
            if np.any(pop_mask):
                pop_rates[pop_name] = np.mean(R[:, pop_mask], axis=1)

        # Spectral analysis of global network activity
        time_vector = np.arange(t_steps) * dt
        spec_analysis = compute_spectral_analysis(R, dt=dt * 0.001, t_start_ms=1000)

        result = SimulationResult(
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

        return result
