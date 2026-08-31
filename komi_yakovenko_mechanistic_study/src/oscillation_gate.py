"""
Oscillation Gate & Eigenvalue Diagnostics Module.
Provides hard oscillation assertion and spectral diagnostics for neural network models.
"""

from typing import Tuple, Optional, Union
import numpy as np


def print_eigenvalue_diagnostics(W: np.ndarray, name: str = "Network") -> Tuple[float, float, float]:
    """
    Computes and prints leading eigenvalue diagnostics:
      - Dominant eigenvalue real part max Re(lambda)
      - Imaginary part at that dominant eigenvalue Im(lambda_dom)
      - Spectral radius max |lambda|
    Returns (max_re, im_at_max_re, spectral_radius).
    """
    try:
        ev = np.linalg.eigvals(W)
        i = np.argmax(ev.real)
        max_re = float(ev[i].real)
        im_at_dom = float(ev[i].imag)
        spectral_radius = float(np.max(np.abs(ev)))
        print(f"[{name}] Eigenvalue Diagnostics: max Re(lambda)={max_re:.4f}, Im={im_at_dom:+.4f}, Spectral Radius={spectral_radius:.4f}")
        return max_re, im_at_dom, spectral_radius
    except Exception as e:
        print(f"[{name}] Warning: Eigenvalue computation failed: {e}")
        return 0.0, 0.0, 0.0


def assert_oscillatory(
    W: np.ndarray,
    rates_noiseless: np.ndarray,
    name: str = "Network"
) -> None:
    """
    Hard oscillation gate assertion.
    Asserts:
      1. max Re(lambda) > 1.0 (linear instability / above Hopf threshold)
      2. |Im(lambda_dom)| > 1e-3 (dominant mode is complex conjugate pair, not static bump)
      3. Noiseless steady-state population firing rate peak-to-peak amplitude > 0.5 Hz
    """
    ev = np.linalg.eigvals(W)
    i = np.argmax(ev.real)
    dom = ev[i]

    assert dom.real > 1.0, f"{name}: max Re(lambda)={dom.real:.4f} <= 1"
    assert abs(dom.imag) > 1e-3, f"{name}: dominant mode is real (Im={dom.imag:.4f}), no rotation"

    # Support rates_noiseless formatted as (neurons, time) or (time, neurons) or 1D (time,)
    if rates_noiseless.ndim == 2:
        if rates_noiseless.shape[0] < rates_noiseless.shape[1]:
            # (neurons, time)
            mean_t = np.mean(rates_noiseless, axis=0)
        else:
            # (time, neurons)
            mean_t = np.mean(rates_noiseless, axis=1)
    elif rates_noiseless.ndim == 1:
        mean_t = rates_noiseless
    else:
        raise ValueError(f"{name}: invalid rates array shape {rates_noiseless.shape}")

    steady_window = mean_t[-1000:] if len(mean_t) >= 1000 else mean_t
    ptp = float(np.ptp(steady_window))
    assert ptp > 0.5, f"{name}: noiseless amplitude {ptp:.5f} Hz <= 0.5 Hz - fixed point detected"
