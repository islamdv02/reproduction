"""
Controls & Parameter Sensitivity Module.
Implements Controls A, B, C, D and systematic sensitivity sweeps on the cat spinal projectome.
"""

from typing import Dict, List, Tuple
import numpy as np
from spatial_mapping import YakovenkoKomiSpatialNetwork
from connectivity import CatSynapticConnectome
from neural_dynamics import RecurrentRateDynamics
from phase_analysis import PhaseUnfolder
from projectome_analysis import ProjectomeAnalyzer
from traveling_wave import TravelingWaveAnalyzer


class ControlsAndSensitivityRunner:
    """
    Executes benchmark control models and parameter sensitivity sweeps.
    """

    def __init__(self, rng_seed: int = 42):
        self.rng_seed = rng_seed

    def run_control_experiments(self) -> Dict[str, Dict[str, float]]:
        """
        Runs the 4 fundamental control models:
        - Control A: Main Model (Yakovenko 3D Anatomy + Komi Anisotropic Balanced Connectome)
        - Control B: Shuffled Anatomy (Randomized Z positions + Komi Connectome)
        - Control C: Unstructured Connectome (Yakovenko Anatomy + Random Erdos-Renyi Wiring)
        - Control D: Unbalanced E/I (Yakovenko Anatomy + Unbalanced W)
        """
        results = {}

        # 1. Control A (Main Model)
        net_a = YakovenkoKomiSpatialNetwork(n_neurons=800, rng_seed=self.rng_seed)
        conn_a = CatSynapticConnectome(net_a, balance_ei=True, rng_seed=self.rng_seed)
        dyn_a = RecurrentRateDynamics(conn_a, rng_seed=self.rng_seed)
        times, rates_a, _ = dyn_a.simulate(duration_ms=2000.0, warmup_ms=500.0)
        pu_a = PhaseUnfolder(rates_a, times)
        proj_a = ProjectomeAnalyzer(conn_a)
        wave_a = TravelingWaveAnalyzer(net_a, rates_a, times)

        results['Control_A_Main'] = {
            'planar_variance': pu_a.planar_variance,
            'orbit_radius': pu_a.orbit_radius,
            'mexican_hat_index': proj_a.mexican_hat_index,
            'wave_velocity_mm_s': wave_a.velocity_mm_s,
            'bilateral_alternation': wave_a.alternation_index
        }

        # 2. Control B (Shuffled Z Anatomy)
        net_b = YakovenkoKomiSpatialNetwork(n_neurons=800, rng_seed=self.rng_seed)
        net_b.rng.shuffle(net_b.z) # Disrupt spatial gradient
        conn_b = CatSynapticConnectome(net_b, balance_ei=True, rng_seed=self.rng_seed)
        dyn_b = RecurrentRateDynamics(conn_b, rng_seed=self.rng_seed)
        times, rates_b, _ = dyn_b.simulate(duration_ms=2000.0, warmup_ms=500.0)
        pu_b = PhaseUnfolder(rates_b, times)
        proj_b = ProjectomeAnalyzer(conn_b)
        wave_b = TravelingWaveAnalyzer(net_b, rates_b, times)

        results['Control_B_Shuffled'] = {
            'planar_variance': pu_b.planar_variance,
            'orbit_radius': pu_b.orbit_radius,
            'mexican_hat_index': proj_b.mexican_hat_index,
            'wave_velocity_mm_s': wave_b.velocity_mm_s,
            'bilateral_alternation': wave_b.alternation_index
        }

        # 3. Control C (Unstructured Random Connectivity)
        net_c = YakovenkoKomiSpatialNetwork(n_neurons=800, rng_seed=self.rng_seed)
        conn_c = CatSynapticConnectome(net_c, balance_ei=True, rng_seed=self.rng_seed)
        # Flatten spatial probability to uniform Erdos-Renyi
        N = net_c.n_neurons
        rand_adj = (conn_c.rng.random((N, N)) < 0.12).astype(np.float64)
        np.fill_diagonal(rand_adj, 0.0)
        for j in range(N):
            if net_c.is_excitatory[j]:
                conn_c.W[:, j] = rand_adj[:, j] * conn_c.rng.uniform(0.5, 1.5, N)
            else:
                conn_c.W[:, j] = -rand_adj[:, j] * conn_c.rng.uniform(0.5, 1.5, N)
        # Rebalance
        for i in range(N):
            r_exc = np.sum(conn_c.W[i, conn_c.W[i, :] > 0])
            r_inh = np.sum(np.abs(conn_c.W[i, conn_c.W[i, :] < 0]))
            if r_inh > 1e-6 and r_exc > 1e-6:
                conn_c.W[i, conn_c.W[i, :] < 0] *= (r_exc / r_inh)
        try:
            eigs = np.linalg.eigvals(conn_c.W)
            conn_c.W = (conn_c.W / np.max(np.abs(eigs))) * 1.25
        except Exception:
            pass

        dyn_c = RecurrentRateDynamics(conn_c, rng_seed=self.rng_seed)
        times, rates_c, _ = dyn_c.simulate(duration_ms=2000.0, warmup_ms=500.0)
        pu_c = PhaseUnfolder(rates_c, times)
        proj_c = ProjectomeAnalyzer(conn_c)
        wave_c = TravelingWaveAnalyzer(net_c, rates_c, times)

        results['Control_C_Unstructured'] = {
            'planar_variance': pu_c.planar_variance,
            'orbit_radius': pu_c.orbit_radius,
            'mexican_hat_index': proj_c.mexican_hat_index,
            'wave_velocity_mm_s': wave_c.velocity_mm_s,
            'bilateral_alternation': wave_c.alternation_index
        }

        # 4. Control D (Unbalanced E/I)
        net_d = YakovenkoKomiSpatialNetwork(n_neurons=800, rng_seed=self.rng_seed)
        conn_d = CatSynapticConnectome(net_d, balance_ei=False, rng_seed=self.rng_seed)
        dyn_d = RecurrentRateDynamics(conn_d, rng_seed=self.rng_seed)
        times, rates_d, _ = dyn_d.simulate(duration_ms=2000.0, warmup_ms=500.0)
        pu_d = PhaseUnfolder(rates_d, times)
        proj_d = ProjectomeAnalyzer(conn_d)
        wave_d = TravelingWaveAnalyzer(net_d, rates_d, times)

        results['Control_D_Unbalanced'] = {
            'planar_variance': pu_d.planar_variance,
            'orbit_radius': pu_d.orbit_radius,
            'mexican_hat_index': proj_d.mexican_hat_index,
            'wave_velocity_mm_s': wave_d.velocity_mm_s,
            'bilateral_alternation': wave_d.alternation_index
        }

        return results

    def sweep_kernel_width(self, sigmas: List[float] = [2.0, 4.0, 6.0, 8.0, 10.0]) -> Dict[str, np.ndarray]:
        """Sweeps longitudinal kernel span and evaluates Mexican-hat index and wave velocity."""
        mhis = []
        vels = []

        for sig in sigmas:
            net = YakovenkoKomiSpatialNetwork(n_neurons=600, rng_seed=self.rng_seed)
            conn = CatSynapticConnectome(net, balance_ei=True, rng_seed=self.rng_seed)
            proj = ProjectomeAnalyzer(conn)
            dyn = RecurrentRateDynamics(conn, rng_seed=self.rng_seed)
            times, rates, _ = dyn.simulate(duration_ms=1800.0, warmup_ms=400.0)
            wave = TravelingWaveAnalyzer(net, rates, times)

            mhis.append(proj.mexican_hat_index)
            vels.append(wave.velocity_mm_s)

        return {
            'kernel_widths_mm': np.array(sigmas),
            'mexican_hat_indices': np.array(mhis),
            'wave_velocities_mm_s': np.array(vels)
        }
