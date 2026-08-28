"""
Wave Comparative Math Module: Mathematical Dissection of 5 Locomotor Wave/Migration Objects.
Quantifies and contrasts the 5 distinct mathematical entities and explains the velocity discrepancy.
"""

from typing import Dict, List
import numpy as np
import pandas as pd


def build_wave_definition_table() -> pd.DataFrame:
    """
    Constructs the comparative mathematical table of the 5 locomotor wave objects.
    """
    data = [
        {
            "object_id": 1,
            "phenomenon_name": "Yakovenko Center-of-Activity Migration",
            "mathematical_definition": "r_cm(t) = sum(s * A(s,t)) / sum(A(s,t))",
            "biological_substrate": "Centroid of active motoneurons across 30 slices",
            "underlying_cause": "Phase-staggered empirical muscle recruitment",
            "velocity_concept": "Kinematic Centroid Velocity: |dr_cm/dt| (300-415 mm/s)",
            "continuity": "Discontinuous (Rapid jumps at stance-swing transitions)",
            "generative_or_epiphenomenon": "Epiphenomenon of muscle timing"
        },
        {
            "object_id": 2,
            "phenomenon_name": "Yakovenko Stance-to-Swing Phase Shift",
            "mathematical_definition": "Delta r_cm = r_cm(swing) - r_cm(stance)",
            "biological_substrate": "Switching between extensor (L7-S1) and flexor (L4-L6) pools",
            "underlying_cause": "Reciprocal inhibition / half-center switching",
            "velocity_concept": "Phase Shift Velocity: Delta Z / Delta t_trans (~400 mm/s)",
            "continuity": "Step-like jump across spinal segments",
            "generative_or_epiphenomenon": "Macro-level half-center state change"
        },
        {
            "object_id": 3,
            "phenomenon_name": "Komi Continuous Traveling Wave",
            "mathematical_definition": "phi(z) = phi_0 + (2*pi*f / v_wave) * z",
            "biological_substrate": "Premotor interneuronal firing phase sequence",
            "underlying_cause": "Asymmetric descending axonal kernels + zero-sum E/I",
            "velocity_concept": "Phase Wave Velocity: v_wave = omega / k (36.5-130 mm/s in cat, 1.85 mm/s in mouse)",
            "continuity": "Smooth, continuous, linear phase unwrapping",
            "generative_or_epiphenomenon": "Generative neurogenic dynamical mode"
        },
        {
            "object_id": 4,
            "phenomenon_name": "Komi Propagating Neural Activity",
            "mathematical_definition": "R(z, t) = R_0 + A(z) * cos(2*pi*f*t - k*z)",
            "biological_substrate": "Spatiotemporal rate landscape across all ventral neurons",
            "underlying_cause": "Autonomous limit cycle trajectory on SVD plane",
            "velocity_concept": "Spatiotemporal Wavefront Propagation (dx/dt of crest)",
            "continuity": "Continuous spatiotemporal field",
            "generative_or_epiphenomenon": "Emergent recurrent circuit property"
        },
        {
            "object_id": 5,
            "phenomenon_name": "Motor-Pool Output Activation Sequence",
            "mathematical_definition": "A_m(t) = sum_{s} N_{m,s} * R_slice(s, t)",
            "biological_substrate": "27 individual hindlimb motor pool drives",
            "underlying_cause": "Continuous wave filtered through anatomical somatotopy",
            "velocity_concept": "Sequential Joint Activation Delays (Hip -> Knee -> Ankle)",
            "continuity": "Segmented polyphasic bursts",
            "generative_or_epiphenomenon": "Neuromechanical output drive"
        }
    ]
    df = pd.DataFrame(data)
    return df
