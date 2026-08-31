"""
Neural Dynamics Module: Forward Euler Leaky Rate Dynamics & Compound Tanh Activation.
Implements Komi et al. (2026) recurrent rate integration on Yakovenko cat spinal network.
"""

from typing import Tuple, Optional
import numpy as np
from connectivity import CatSynapticConnectome
from oscillation_gate import assert_oscillatory


def compound_tanh(I: np.ndarray, f_max: float = 100.0, threshold: float = 0.0) -> np.ndarray:
    """
    Komi et al. (2026) Compound Hyperbolic Tangent Activation Function:
    f(I) = f_max * tanh( max(0, I - T) / f_max )
    """
    rectified = np.maximum(0.0, I - threshold)
    return f_max * np.tanh(rectified / f_max)


class RecurrentRateDynamics:
    """
    Simulates recurrent rate dynamics across the 3D balanced cat spinal network.
    tau * dR/dt = -R + f( W @ R + I_tonic + I_ext + noise )
    """

    def __init__(
        self,
        connectome: CatSynapticConnectome,
        tau_ms: float = 20.0,
        dt_ms: float = 1.0,
        f_max: float = 100.0,
        threshold: float = 0.0,
        tonic_drive_pA: float = 30.0,
        noise_std: float = 0.5,
        rng_seed: int = 42
    ):
        self.connectome = connectome
        self.W = connectome.W
        self.N = connectome.network.n_neurons
        self.tau_ms = float(tau_ms)
        self.dt_ms = float(dt_ms)
        self.f_max = float(f_max)
        self.threshold = float(threshold)
        self.tonic_drive_pA = float(tonic_drive_pA)
        self.noise_std = float(noise_std)
        self.rng_seed = int(rng_seed)
        self.rng = np.random.default_rng(rng_seed)

    def simulate(
        self,
        duration_ms: float = 2500.0,
        warmup_ms: float = 500.0,
        external_drive: Optional[np.ndarray] = None,
        assert_gate: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Runs Forward Euler integration.
        Returns:
            times_ms: (n_steps,)
            rates: (N, n_steps)
            driving_currents: (N, n_steps)
        """
        n_total_steps = int(np.round(duration_ms / self.dt_ms))
        n_warmup_steps = int(np.round(warmup_ms / self.dt_ms))

        # Initial rates: small positive random state
        R = self.rng.uniform(2.0, 10.0, self.N)

        rates_history = np.zeros((self.N, n_total_steps), dtype=np.float64)
        currents_history = np.zeros((self.N, n_total_steps), dtype=np.float64)
        times_ms = np.arange(n_total_steps) * self.dt_ms

        dt_over_tau = self.dt_ms / self.tau_ms

        for t in range(n_total_steps):
            # Recurrent synaptic input
            syn_input = self.W @ R

            # External drive
            if external_drive is not None:
                ext_val = external_drive[:, t] if external_drive.ndim > 1 else external_drive[t]
            else:
                ext_val = 0.0

            # Noise
            if self.noise_std > 0.0:
                noise = self.rng.normal(0.0, self.noise_std, self.N)
            else:
                noise = 0.0

            # Total somatic current
            I_tot = syn_input + self.tonic_drive_pA + ext_val + noise

            # Activation
            target_R = compound_tanh(I_tot, f_max=self.f_max, threshold=self.threshold)

            # Leaky integration update
            R += dt_over_tau * (-R + target_R)
            R = np.maximum(0.0, R) # Firing rates non-negative

            rates_history[:, t] = R
            currents_history[:, t] = I_tot

        # Discard warmup
        valid_idx = slice(n_warmup_steps, n_total_steps)
        valid_times = times_ms[valid_idx] - warmup_ms
        valid_rates = rates_history[:, valid_idx]
        valid_currents = currents_history[:, valid_idx]

        # Verify noiseless oscillation gate if requested and connectome is balanced
        if assert_gate and self.connectome.balance_ei and (self.noise_std == 0.0):
            assert_oscillatory(self.W, valid_rates, name=f"CatNetwork(N={self.N}, seed={self.rng_seed})")

        return valid_times, valid_rates, valid_currents
