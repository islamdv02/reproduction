"""
Figure 1 Computational Models: Non-Spatial Balanced Sequence Generator (BSG)
and 1D 5-Subpopulation Mexican-Hat Network.

Grounded in Komi et al. (Nature Communications, 2026) and BergLab MATLAB codebase:
- 00_SpinalNetworkModel/@Network/ComputeEigenModesandNullSpace.m
- 02_HelperFunctions/BalanceConnectivity.m
- 02_HelperFunctions/ComputeFiringPhaseSorting.m
- 02_HelperFunctions/RescaleConnectivity.m
- @Network/Simulate.m
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List
import numpy as np
from scipy.signal import find_peaks
from sklearn.decomposition import PCA


@dataclass
class BSGConfig:
    """Configuration for Balanced Sequence Generator (BSG) random recurrent network."""
    n_neurons: int = 500
    p_conn: float = 0.1
    prop_excitatory: float = 0.5
    weight_mean: float = 1.0
    weight_std: float = 0.1
    tau_e_ms: float = 50.0
    tau_i_ms: float = 20.0
    I_e: float = 30.0
    noise_ampl: float = 0.5
    dt_ms: float = 1.0
    t_steps: int = 10000
    rng_seed: int = 42


def balance_bsg_connectivity(
    conn_mat: np.ndarray,
    neuron_types: np.ndarray
) -> np.ndarray:
    """
    Row-wise zero-sum synaptic balancing matching BalanceConnectivity.m:
      For each neuron row i:
        S_i = sum_j W_{ij}
        S_i^+ = sum_{j, W>0} W_{ij}
        S_i^- = sum_{j, W<0} W_{ij}
        f_i^+ = (S_i^+ - S_i / 2) / S_i^+
        f_i^- = (S_i^- - S_i / 2) / S_i^-
        W_{ij} <- W_{ij} * f_i^+ (if W > 0)
        W_{ij} <- W_{ij} * f_i^- (if W < 0)
      Guarantees sum_j W_{ij} == 0.0 exactly for every neuron.
    """
    W = conn_mat.copy()
    N = W.shape[0]

    for i in range(N):
        row = W[i, :]
        pos_mask = row > 0
        neg_mask = row < 0

        sum_pos = np.sum(row[pos_mask])
        sum_neg = np.sum(row[neg_mask])
        total_sum = sum_pos + sum_neg

        if sum_pos > 0 and sum_neg < 0:
            f_pos = (sum_pos - total_sum / 2.0) / sum_pos
            f_neg = (sum_neg - total_sum / 2.0) / sum_neg
            W[i, pos_mask] *= f_pos
            W[i, neg_mask] *= f_neg
        elif sum_pos > 0 and sum_neg == 0:
            # Shift all positive weights down
            W[i, pos_mask] -= total_sum / np.sum(pos_mask)
        elif sum_neg < 0 and sum_pos == 0:
            W[i, neg_mask] -= total_sum / np.sum(neg_mask)

    return W


class BSGNetwork:
    """
    Non-spatial Balanced Sequence Generator (BSG) random recurrent network.
    Generates multi-phase sequential rhythms through finite-size fluctuations.
    """

    def __init__(self, config: Optional[BSGConfig] = None):
        self.config = config or BSGConfig()
        self.n_neurons = self.config.n_neurons
        self.rng = np.random.default_rng(self.config.rng_seed)

        n_e = int(self.n_neurons * self.config.prop_excitatory)
        n_i = self.n_neurons - n_e
        self.is_excitatory = np.array([True] * n_e + [False] * n_i)
        self.transmitter = np.where(self.is_excitatory, 1.0, -1.0)

        self.conn_mat = self._build_balanced_connectivity()
        self.tau_v = np.where(self.is_excitatory, self.config.tau_e_ms, self.config.tau_i_ms)

    def _build_balanced_connectivity(self) -> np.ndarray:
        cfg = self.config
        N = self.n_neurons

        # Flat Erdős–Rényi random adjacency (p = 0.1), no autapses
        adj = (self.rng.random((N, N)) < cfg.p_conn).astype(np.float64)
        np.fill_diagonal(adj, 0.0)

        # Gaussian weights with Dale's law
        weights = self.rng.normal(cfg.weight_mean, cfg.weight_std, size=(N, N))
        weights = np.clip(weights, 0.01, None)
        W = adj * weights * self.transmitter[None, :]

        # Row-wise zero-sum balancing: sum_j W_{ij} == 0
        W_balanced = balance_bsg_connectivity(W, self.transmitter)

        # Rescale connectivity
        n_pos = np.count_nonzero(W_balanced > 0)
        n_neg = np.count_nonzero(W_balanced < 0)
        n_zeros = np.count_nonzero(W_balanced == 0)
        r = n_pos / max(1, n_neg)
        S = n_zeros / (N * N)
        norm_factor = np.sqrt(S * (1.0 - S) * (1.0 + r**2) / 2.0) * np.sqrt(N)
        if norm_factor > 0:
            W_balanced = (W_balanced / norm_factor) * 1.5

        return W_balanced

    def simulate(
        self,
        t_steps: Optional[int] = None,
        dt_ms: Optional[float] = None,
        I_e: Optional[float] = None,
        seed: Optional[int] = None
    ) -> Dict[str, np.ndarray]:
        """
        Simulates rate-based membrane dynamics using Forward Euler integration:
          tau_i dx_i/dt = -x_i + sum_j W_{ij} F(x_j) + I_e + epsilon_i(t)
        """
        cfg = self.config
        steps = t_steps or cfg.t_steps
        dt = dt_ms or cfg.dt_ms
        drive = I_e if I_e is not None else cfg.I_e
        sim_rng = np.random.default_rng(seed if seed is not None else cfg.rng_seed)

        N = self.n_neurons
        V = sim_rng.normal(-70.0, 3.0, size=N)
        V_history = np.zeros((steps, N), dtype=np.float64)
        R_history = np.zeros((steps, N), dtype=np.float64)

        # Compound tanh activation function matching Methods p. 10
        T_thresh = 5.0
        gain = 1.0
        f_max = 50.0

        for t in range(steps):
            # Compound tanh
            below = (V <= T_thresh)
            above = ~below
            R = np.zeros(N, dtype=np.float64)
            if np.any(below):
                R[below] = T_thresh * np.tanh(gain * (V[below] - T_thresh) / T_thresh) + T_thresh
            if np.any(above):
                R[above] = f_max * np.tanh(gain * (V[above] - T_thresh) / f_max) + T_thresh
            R = np.clip(R, 0.0, None)

            # Synaptic current
            I_syn = self.conn_mat @ R
            noise = sim_rng.normal(0.0, cfg.noise_ampl, size=N)

            # Euler step
            dV = (-V + I_syn + drive + noise) * (dt / self.tau_v)
            V += dV

            V_history[t, :] = V
            R_history[t, :] = R

        time_ms = np.arange(steps) * dt
        return {
            'time_ms': time_ms,
            'voltages': V_history,
            'rates': R_history
        }


def compute_phase_unfolding(
    rates: np.ndarray,
    conn_mat: np.ndarray,
    dt_ms: float = 1.0,
    t_start_ms: int = 2000
) -> Dict[str, Any]:
    """
    Phase-space unfolding algorithm matching ComputeFiringPhaseSorting.m:
    1. Extracts 1st principal component s_1(t) from steady-state rates.
    2. Cross-correlates each neuron's activity R_i(t) against s_1(t) to find peak lag L_i.
    3. Estimates dominant cycle period T_cycle from autocorrelation.
    4. Computes circular phase coordinate theta_i = (L_i * 2pi / T_cycle) mod 2pi.
    5. Sorts neurons and permutes connectivity matrix W_unfolded = W_{Pi, Pi}.
    6. Bins connection weight as a function of phase distance Delta theta.
    """
    start_idx = int(t_start_ms / dt_ms)
    steady_rates = rates[start_idx:, :]
    T, N = steady_rates.shape

    # Center rates for PCA
    centered_rates = steady_rates - np.mean(steady_rates, axis=0)

    pca = PCA(n_components=2)
    scores = pca.fit_transform(centered_rates)
    s1 = scores[:, 0]

    # Find cycle period from autocorrelation of PC1
    autocorr = np.correlate(s1, s1, mode='full')
    center = len(autocorr) // 2
    pos_autocorr = autocorr[center:]
    peaks, _ = find_peaks(pos_autocorr, distance=int(100 / dt_ms))

    if len(peaks) > 1:
        cycle_period_ms = float(np.mean(np.diff(peaks)) * dt_ms)
    else:
        cycle_period_ms = 400.0

    # Cross-correlate each neuron with PC1 to find peak phase lag
    phase_lags_ms = np.zeros(N)
    for i in range(N):
        sig = centered_rates[:, i]
        if np.std(sig) > 1e-6:
            xcorr = np.correlate(s1, sig, mode='full')
            lag_idx = np.argmax(xcorr)
            phase_lags_ms[i] = (lag_idx - (T - 1)) * dt_ms

    # Circular phase coordinate theta_i in [0, 2pi)
    theta = (phase_lags_ms * 2.0 * np.pi / cycle_period_ms) % (2.0 * np.pi)
    sort_order = np.argsort(theta)
    sorted_theta = theta[sort_order]

    # Permuted unfolded connectivity matrix
    W_unfolded = conn_mat[np.ix_(sort_order, sort_order)]

    # Compute 1D projectome curve as a function of delta theta in [-pi, pi]
    n_bins = 60
    delta_theta_bins = np.linspace(-np.pi, np.pi, n_bins)
    projectome_profile = np.zeros(n_bins - 1)
    projectome_excit = np.zeros(n_bins - 1)
    projectome_inhib = np.zeros(n_bins - 1)
    bin_centers = 0.5 * (delta_theta_bins[:-1] + delta_theta_bins[1:])

    # Pairwise circular phase difference matrix
    d_theta = sorted_theta[:, None] - sorted_theta[None, :]
    # Wrap to [-pi, pi]
    d_theta = (d_theta + np.pi) % (2.0 * np.pi) - np.pi

    for b in range(n_bins - 1):
        mask = (d_theta >= delta_theta_bins[b]) & (d_theta < delta_theta_bins[b + 1])
        if np.any(mask):
            w_vals = W_unfolded[mask]
            projectome_profile[b] = np.mean(w_vals)
            projectome_excit[b] = np.mean(np.clip(w_vals, 0.0, None))
            projectome_inhib[b] = np.mean(np.clip(w_vals, None, 0.0))

    return {
        'pca_scores': scores,
        'explained_variance_ratio': pca.explained_variance_ratio_,
        'cycle_period_ms': cycle_period_ms,
        'theta': theta,
        'sort_order': sort_order,
        'sorted_theta': sorted_theta,
        'W_unfolded': W_unfolded,
        'delta_theta_centers': bin_centers,
        'projectome_profile': projectome_profile,
        'projectome_excit': projectome_excit,
        'projectome_inhib': projectome_inhib
    }


@dataclass
class SubpopulationConfig:
    """1D Subpopulation spatial projection kernel parameters."""
    name: str
    is_excitatory: bool
    mu_um: float
    sigma_um: float
    gain: float = 1.0


class MexicanHat1DNetwork:
    """
    1D 5-subpopulation spatial network with asymmetric Mexican-hat projectome.
    Demonstrates independent gain control of locomotor amplitude (sp3) and frequency (sp2).
    """

    def __init__(
        self,
        n_neurons: int = 500,
        length_um: float = 5000.0,
        pop_configs: Optional[List[SubpopulationConfig]] = None,
        rng_seed: int = 42
    ):
        self.n_neurons = n_neurons
        self.length_um = length_um
        self.rng = np.random.default_rng(rng_seed)

        # 5 canonical subpopulations matching Methods p. 11 and Fig. 1F
        self.pop_configs = pop_configs or [
            SubpopulationConfig(name='sp1', is_excitatory=True, mu_um=200.0, sigma_um=150.0, gain=1.0),
            SubpopulationConfig(name='sp2', is_excitatory=False, mu_um=600.0, sigma_um=250.0, gain=1.0),
            SubpopulationConfig(name='sp3', is_excitatory=True, mu_um=1200.0, sigma_um=350.0, gain=1.0),
            SubpopulationConfig(name='sp4', is_excitatory=False, mu_um=2000.0, sigma_um=450.0, gain=1.0),
            SubpopulationConfig(name='sp5', is_excitatory=True, mu_um=3000.0, sigma_um=600.0, gain=1.0)
        ]

        self.n_pops = len(self.pop_configs)
        self.pos_z = np.linspace(0.0, self.length_um, self.n_neurons)
        self.neuron_pops = np.array([self.pop_configs[i % self.n_pops].name for i in range(self.n_neurons)])
        self.is_excitatory = np.array([self.pop_configs[i % self.n_pops].is_excitatory for i in range(self.n_neurons)])
        self.transmitter = np.where(self.is_excitatory, 1.0, -1.0)

        self.conn_mat = self._build_1d_mexican_hat_connectivity()
        self.tau_v = np.full(self.n_neurons, 50.0)

    def _build_1d_mexican_hat_connectivity(self) -> np.ndarray:
        N = self.n_neurons
        W = np.zeros((N, N), dtype=np.float64)

        # Periodic distance on 1D ring to ensure boundary-invariant traveling waves
        L = self.length_um
        dz_raw = self.pos_z[:, None] - self.pos_z[None, :]
        # Wrap distance to [-L/2, L/2]
        dz = (dz_raw + L / 2.0) % L - L / 2.0

        for p_idx, pop in enumerate(self.pop_configs):
            src_mask = (self.neuron_pops == pop.name)
            if not np.any(src_mask):
                continue

            # Gaussian spatial projection kernel
            mu = pop.mu_um
            sigma = pop.sigma_um
            p_prob = np.exp(-((dz[:, src_mask] - mu)**2) / (2.0 * sigma**2))

            # Sample binary adjacency
            adj = (self.rng.random(p_prob.shape) < 0.25 * p_prob).astype(np.float64)
            weights = self.rng.normal(1.0, 0.1, size=p_prob.shape)
            weights = np.clip(weights, 0.05, None)

            sign = 1.0 if pop.is_excitatory else -1.0
            W[:, src_mask] = adj * weights * sign

        np.fill_diagonal(W, 0.0)

        # Row-wise zero-sum balancing: sum_j W_{ij} == 0
        W_balanced = balance_bsg_connectivity(W, self.transmitter)

        # Rescale matrix
        n_pos = np.count_nonzero(W_balanced > 0)
        n_neg = np.count_nonzero(W_balanced < 0)
        n_zeros = np.count_nonzero(W_balanced == 0)
        r = n_pos / max(1, n_neg)
        S = n_zeros / (N * N)
        norm_factor = np.sqrt(S * (1.0 - S) * (1.0 + r**2) / 2.0) * np.sqrt(N)
        if norm_factor > 0:
            W_balanced = (W_balanced / norm_factor) * 2.2

        return W_balanced

    def simulate(
        self,
        t_steps: int = 10000,
        dt_ms: float = 1.0,
        I_e: float = 30.0,
        pop_gains: Optional[Dict[str, float]] = None,
        seed: int = 42
    ) -> Dict[str, np.ndarray]:
        """
        Simulates 1D network rate dynamics with optional population-specific gains:
          F_i(x) = Compound_Tanh(g_{pop(i)} * x)
        """
        sim_rng = np.random.default_rng(seed)
        N = self.n_neurons
        V = sim_rng.normal(-70.0, 3.0, size=N)
        V_history = np.zeros((t_steps, N), dtype=np.float64)
        R_history = np.zeros((t_steps, N), dtype=np.float64)

        # Setup per-neuron gain array
        gains = np.ones(N, dtype=np.float64)
        if pop_gains:
            for p_name, g_val in pop_gains.items():
                mask = (self.neuron_pops == p_name)
                gains[mask] = g_val

        T_thresh = 5.0
        f_max = 50.0

        for t in range(t_steps):
            below = (V <= T_thresh)
            above = ~below
            R = np.zeros(N, dtype=np.float64)
            if np.any(below):
                R[below] = T_thresh * np.tanh(gains[below] * (V[below] - T_thresh) / T_thresh) + T_thresh
            if np.any(above):
                R[above] = f_max * np.tanh(gains[above] * (V[above] - T_thresh) / f_max) + T_thresh
            R = np.clip(R, 0.0, None)

            I_syn = self.conn_mat @ R
            noise = sim_rng.normal(0.0, 0.5, size=N)

            dV = (-V + I_syn + I_e + noise) * (dt_ms / self.tau_v)
            V += dV

            V_history[t, :] = V
            R_history[t, :] = R

        time_ms = np.arange(t_steps) * dt_ms
        return {
            'time_ms': time_ms,
            'voltages': V_history,
            'rates': R_history
        }


def simulate_gain_modulation_sweep(
    network_1d: MexicanHat1DNetwork,
    target_population: str,
    gain_levels: List[float],
    t_steps: int = 6000,
    dt_ms: float = 1.0,
    I_e: float = 30.0,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Sweeps the gain of target_population (e.g. sp2 or sp3) and quantifies:
      - Dominant frequency (Hz)
      - RMS burst amplitude (Hz)
      - 2D PCA trajectory and mean orbit radius R_orbit
    """
    frequencies = []
    amplitudes = []
    orbit_radii = []
    sim_runs = {}

    for g in gain_levels:
        gains = {target_population: g}
        res = network_1d.simulate(t_steps=t_steps, dt_ms=dt_ms, I_e=I_e, pop_gains=gains, seed=seed)

        # Steady-state window (discard initial transient, keep last 60% or after 2000ms)
        cutoff_ms = min(2000.0, 0.4 * (t_steps * dt_ms))
        t_steady = (res['time_ms'] >= cutoff_ms)
        rates_s = res['rates'][t_steady, :]

        # 1. Amplitude (mean RMS across neurons)
        rms_val = float(np.mean(np.std(rates_s, axis=0)))
        amplitudes.append(rms_val)

        # 2. PCA and Orbit Radius
        centered = rates_s - np.mean(rates_s, axis=0)
        pca = PCA(n_components=2)
        scores = pca.fit_transform(centered)
        r_orbit = float(np.mean(np.sqrt(scores[:, 0]**2 + scores[:, 1]**2)))
        orbit_radii.append(r_orbit)

        # 3. Frequency from autocorrelation of PC1
        s1 = scores[:, 0]
        autocorr = np.correlate(s1, s1, mode='full')
        center = len(autocorr) // 2
        pos_ac = autocorr[center:]
        peaks, _ = find_peaks(pos_ac, distance=max(5, int(50 / dt_ms)))
        if len(peaks) > 1:
            period_ms = float(np.mean(np.diff(peaks)) * dt_ms)
            freq_hz = 1000.0 / period_ms
        else:
            freq_hz = 2.5
        frequencies.append(freq_hz)

        sample_len = min(1000, len(rates_s))
        sim_runs[f"gain_{g:.2f}"] = {
            'gain': g,
            'frequency_hz': freq_hz,
            'amplitude_hz': rms_val,
            'orbit_radius': r_orbit,
            'pca_scores': scores,
            'sample_rates': rates_s[:sample_len, :10]
        }

    return {
        'target_population': target_population,
        'gain_levels': gain_levels,
        'frequencies_hz': frequencies,
        'amplitudes_hz': amplitudes,
        'orbit_radii': orbit_radii,
        'sim_runs': sim_runs
    }
