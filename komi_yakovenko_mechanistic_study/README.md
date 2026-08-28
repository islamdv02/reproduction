# Critical Scientific Validation & Mechanistic Study: Komi et al. (2026) vs. Yakovenko et al. (2002)

**Project Location**: `komi_yakovenko_mechanistic_study/`  
**Authors**: Antigravity AI Advanced Scientific Research Team  
**Date**: August 2026  

---

## 1. Executive Summary & Verdict

- **Central Scientific Question**: Does a Komi-style spatially organized recurrent spinal network, constrained by the anatomical and locomotor information from Yakovenko et al. (2002), generate the spatiotemporal activity pattern observed by Yakovenko?
- **Final Classification**: **B. PARTIAL COMPATIBILITY / COMPLEMENTARY MECHANISTIC LEVELS**.
- **Key Finding**: The two papers operate at complementary mechanistic levels:
  - **Yakovenko et al. (2002)** characterize the **feedforward motoneuron output somatotopy** given empirical muscle timing.
  - **Komi et al. (2026)** model the **generative recurrent projectome dynamics** that autonomously produce the underlying rhythm and traveling wave.
- **Quantitative Match**: Untuned Model K-Y center-of-activity trajectory correlates strongly with Yakovenko's reference (**median $r = 0.750$, max $r = 0.836$, $\text{NRMSE} = 0.372$** across $n=10$ random seeds).

---

## 2. Directory Structure

```text
komi_yakovenko_mechanistic_study/
├── pyproject.toml                         # Configuration & pytest settings
├── README.md                              # Master overview (this file)
│
├── Documentation Package:
│   ├── CRITICAL_SCIENTIFIC_VALIDATION.md  # Comprehensive skeptical scientific validation report
│   ├── PARAMETER_PROVENANCE.md            # Complete parameter grounding & sensitivity table
│   ├── ABLATION_AND_CONTROLS.md           # 11 systematic ablation conditions (A through K)
│   ├── WAVE_DEFINITION_ANALYSIS.md        # Mathematical dissection of 5 wave objects & velocity
│   ├── FINAL_MECHANISTIC_CONCLUSION.md    # Multi-level synthesis & discriminating predictions
│   ├── SCIENTIFIC_CONFLICT_ANALYSIS.md    # Deconstruction of claims & experimental paradigms
│   ├── MODEL_Y_VS_MODEL_KY.md             # Mathematical formulations: Feedforward vs Recurrent
│   ├── DISCRIMINATING_EXPERIMENTS.md      # 4 concrete biological experimental protocols
│   └── TRANSFER_PROVENANCE.md             # Initial parameter trace
│
├── src/                                   # Computational engine
│   ├── model_y.py                         # Model Y (Yakovenko feedforward kinematic model)
│   ├── model_ky.py                        # Model K-Y (Komi recurrent projectome on cat anatomy)
│   ├── ablation_experiments.py            # 11 Systematic ablation conditions (A through K)
│   ├── parameter_sensitivity_suite.py     # Parameter sweeps (mu_z, sigma_z, tau, I_tonic, comm)
│   ├── critical_monte_carlo.py            # 10-seed Monte Carlo evaluator with 95% CIs
│   ├── wave_comparative_math.py           # Mathematical comparison of 5 wave entities
│   ├── parameter_provenance_builder.py    # Parameter provenance table builder
│   ├── wave_decomposition.py              # Wave A vs Wave B vs Wave C analyzer
│   ├── controls_suite.py                  # 8 Controlled experiments runner
│   ├── mechanistic_comparator.py          # Multi-seed comparator
│   ├── figure_plotting.py                 # Figures 1-8 plotting module
│   └── critical_figures.py                # Publication Figures 1-10 generator
│
├── tests/                                 # Automated test suite (8/8 tests passing, 100%)
│   ├── test_model_y.py
│   ├── test_model_ky.py
│   ├── test_wave_decomposition.py
│   ├── test_controls_suite.py
│   ├── test_mechanistic_comparator.py
│   └── test_figures.py
│
├── plots/                                 # 10 Publication-Quality Figures (300 DPI)
│   ├── figure1_yakovenko_reference.png            # Motoneuron somatotopy & empirical EMG
│   ├── figure2_komi_derived_network.png           # 3D spatial network & zero-sum E/I balance
│   ├── figure3_recurrent_activity.png             # Recurrent rates & rotational limit cycle
│   ├── figure4_direct_overlay.png                 # Spatiotemporal landscape side-by-side
│   ├── figure5_center_of_activity_and_velocity.png# r_cm(t) overlay & migration velocities
│   ├── figure6_traveling_wave_vs_migration.png    # Continuous phase wave vs centroid migration
│   ├── figure7_ablations_and_controls.png         # 11 ablation benchmark comparisons
│   ├── figure8_parameter_sensitivity.png          # Sweeps across 5 transferred dimensions
│   ├── figure9_wave_definition_comparison.png     # Mathematical taxonomy of 5 wave objects
│   └── figure10_mechanistic_synthesis.png         # Multi-level mammalian architecture table
│
├── results/                               # Machine-Readable Data Outputs (CSV & JSON)
│   ├── critical_validation_metrics.csv    # 10-seed Monte Carlo dataset
│   ├── critical_validation_metrics.json   # Mean, SD, Median, Min, Max, 95% CIs
│   ├── parameter_provenance.csv           # Complete parameter provenance table
│   ├── ablation_results.csv               # 11 ablation condition benchmark results
│   ├── parameter_sensitivity.csv          # Parameter sensitivity sweep dataset
│   ├── wave_definition_comparison.csv     # 5 wave entities comparison table
│   └── comparison_metrics.csv / .json     # Initial comparison datasets
│
├── run_critical_validation.py             # Master runner executing full critical pipeline
└── run_mechanistic_study.py               # Master runner for initial mechanistic study
```

---

## 3. Reproduction & Execution Instructions

### Execute Full Critical Validation Pipeline (Regenerates all CSVs, JSONs, and Figures 1–10):
```bash
python komi_yakovenko_mechanistic_study/run_critical_validation.py
```

### Run Full Test Suite:
```bash
pytest komi_yakovenko_mechanistic_study/tests
```
*Status: 8 passed in ~62s (100% pass rate).*
