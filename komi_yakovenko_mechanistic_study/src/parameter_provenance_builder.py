"""
Parameter Provenance Table Generator.
Exports the full parameter provenance audit to CSV and DataFrame.
"""

import pandas as pd

def build_parameter_provenance_table() -> pd.DataFrame:
    params = [
        {
            "Parameter": "Spinal Cord Length (L_cord)",
            "Komi_Value": "11.0 mm (Mouse T13-S4)",
            "Yakovenko_Value": "28.8 mm (Cat L4-S1)",
            "Transferred_Value": "28.8 mm",
            "Source": "Yakovenko et al. (2002), Table 1",
            "Reason_for_Transfer": "Cat anatomical coordinate boundary",
            "Directly_Measured": "Yes (Anatomy)",
            "Assumed": "No",
            "Fitted": "No",
            "Sensitivity": "Linear scaling of spatial bin coordinates"
        },
        {
            "Parameter": "Transverse Hemicord Width (w_cord)",
            "Komi_Value": "1.2 mm",
            "Yakovenko_Value": "3.6 mm",
            "Transferred_Value": "3.6 mm",
            "Source": "Yakovenko et al. (2002) Methods",
            "Reason_for_Transfer": "Mediolateral bounding box for cat ventral horn",
            "Directly_Measured": "Yes (Anatomy)",
            "Assumed": "No",
            "Fitted": "No",
            "Sensitivity": "Low (affects ML projection kernel scaling)"
        },
        {
            "Parameter": "Dorsoventral Height (h_cord)",
            "Komi_Value": "1.5 mm",
            "Yakovenko_Value": "5.5 mm",
            "Transferred_Value": "5.5 mm (Ventral: 1.2-4.2 mm)",
            "Source": "Yakovenko et al. (2002) Methods",
            "Reason_for_Transfer": "Dorsoventral bounding box for cat ventral horn",
            "Directly_Measured": "Yes (Anatomy)",
            "Assumed": "Ventral limit (1.2-4.2 mm)",
            "Fitted": "No",
            "Sensitivity": "Low"
        },
        {
            "Parameter": "Motoneuron Pool Somatotopy (N_m,s)",
            "Komi_Value": "35 Generic pools",
            "Yakovenko_Value": "27 Specific Cat Hindlimb pools",
            "Transferred_Value": "27 Specific Cat Hindlimb pools",
            "Source": "VanderHorst & Holstege (1997), Yakovenko Table 1",
            "Reason_for_Transfer": "Biological output mapping constraint",
            "Directly_Measured": "Yes (Retrograde HRP)",
            "Assumed": "No",
            "Fitted": "No",
            "Sensitivity": "High (shapes center-of-activity trajectory)"
        },
        {
            "Parameter": "Axonal Excitatory Reach (sigma_z,exc)",
            "Komi_Value": "1.8 mm (Mouse)",
            "Yakovenko_Value": "Not measured",
            "Transferred_Value": "6.0 mm",
            "Source": "Transferred from Komi scaled to cat spinal length",
            "Reason_for_Transfer": "Spanning 6-8 cat slices (equivalent to ~2 spinal segments)",
            "Directly_Measured": "No (Mouse only)",
            "Assumed": "Yes (Anatomical scale transfer)",
            "Fitted": "No",
            "Sensitivity": "Moderate (controls wave propagation smoothness)"
        },
        {
            "Parameter": "Axonal Inhibitory Reach (sigma_z,inh)",
            "Komi_Value": "0.8 mm (Mouse)",
            "Yakovenko_Value": "Not measured",
            "Transferred_Value": "2.5 mm",
            "Source": "Transferred from Komi scaled to cat spinal length",
            "Reason_for_Transfer": "Local recurrent inhibition within 2-3 cat slices",
            "Directly_Measured": "No (Mouse only)",
            "Assumed": "Yes (Anatomical scale transfer)",
            "Fitted": "No",
            "Sensitivity": "High (maintains Mexican-hat trough)"
        },
        {
            "Parameter": "Descending Projection Bias (mu_z,exc)",
            "Komi_Value": "+1.2 mm (Mouse)",
            "Yakovenko_Value": "Not measured",
            "Transferred_Value": "+3.5 mm",
            "Source": "Transferred from Komi scaled to cat spinal length",
            "Reason_for_Transfer": "Creates directional asymmetry for rostrocaudal wave",
            "Directly_Measured": "No (Mouse only)",
            "Assumed": "Yes (Descending bias principle)",
            "Fitted": "No",
            "Sensitivity": "High (breaks symmetry; determines wave direction)"
        },
        {
            "Parameter": "Leaky Rate Time Constant (tau)",
            "Komi_Value": "20.0 ms",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "20.0 ms",
            "Source": "Komi et al. (2026), Simulate.m",
            "Reason_for_Transfer": "Standard biophysical rate integration time constant",
            "Directly_Measured": "No (Model param)",
            "Assumed": "Yes (Transferred unchanged)",
            "Fitted": "No",
            "Sensitivity": "Moderate (scales dominant frequency)"
        },
        {
            "Parameter": "Tonic Driving Current (I_tonic)",
            "Komi_Value": "15.0 pA",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "15.0 pA",
            "Source": "Komi et al. (2026), Simulate.m",
            "Reason_for_Transfer": "Unpatterned tonic somatic drive",
            "Directly_Measured": "No (Model param)",
            "Assumed": "Yes (Transferred unchanged)",
            "Fitted": "No",
            "Sensitivity": "Low across 10-30 pA range"
        },
        {
            "Parameter": "Activation Non-Linearity (f_max, T)",
            "Komi_Value": "f_max = 100 Hz, T = 0 pA",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "f_max = 100 Hz, T = 0 pA",
            "Source": "Komi et al. (2026), Compound Tanh",
            "Reason_for_Transfer": "Standard rate saturation function",
            "Directly_Measured": "No (Model param)",
            "Assumed": "Yes (Transferred unchanged)",
            "Fitted": "No",
            "Sensitivity": "Low"
        },
        {
            "Parameter": "Commissural Fraction & E/I Ratio",
            "Komi_Value": "15% commissural, 60:40 E/I",
            "Yakovenko_Value": "Not measured",
            "Transferred_Value": "15% commissural, 60:40 E/I",
            "Source": "Mammalian spinal electrophysiology literature (V0v/V0d)",
            "Reason_for_Transfer": "Contralateral inhibition for left-right alternation",
            "Directly_Measured": "No (Literature estimate)",
            "Assumed": "Yes",
            "Fitted": "No",
            "Sensitivity": "High for bilateral alternation"
        },
        {
            "Parameter": "Spectral Rescaling Factor (g_spec)",
            "Komi_Value": "1.25",
            "Yakovenko_Value": "Not modeled",
            "Transferred_Value": "1.25",
            "Source": "BergLab RescaleConnectivity.m",
            "Reason_for_Transfer": "Places network into self-sustaining rotational limit cycle",
            "Directly_Measured": "No (Model param)",
            "Assumed": "Yes",
            "Fitted": "No",
            "Sensitivity": "High (determines limit cycle emergence vs decay)"
        }
    ]
    return pd.DataFrame(params)
