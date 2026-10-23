import json
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results_dir = os.path.join(root_dir, 'results')

json_main_path = os.path.join(results_dir, 'wave_scientific_audit.json')
json_all_metrics_path = os.path.join(results_dir, 'all_anatomical_wave_metrics.json')

with open(json_main_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(json_all_metrics_path, 'r', encoding='utf-8') as f:
    all_metrics = json.load(f)

# 1. Update hash of comparison figure
data['frozen_sha256_hashes']['comparison_figure_png'] = '866915779fab8efc16d022f070a8e283840846d3c359003ca0218dfe32474899'

# 2. Update author projection parameters
data['population_counts']['cell_classes']['V2a_1'] = {
    "count": 635,
    "type": "Excitatory",
    "laterality": "Ipsilateral",
    "BiasRC": "cau",
    "LengthScale_um": 500,
    "BiasDV": "ven",
    "BiasML": "med",
    "SynStrength": 0.5,
    "projections": "Caudal bias, ventral, medial, ipsilateral (LengthScale = 500 um, SynStrength = 0.5)"
}

data['population_counts']['cell_classes']['V2a_2'] = {
    "count": 185,
    "type": "Excitatory",
    "laterality": "Ipsilateral",
    "BiasRC": "bi",
    "LengthScale_um": 7000,
    "BiasDV": "ven",
    "BiasML": "lat",
    "SynStrength": 0.5,
    "projections": "Bilateral/longitudinal bias, ventral, lateral, ipsilateral (LengthScale = 7000 um, SynStrength = 0.5)"
}

data['population_counts']['cell_classes']['V1'] = {
    "count": 1173,
    "type": "Inhibitory",
    "laterality": "Ipsilateral",
    "BiasRC": "ro",
    "LengthScale_um": 2000,
    "BiasDV": "ven",
    "BiasML": "",
    "SynStrength": 0.1,
    "projections": "Rostral bias, ventral, ipsilateral (LengthScale = 2000 um, SynStrength = 0.1 [gc * 0.2])"
}

data['population_counts']['cell_classes']['V2b'] = {
    "count": 633,
    "type": "Inhibitory",
    "laterality": "Ipsilateral",
    "BiasRC": "cau",
    "LengthScale_um": 4000,
    "BiasDV": "ven",
    "BiasML": "lat",
    "SynStrength": 0.5,
    "projections": "Caudal bias, ventral, lateral, ipsilateral (LengthScale = 4000 um, SynStrength = 0.5)"
}

data['population_counts']['cell_classes']['V0d'] = {
    "count": 87,
    "type": "Inhibitory",
    "laterality": "Contralateral",
    "BiasRC": "loc",
    "LengthScale_um": 500,
    "BiasDV": "ven",
    "BiasML": "med",
    "SynStrength": 0.5,
    "projections": "Local bias, ventral, medial, contralateral (LengthScale = 500 um, SynStrength = 0.5)"
}

data['population_counts']['cell_classes']['V0v'] = {
    "count": 225,
    "type": "Excitatory",
    "laterality": "Contralateral",
    "BiasRC": "ro",
    "LengthScale_um": 3400,
    "BiasDV": "loc",
    "BiasML": "med",
    "SynStrength": 0.5,
    "projections": "Rostral bias, local DV, medial, contralateral (LengthScale = 3400 um, SynStrength = 0.5)"
}

data['population_counts']['cell_classes']['DI6'] = {
    "count": 60,
    "type": "Inhibitory",
    "laterality": "Contralateral",
    "BiasRC": "cau",
    "LengthScale_um": 5000,
    "BiasDV": "dor",
    "BiasML": "med",
    "SynStrength": 0.5,
    "projections": "Caudal bias, dorsal, medial, contralateral (LengthScale = 5000 um, SynStrength = 0.5)"
}

data['population_counts']['cell_classes']['V3'] = {
    "count": 141,
    "type": "Excitatory",
    "laterality": "Contralateral",
    "BiasRC": "cau",
    "LengthScale_um": 500,
    "BiasDV": "ven",
    "BiasML": "lat",
    "SynStrength": 0.5,
    "projections": "Caudal bias, ventral, lateral, contralateral (LengthScale = 500 um, SynStrength = 0.5)"
}

data['population_counts']['cell_classes']['MN'] = {
    "count": 1795,
    "type": "Cholinergic",
    "laterality": "Ipsilateral",
    "BiasRC": "loc",
    "LengthScale_um": 300,
    "BiasDV": "ven",
    "BiasML": "lat",
    "SynStrength": 0.5,
    "mn_to_in_scaling": 0.1,
    "architectural_note": "Local motoneuron recurrent connectivity (LengthScale = 300 um, 0.1 gain multiplier to interneurons via SetCellBiasPop) is an architectural parameterization specific to this computational model, not universal mammalian biology.",
    "projections": "Local bias, ventral, lateral, ipsilateral (LengthScale = 300 um, transmission to INs scaled by 0.1)"
}

# 3. Correct Figure 2F description to column-normalized reconstruction
data['figure_panel_provenance_and_status']['Figure2']['2F'] = {
    "status": "METHODS-BASED RECONSTRUCTION",
    "variable": "9x9 cell-type interaction matrix (column-normalized incoming synaptic weight per pair)",
    "author_routine": "Unreleased; reconstructed via candidate search matching published values",
    "discrepancies": "Matrix calculated as mean synaptic weight per possible pair C(i, j) = sum(|W_ij|) / (N_i * N_j) and column-normalized by the maximum of each presynaptic class: C_norm(i, j) = C(i, j) / max_k C(k, j). Numerical values exported to results/figure2f_matrix.csv."
}

# 4. Remove unsupported claim that only interneurons have a continuous wave
data['four_wave_representations_audit']['representation_2_anatomical_interneurons'] = {
    "name": "Anatomically Sorted Interneurons",
    "sorting_principle": "Physical rostrocaudal coordinate N.Position(:, 2)",
    "population": "Right hemicord interneurons (N = 1,609)",
    "finding": "When analyzed in physical anatomical space using Position(:, 2), interneurons do NOT form a continuous smooth wave. Like motoneurons, interneurons exhibit stationary dwell fractions > 98%, low circular-linear correlations (R^2 = 0.123, p = 0.140 at 500 um bins), 36.2% skipped transitions at 500 um bins (71.6% skipped at 250 um bins), and repeated rostral-caudal cluster switching across cycles."
}

# 5. Add complete multi-population exhaustive wave test results
data['exhaustive_anatomical_wave_analysis'] = {
    "summary": "Exhaustive continuity and wave kinematic audit across right/left motoneurons, right/left interneurons, all 8 interneuron classes, 18 motor pools, and 11 spinal segments across 250, 500, and 1000 um bin widths.",
    "populations": all_metrics['populations'],
    "pools": all_metrics['pools'],
    "segments": all_metrics['segments']
}

# 6. Save updated JSON
with open(json_main_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Successfully updated {json_main_path} ({os.path.getsize(json_main_path)} bytes)")
