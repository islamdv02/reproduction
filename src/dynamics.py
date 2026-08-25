"""
Neural Dynamics and Rate Activation Module for Spinal Projectome.
Implements the core dynamical equations from Komi et al., Nature Communications, 2026:
- Non-linear compound hyperbolic tangent activation function: R = f(V - a)
- Euler voltage integration with membrane time constant tau_V
- Spike frequency adaptation with slow recovery tau_a
- High-resolution power spectral density and dominant frequency analysis
"""

import numpy as np
from scipy import signal
from typing import Dict, Union, Tuple, Optional, Any


def tanh_activation(
    v: Union[float, np.ndarray],
    threshold: Union[float, np.ndarray] = 20.0,
    gain: Union[float, np.ndarray] = 1.0,
    f_max: Union[float, np.ndarray] = 50.0
) -> Union[float, np.ndarray]:
    """
    Computes compound hyperbolic tangent non-linear rate activation.
    Matches MATLAB @Network/Simulate.m lines 77-84:
      f(V <= T) = T * tanh(g * (V - T) / T)
      f(V > T)  = f_max * tanh(g * (V - T) / f_max)
      R(V) = max(0, f(V) + T)
    """
    is_scalar = np.isscalar(v) or np.ndim(v) == 0
    v_arr = np.asarray(v, dtype=np.float64)
    th_arr = np.asarray(threshold, dtype=np.float64)
    g_arr = np.asarray(gain, dtype=np.float64)
    fm_arr = np.asarray(f_max, dtype=np.float64)

    delta_v = v_arr - th_arr
    scale = np.where(delta_v <= 0.0, th_arr, fm_arr)
    f = scale * np.tanh(g_arr * delta_v / np.maximum(scale, 1e-12))
    out = np.maximum(0.0, f + th_arr)
    return float(out) if is_scalar else out


def euler_step_voltage(
    v_prev: Union[float, np.ndarray],
    i_tot: Union[float, np.ndarray],
    tau_v: Union[float, np.ndarray],
    dt: float = 1.0
) -> Union[float, np.ndarray]:
    """
    Performs one Euler integration step for the membrane potential.
    dV/dt = (-V + I_tot) / tau_V
    """
    is_scalar = np.isscalar(v_prev) or np.ndim(v_prev) == 0
    v_arr = np.asarray(v_prev, dtype=np.float64)
    i_arr = np.asarray(i_tot, dtype=np.float64)
    tau_arr = np.asarray(tau_v, dtype=np.float64)

    dv = (dt / np.maximum(tau_arr, 1e-12)) * (-v_arr + i_arr)
    v_next = v_arr + dv
    return float(v_next) if is_scalar else v_next


def euler_step_adaptation(
    a_prev: np.ndarray,
    rates: np.ndarray,
    tau_a: Union[float, np.ndarray] = 100.0,
    ca: float = 0.0,
    beta_a: float = 0.0,
    dt: float = 1.0
) -> np.ndarray:
    """
    Performs one Euler integration step for spike frequency adaptation.
    da/dt = (-a + ca * R) / tau_a
    """
    tau_arr = np.asarray(tau_a, dtype=np.float64)
    coeff = ca if ca != 0.0 else beta_a
    da = (dt / np.maximum(tau_arr, 1e-12)) * (-a_prev + coeff * rates)
    return a_prev + da


def compute_spectral_analysis(
    rates: np.ndarray,
    dt: float = 0.001,
    t_start_ms: int = 1000,
    nperseg: Optional[int] = None
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Computes power spectral density and identifies dominant oscillation frequency.
    Matches MATLAB @Network/Simulate.m Welch PSD estimation.
    """
    start_idx = min(t_start_ms, rates.shape[0] // 2)
    steady_state_rates = rates[start_idx:, :]

    # Population mean firing rate
    pop_mean = np.mean(steady_state_rates, axis=1)
    pop_mean_centered = pop_mean - np.mean(pop_mean)

    fs = 1.0 / dt
    if nperseg is None:
        nperseg = min(len(pop_mean_centered), int(2.0 * fs))

    freqs, psd = signal.welch(
        pop_mean_centered,
        fs=fs,
        window='hann',
        nperseg=nperseg,
        scaling='density'
    )

    # Focus on physiological locomotor range (0.5 to 15 Hz)
    valid_range = (freqs >= 0.5) & (freqs <= 15.0)
    if np.any(valid_range):
        peak_idx = np.argmax(psd[valid_range])
        dominant_freq = float(freqs[valid_range][peak_idx])
        peak_power = float(psd[valid_range][peak_idx])
    else:
        dominant_freq = 0.0
        peak_power = 0.0

    return {
        'frequencies_hz': freqs,
        'psd': psd,
        'dominant_frequency_hz': dominant_freq,
        'peak_power': peak_power,
        'mean_population_rate_hz': float(np.mean(pop_mean))
    }
