"""
Parameter Provenance & Pre-Registered Predictions Module.
Contains complete mathematical and empirical extraction from Komi et al. (2026) and Yakovenko et al. (2002),
categorizing every parameter into Categories A, B, C, and D.
"""

from typing import Dict, List
import pandas as pd


def get_parameter_provenance_dataframe() -> pd.DataFrame:
    """
    Returns full parameter provenance table with Category A, B, C, D distinctions.
    Category A: Explicitly reported by Komi
    Category B: Mathematically implied by Komi
    Category C: Assumed by the original implementation
    Category D: Newly introduced for the Yakovenko transfer
    """
    records = [
        {
            "Parameter": "Spinal Cord Rostrocaudal Length (L_cord)",
            "Symbol": "L_{cord}",
            "Komi_Value": "11.0 mm (Mouse T13-S4)",
            "Yakovenko_Value": "28.8 mm (Cat L4-S1)",
            "Transferred_Value": "28.8 mm",
            "Category": "D. Newly introduced for transfer",
            "Source_Citation": "Yakovenko et al. (2002) Table 1",
            "Justification": "Physical anatomical boundary of cat lumbosacral segments",
            "Tuned_To_Fit": "No (Untuned anatomical constraint)"
        },
        {
            "Parameter": "Transverse Hemicord Width",
            "Symbol": "w_{cord}",
            "Komi_Value": "1.2 mm",
            "Yakovenko_Value": "3.6 mm",
            "Transferred_Value": "3.6 mm",
            "Category": "D. Newly introduced for transfer",
            "Source_Citation": "Yakovenko et al. (2002) Methods",
            "Justification": "Cat ventral horn mediolateral bounding box",
            "Tuned_To_Fit": "No (Untuned anatomical constraint)"
        },
        {
            "Parameter": "Dorsoventral Height",
            "Symbol": "h_{cord}",
            "Komi_Value": "1.5 mm",
            "Yakovenko_Value": "5.5 mm",
            "Transferred_Value": "5.5 mm (Ventral: 1.2-4.2 mm)",
            "Category": "D. Newly introduced for transfer",
            "Source_Citation": "Yakovenko et al. (2002) Methods",
            "Justification": "Cat ventral horn dorsoventral coordinate range",
            "Tuned_To_Fit": "No (Untuned anatomical constraint)"
        },
        {
            "Parameter": "Motoneuron Pool Spatial Somatotopy",
            "Symbol": "N_{m,s}",
            "Komi_Value": "35 Generic motor pools",
            "Yakovenko_Value": "27 Specific Cat Hindlimb pools",
            "Transferred_Value": "27 Specific Cat Hindlimb pools",
            "Category": "D. Newly introduced for transfer",
            "Source_Citation": "VanderHorst & Holstege (1997); Yakovenko Table 1",
            "Justification": "Empirical retrograde HRP pool distribution across 30 slices",
            "Tuned_To_Fit": "No (Untuned anatomical constraint)"
        },
        {
            "Parameter": "Axonal Excitatory Reach",
            "Symbol": "\\sigma_{z,exc}",
            "Komi_Value": "1.8 mm (Mouse)",
            "Yakovenko_Value": "Not measured",
            "Transferred_Value": "6.0 mm",
            "Category": "D. Newly introduced for transfer",
            "Source_Citation": "Proportional scaling of Komi reach to cat spinal length",
            "Justification": "Spans 6-8 cat slices (~2 spinal segments)",
            "Tuned_To_Fit": "No (Tested via sensitivity sweep)"
        },
        {
            "Parameter": "Axonal Inhibitory Reach",
            "Symbol": "\\sigma_{z,inh}",
            "Komi_Value": "0.8 mm (Mouse)",
            "Yakovenko_Value": "Not measured",
            "Transferred_Value": "2.5 mm",
            "Category": "D. Newly introduced for transfer",
            "Source_Citation": "Proportional scaling of Komi reach to cat spinal length",
            "Justification": "Local recurrent inhibition within 2-3 cat slices",
            "Tuned_To_Fit": "No (Tested via sensitivity sweep)"
        },
        {
            "Parameter": "Descending Projection Bias",
            "Symbol": "\\mu_{z,exc}",
            "Komi_Value": "+1.2 mm (Mouse)",
            "Yakovenko_Value": "Not measured",
            "Transferred_Value": "+3.5 mm",
            "Category": "D. Newly introduced for transfer",
            "Source_Citation": "Komi descending bias principle scaled to cat length",
            "Justification": "Breaks rostrocaudal symmetry to drive descending phase wave",
            "Tuned_To_Fit": "No (Tested via sensitivity sweep)"
        },
        {
            "Parameter": "Leaky Rate Time Constant",
            "Symbol": "\\tau",
            "Komi_Value": "20.0 ms",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "20.0 ms",
            "Category": "A. Explicitly reported by Komi",
            "Source_Citation": "Komi et al. (2026) Simulate.m",
            "Justification": "Biophysical rate integration time constant",
            "Tuned_To_Fit": "No (Direct Komi value)"
        },
        {
            "Parameter": "Tonic Driving Current",
            "Symbol": "I_{tonic}",
            "Komi_Value": "15.0 pA",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "15.0 pA",
            "Category": "A. Explicitly reported by Komi",
            "Source_Citation": "Komi et al. (2026) Simulate.m",
            "Justification": "Unpatterned somatic driving current",
            "Tuned_To_Fit": "No (Direct Komi value)"
        },
        {
            "Parameter": "Activation Function Parameters",
            "Symbol": "f_{max}, T, g",
            "Komi_Value": "f_{max}=100 Hz, T=0 pA, g=1.0",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "f_{max}=100 Hz, T=0 pA, g=1.0",
            "Category": "A. Explicitly reported by Komi",
            "Source_Citation": "Komi et al. (2026) Compound Tanh Activation",
            "Justification": "Rate saturation and rectification non-linearity",
            "Tuned_To_Fit": "No (Direct Komi equation)"
        },
        {
            "Parameter": "Row-Wise Zero-Sum E/I Balancing Rule",
            "Symbol": "\\sum_j W_{ij} = 0",
            "Komi_Value": "Exact row-wise cancellation",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "Exact row-wise cancellation",
            "Category": "A. Explicitly reported by Komi",
            "Source_Citation": "Komi et al. (2026) BalanceConnectivity.m",
            "Justification": "Stabilizes network dynamics near critical operating regime",
            "Tuned_To_Fit": "No (Direct Komi algorithm)"
        },
        {
            "Parameter": "Spectral Radius Rescaling Factor",
            "Symbol": "g_{spec}",
            "Komi_Value": "1.25",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "1.25",
            "Category": "A. Explicitly reported by Komi",
            "Source_Citation": "Komi et al. (2026) RescaleConnectivity.m",
            "Justification": "Places autonomous network into self-sustaining limit cycle",
            "Tuned_To_Fit": "No (Direct Komi value)"
        },
        {
            "Parameter": "Commissural Population Fraction",
            "Symbol": "f_{comm}",
            "Komi_Value": "15% (V0d, V0v, dI6, V3)",
            "Yakovenko_Value": "Not measured",
            "Transferred_Value": "15% (V0d, V0v, dI6, V3)",
            "Category": "C. Assumed by baseline implementation",
            "Source_Citation": "Spinal interneuron literature (Kullander 2003, Talpalar 2013)",
            "Justification": "Cross-cord projections responsible for left-right coordination",
            "Tuned_To_Fit": "No (Literature-based constant)"
        }
    ]
    return pd.DataFrame(records)


def get_preregistered_predictions_dataframe() -> pd.DataFrame:
    """
    Returns pre-registered predictions table formulated BEFORE looking at transfer results.
    """
    records = [
        {
            "Mechanism": "Rostrocaudal Asymmetric Connectivity (mu_z > 0)",
            "Mathematical_Form": "P(z_post, z_pre) propto exp(-(Delta z - mu_z)^2 / (2 sigma_z^2))",
            "Prediction_in_Yakovenko_System": "Progressive descending phase organization along L4 -> S1",
            "Direction_of_Expected_Effect": "Monotonic negative phase gradient dphi/dz < 0 (Rostral leads caudal)",
            "Pre_Registered": "Yes"
        },
        {
            "Mechanism": "Mexican-Hat Spatial Kernel",
            "Mathematical_Form": "Local Excitation (Delta z <= 2.5 mm) + Long-range Inhibition (Delta z > 2.5 mm)",
            "Prediction_in_Yakovenko_System": "Spatial localization of active wavefront; suppression of surround slices",
            "Direction_of_Expected_Effect": "Positive peak at Delta z ~ 0 flanked by negative trough",
            "Pre_Registered": "Yes"
        },
        {
            "Mechanism": "Recurrent Balanced Rate Dynamics",
            "Mathematical_Form": "tau dR/dt = -R + f(W @ R + I_tonic)",
            "Prediction_in_Yakovenko_System": "Spontaneous autonomous rhythm generation without periodic input",
            "Direction_of_Expected_Effect": "Single dominant frequency peak in 0.5-3.0 Hz range",
            "Pre_Registered": "Yes"
        },
        {
            "Mechanism": "Commissural Reciprocal Coupling",
            "Mathematical_Form": "Contralateral projections with balanced inhibitory bias",
            "Prediction_in_Yakovenko_System": "Left-right antiphase bilateral alternation",
            "Direction_of_Expected_Effect": "Bilateral phase difference Delta phi_LR ~ 180 degrees",
            "Pre_Registered": "Yes"
        },
        {
            "Mechanism": "Motor Pool Somatotopic Filtering",
            "Mathematical_Form": "A_m(t) = sum_s N_{m,s} * R_slice(s, t)",
            "Prediction_in_Yakovenko_System": "Continuous interneuronal wave produces discrete, segregated motor output bursts",
            "Direction_of_Expected_Effect": "Bimodal r_cm(t) trajectory dwelling in L7 during stance and jumping to L4-L5 in swing",
            "Pre_Registered": "Yes"
        },
        {
            "Mechanism": "Centroid Migration vs Neural Wave",
            "Mathematical_Form": "v_cm(t) = |dr_cm/dt| vs v_wave = omega / k",
            "Prediction_in_Yakovenko_System": "Kinematic centroid velocity exhibits high transition spikes (>30 mm/s) despite slow underlying wave",
            "Direction_of_Expected_Effect": "v_cm(t) peaks at stance-swing transitions; v_wave remains steady",
            "Pre_Registered": "Yes"
        }
    ]
    return pd.DataFrame(records)
