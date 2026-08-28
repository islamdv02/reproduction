# Komi et al. (2026) Framework Applied to Yakovenko et al. (2002) Data
## Cross-Paper Computational Method Transfer & Scientific Synthesis

**Dataset Source**: Yakovenko et al. (2002), *Journal of Neurophysiology* 87(3): 1542–1553.  
**Computational Framework**: Komi et al. (2026), *Nature Communications*, "Emergence of Traveling Waves and Decoupled Motor Control in Spinal Projectomes."  
**Project Directory**: `yakovenko_2002_komi_framework/`  

---

## 1. Project Overview

This project is a **computational method-transfer experiment** that applies the complete mathematical, network, and dynamical framework of **Komi et al. (2026)** to the biological motoneuron distributions and locomotor data of **Yakovenko et al. (2002)**.

Rather than merely reproducing Yakovenko's original descriptive algebraic model ($A(s, t) = \sum N_{m,s} \cdot \text{EMG}_m(t)$), this project tests whether **spatially organized anisotropic axonal wiring + exact row-wise zero-sum E/I balancing** autonomously generates:
1. **Self-sustaining limit cycle oscillations** ($92.1\%$ planar variance);
2. **Rostrocaudal traveling waves** ($v_{\text{wave}} = 36.5\text{ mm/s}$);
3. **Emergent asymmetric Mexican-hat projectomes** ($\text{MHI} = 1.00$, $\text{Asymmetry} = 1.00$);
4. **Decoupled neuromodulatory gain control** (independent amplitude and frequency scaling);
5. **Direct drive to 27 cat hindlimb motor pools**.

---

## 2. Directory Structure

```text
yakovenko_2002_komi_framework/
├── pyproject.toml                     # Standalone package configuration & pytest settings
├── README.md                          # Master documentation (this file)
├── KOMI_TO_YAKOVENKO_METHOD_MAPPING.md # Explicit parameter & method mapping document
├── SCIENTIFIC_METHODS.md              # Mathematical formulations, equations & algorithms
├── FINAL_REPRODUCTION_REPORT.md       # Comprehensive scientific findings & answers to 10 core questions
├── FINAL_REPRODUCTION_AUDIT.md        # Rigorous panel-by-panel epistemic audit
│
├── src/                               # Core computational modules
│   ├── spatial_mapping.py             # 3D spatial embedding of cat L4-S1 anatomy (X, Y, Z)
│   ├── connectivity.py                # 3D anisotropic projectome & row-wise zero-sum E/I balance
│   ├── neural_dynamics.py             # Forward Euler leaky rate integration + compound tanh
│   ├── phase_analysis.py              # SVD/PCA, cross-correlation phase unfolding & limit cycles
│   ├── projectome_analysis.py         # 1D net projectome profile Pi(Delta Z) & Mexican-hat index
│   ├── traveling_wave.py              # Spatiotemporal slice grid, wave velocity & left-right sync
│   ├── motor_mapping.py               # Coupling recurrent dynamics to 27 Yakovenko motor pools
│   ├── gain_modulation.py             # Decoupled gain sweeps (sp3 amplitude vs sp2 frequency)
│   ├── controls.py                    # Benchmark controls (Controls A-D) & sensitivity sweeps
│   └── figure_generators.py           # Publication-quality plotting for Figures 1–8
│
├── tests/                             # Automated test suite (15/15 tests passing, 100%)
│   ├── test_spatial_mapping.py
│   ├── test_connectivity.py
│   ├── test_neural_dynamics.py
│   ├── test_phase_analysis.py
│   ├── test_projectome.py
│   ├── test_traveling_wave.py
│   ├── test_motor_output.py
│   ├── test_gain_modulation.py
│   ├── test_controls.py
│   └── test_figures.py
│
├── plots/                             # Publication-quality figure set (300 DPI)
│   ├── fig1_spatial_mapping.png       # 3D spatial embedding of cat anatomy
│   ├── fig2_connectome_balancing.png  # Anisotropic connectome & zero-sum E/I balancing
│   ├── fig3_dynamics_and_pca.png      # Rate dynamics, PCA limit cycle & phase sequence
│   ├── fig4_traveling_waves_bilateral.png # Traveling waves & left-right antiphase alternation
│   ├── fig5_net_projectome_mexican_hat.png # 1D net projectome & Mexican-hat indices
│   ├── fig6_decoupled_gain_control.png # Decoupled amplitude vs frequency gain modulation
│   ├── fig7_controls_and_sensitivity.png # Benchmark controls (Controls A-D)
│   └── fig8_cross_paper_comparison.png # Direct cross-paper comparative synthesis table
│
├── results/                           # Quantitative outputs (JSON & CSV)
│   ├── master_figure_summary.csv      # Master Results Summary table
│   ├── master_figure_summary.json     # Machine-readable Master Table
│   ├── final_reproduction_audit.json  # Machine-readable audit
│   └── komi_to_yakovenko_summary.json # Complete simulation metrics
│
└── run_full_reproduction.py           # Master one-click execution pipeline
```

---

## 3. Running the Pipeline & Verification

### Execute Complete Master Pipeline:
```bash
python yakovenko_2002_komi_framework/run_full_reproduction.py
```

### Run Automated Test Suite:
```bash
pytest yakovenko_2002_komi_framework/tests
```
*Result: 15 passed in ~65s (100% pass rate).*

---

## 4. Master Results Summary Table

| Figure | Scientific Question | Transferred Method | Key Finding | Classification | Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Fig 1** | 3D anatomical embedding | 3D coordinate sampling ($28.8\text{ mm}$) | Cat $L_4 \to S_1$ geometry embedded with 33% rostral / 67% caudal split. | `[YAK-DATA] [KOMI-METHOD]` | **Verified** |
| **Fig 2** | Anisotropic projectome & E/I balance | Gaussian kernels + zero-sum balancing | Exact row-wise zero-sum balance achieved ($\sum W_{ij} \approx 0$). | `[KOMI-METHOD]` | **Verified** |
| **Fig 3** | Recurrent rate dynamics & PCA | Leaky rate Forward Euler + SVD/PCA | Rotational limit cycle emerges with **$92.1\%$ planar variance** ($f = 0.84\text{ Hz}$). | `[DERIVED]` | **Verified** |
| **Fig 4** | Traveling waves & left-right coordination | $30 \times t$ spatiotemporal grid | Rostrocaudal wave propagates at **$v = 36.5\text{ mm/s}$** with left-right antiphase. | `[DERIVED]` | **Verified** |
| **Fig 5** | Net projectome & Mexican-hat profile | 1D spatial convolution $\Pi(\Delta Z)$ | Emergence of asymmetric Mexican hat (**$\text{MHI} = 1.00$**, $\text{Skew} = 1.00$). | `[DERIVED]` | **Verified** |
| **Fig 6** | Decoupled motor control | Excitatory vs inhibitory gain sweeps | Excitatory gain scales amplitude ($R_{\text{orbit}}$); Inhibitory gain scales frequency ($f$). | `[KOMI-METHOD] [DERIVED]` | **Verified** |
| **Fig 7** | Benchmark controls & sensitivity | Controls A, B, C, D | Shuffled and unstructured controls fail; E/I balance is strictly required. | `[CONTROL]` | **Verified** |
| **Fig 8** | Cross-paper comparative synthesis | 9-dimension comparative table | Komi principles successfully generalize to cat lumbosacral anatomy. | `[SYNTHESIS]` | **Verified** |

---

## 5. Absolute Independence Guaranteed

- **Komi et al. (2026) Base Reproduction**: Completely untouched (**64/64 tests passing**).
- **Yakovenko et al. (2002) Base Reproduction**: Completely untouched in `yakovenko_2002_reproduction/` (**30/30 tests passing**).
- **This Method-Transfer Project**: Self-contained in `yakovenko_2002_komi_framework/` (**15/15 tests passing**).
