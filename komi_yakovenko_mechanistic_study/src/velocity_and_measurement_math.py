"""
Velocity and Measurement Mathematics Module:
Analytical derivations and numerical simulations dissecting the mathematical differences between:
1. r_cm(t) (Yakovenko motoneuron center of activity)
2. phi(z,t) (Komi premotor interneuronal circular phase)
3. v_cm(t) = |dr_cm/dt| (Kinematic centroid migration velocity)
4. v_wave = omega / k (Neural phase wave propagation velocity)
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


def analytical_bimodal_somatotopy_derivation(
    z_flex: float = 6.0,
    z_ext: float = 22.0,
    omega: float = 8.98,  # rad/s (T = 0.7 s)
    k: float = 0.087,     # rad/mm (Phase lag across 28.8 mm)
    n_points: int = 200
) -> Dict[str, np.ndarray]:
    """
    Simulates a continuous interneuronal wave driving two segregated motor pools:
      r(z, t) = max(0, cos(omega * t - k * z))
      Flexor pool at z_flex, Extensor pool at z_ext.
    Derives r_cm(t) and v_cm(t) to prove why v_cm can be high and discontinuous
    even when the underlying neural wave is slow and continuous.
    """
    t = np.linspace(0, 2.0 * np.pi / omega, n_points)
    dt = t[1] - t[0]

    # Continuous neural phase wave at flexor and extensor sites
    f_act = np.maximum(0.0, np.cos(omega * t - k * z_flex))
    e_act = np.maximum(0.0, np.cos(omega * t - k * z_ext))

    # Center of activity
    total_act = f_act + e_act + 1e-9
    r_cm = (z_flex * f_act + z_ext * e_act) / total_act

    # Kinematic migration velocity
    v_cm = np.abs(np.gradient(r_cm, dt))

    # Phase wave velocity
    v_wave = omega / k # mm/s

    return {
        'time_s': t,
        'step_pct': (t / t[-1]) * 100.0,
        'flexor_activation': f_act,
        'extensor_activation': e_act,
        'r_cm_mm': r_cm,
        'v_cm_mm_s': v_cm,
        'v_wave_mm_s': np.full_like(t, v_wave),
        'theoretical_v_wave': float(v_wave),
        'max_v_cm': float(np.max(v_cm)),
        'mean_v_cm': float(np.mean(v_cm))
    }


def get_5_phenomena_comparison_dataframe() -> pd.DataFrame:
    """
    Returns structured comparative table of the 5 distinct locomotor wave/migration phenomena.
    """
    records = [
        {
            "Index": 1,
            "Phenomenon_Name": "Yakovenko Motoneuron Center-of-Activity (r_cm)",
            "Mathematical_Equation": "r_{cm}(t) = \\frac{\\sum_{s=1}^{30} z_s A(s,t)}{\\sum_{s=1}^{30} A(s,t)}",
            "Biological_Substrate": "Spatial centroid of active motoneurons across 30 lumbosacral slices",
            "Underlying_Driver": "Empirical muscle EMG waveforms multiplied by anatomical motor pool somatotopy",
            "Velocity_Metric": "v_{cm} = |\\frac{dr_{cm}}{dt}| (Peaks > 40 mm/s at swing/stance transitions)",
            "Continuity": "Discontinuous / Bimodal (Dwells in L7 during stance, snaps to L4/L5 during swing)",
            "Causal_Status": "IMPOSED output consequence (Kinematic epiphenomenon of muscle timing)"
        },
        {
            "Index": 2,
            "Phenomenon_Name": "Yakovenko Stance-to-Swing Segmental Shift",
            "Mathematical_Equation": "\\Delta r_{cm} = r_{cm}(\\text{swing}) - r_{cm}(\\text{stance}) \\approx 16 \\text{ mm}",
            "Biological_Substrate": "Discrete activation switch between rostral flexor pools and caudal extensor pools",
            "Underlying_Driver": "Reciprocal inhibition between flexor and extensor half-centers",
            "Velocity_Metric": "\\Delta Z / \\Delta t_{\\text{trans}} \\approx 100-300 \\text{ mm/s}",
            "Continuity": "Step-like segmental transition across spinal cord",
            "Causal_Status": "IMPOSED macroscopic state change"
        },
        {
            "Index": 3,
            "Phenomenon_Name": "Komi Continuous Traveling Phase Wave",
            "Mathematical_Equation": "\\phi(z,t) = \\omega t - k z, \\quad v_{\\text{wave}} = \\frac{\\omega}{k}",
            "Biological_Substrate": "Premotor ventral interneuronal firing phase sequence along rostrocaudal axis",
            "Underlying_Driver": "Recurrent asymmetric descending projectome kernels + zero-sum E/I balance",
            "Velocity_Metric": "v_{\\text{wave}} = \\frac{\\partial z}{\\partial t} (36.5 - 130 mm/s in cat, 1.85 mm/s in mouse)",
            "Continuity": "Smooth, continuous, linear phase progression along length of cord",
            "Causal_Status": "EMERGENT autonomous dynamical mode (Central pattern generator engine)"
        },
        {
            "Index": 4,
            "Phenomenon_Name": "Komi Spatiotemporal Firing Rate Wavefront",
            "Mathematical_Equation": "R(z, t) = R_0 + A(z) \\cos(\\omega t - k z)",
            "Biological_Substrate": "3D spatiotemporal rate field across all ventral interneuronal populations",
            "Underlying_Driver": "Rotational limit cycle attractor on leading principal component plane",
            "Velocity_Metric": "Wavefront crest propagation velocity (\\frac{dz_{\\text{crest}}}{dt})",
            "Continuity": "Continuous spatiotemporal rate field",
            "Causal_Status": "EMERGENT recurrent circuit property"
        },
        {
            "Index": 5,
            "Phenomenon_Name": "Somatotopic Motor-Pool Activation Bursts",
            "Mathematical_Equation": "A_m(t) = \\sum_{s=1}^{30} N_{m,s} R_{\\text{slice}}(s, t)",
            "Biological_Substrate": "27 individual hindlimb motor pools driving 14 multi-joint muscles",
            "Underlying_Driver": "Continuous interneuronal wave filtered through anatomical somatotopy matrix N(m, s)",
            "Velocity_Metric": "Sequential multi-joint activation delays (Hip -> Knee -> Ankle)",
            "Continuity": "Segmented, polyphasic motor pool bursts",
            "Causal_Status": "EMERGENT neuromechanical output drive"
        }
    ]
    return pd.DataFrame(records)
