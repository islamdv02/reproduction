"""
Gain Modulation Module: Decoupled Control of Locomotor Frequency vs Burst Amplitude.
Implements Komi et al. (2026) orthogonal gain sweeps on the cat spinal connectome.
"""

from typing import List, Dict, Tuple
import numpy as np
from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from phase_analysis import PhaseUnfolder


class DecoupledGainController:
    """
    Performs systematic gain sweeps across excitatory (sp3-analog) and inhibitory (sp2-analog) populations
    to test for independent regulation of burst amplitude and stride frequency.
    """

    def __init__(self, network: YakovenkoKomiSpatialNetwork):
        self.network = network

    def sweep_excitatory_gain(self, gains: List[float] = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]) -> Dict[str, np.ndarray]:
        """Sweeps excitatory population gain (scaling burst amplitude / orbit radius)."""
        freqs = []
        amplitudes = []
        orbit_radii = []

        for g in gains:
            # Build connectome and scale excitatory weights
            conn = CatSynapticConnectome(self.network, balance_ei=True)
            for j in range(self.network.n_neurons):
                if self.network.is_excitatory[j]:
                    conn.W[:, j] *= g

            dyn = RecurrentRateDynamics(conn)
            times_ms, rates, _ = dyn.simulate(duration_ms=2500.0, warmup_ms=500.0)
            pu = PhaseUnfolder(rates, times_ms)

            freqs.append(pu.frequency_hz)
            amplitudes.append(np.mean(np.max(rates, axis=1) - np.min(rates, axis=1)))
            orbit_radii.append(pu.orbit_radius)

        return {
            'gains': np.array(gains),
            'frequencies_hz': np.array(freqs),
            'amplitudes_hz': np.array(amplitudes),
            'orbit_radii': np.array(orbit_radii)
        }

    def sweep_inhibitory_gain(self, gains: List[float] = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]) -> Dict[str, np.ndarray]:
        """Sweeps inhibitory population gain (accelerating frequency)."""
        freqs = []
        amplitudes = []
        orbit_radii = []

        for g in gains:
            # Build connectome and scale inhibitory weights
            conn = CatSynapticConnectome(self.network, balance_ei=True)
            for j in range(self.network.n_neurons):
                if not self.network.is_excitatory[j]:
                    conn.W[:, j] *= g

            dyn = RecurrentRateDynamics(conn)
            times_ms, rates, _ = dyn.simulate(duration_ms=2500.0, warmup_ms=500.0)
            pu = PhaseUnfolder(rates, times_ms)

            freqs.append(pu.frequency_hz)
            amplitudes.append(np.mean(np.max(rates, axis=1) - np.min(rates, axis=1)))
            orbit_radii.append(pu.orbit_radius)

        return {
            'gains': np.array(gains),
            'frequencies_hz': np.array(freqs),
            'amplitudes_hz': np.array(amplitudes),
            'orbit_radii': np.array(orbit_radii)
        }
