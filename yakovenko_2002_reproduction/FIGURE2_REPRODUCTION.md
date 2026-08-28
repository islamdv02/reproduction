# Figure 2 Reproduction Report
## Motoneuron Distribution Along Rostrocaudal Axis and Table 1 Validation

**Paper**: Yakovenko et al., *Journal of Neurophysiology* (2002)  
**Figure**: Figure 2 (Panels 2A, 2B, 2C) & Table 1  
**Classification**: **[DR] Directly Reproduced** (Grounded in VanderHorst & Holstege 1997 digitized anatomy).

---

### 1. Scientific Overview
Figure 2 plots the number of motoneurons per 0.96-mm transverse slice along the normalized rostrocaudal axis (levels 0–100, 30 slices, $L_4 \to S_1$). It quantitatively demonstrates a profound anatomical asymmetry between the rostral and caudal halves of the lumbosacral enlargement.

---

### 2. Quantitative Verification Against Table 1

| Motoneuron Group | Rostral ($L_4 - L_6$, levels 0–50) | Caudal ($L_7 - S_1$, levels 50–100) | Full Enlargement ($L_4 - S_1$) | Published Match |
| :--- | :---: | :---: | :---: | :---: |
| **Extensor Motoneurons** | **549** ($23\%$) | **1817** ($77\%$) | **2366** | **Exact (100%)** |
| **Retractor Motoneurons (BFp, FDL, Gracilis, SMp, ST)** | **155** ($17\%$) | **752** ($83\%$) | **907** | **Exact (100%)** |
| **Flexor Motoneurons** | **620** ($81\%$) | **141** ($19\%$) | **761** | **Exact (100%)** |
| **All Motoneurons** | **1324** ($33\%$) | **2710** ($67\%$) | **4034** | **Exact (100%)** |

---

### 3. Panel Breakdown
- **Panel 2A (Flexor MNs)**: Concentrated rostrally (levels 0–50) with $81\%$ of all flexors located in $L_4 - L_6$. Peak density at slice 7–8 ($L_5$).
- **Panel 2B (Extensor MNs)**: Concentrated caudally with $77\%$ of extensors in $L_7 - S_1$. Peak density reaches a massive peak of ~260 MNs/slice at level 80 ($L_7$).
- **Panel 2C (Retractor MNs)**: $83\%$ caudal distribution (levels 60–95) with peak density in $L_7$, providing the anatomical substrate for late-stance extensor thrust and swing ground clearance.

---

### 4. Generated Artifacts
- Master Plot: [`plots/figure2_mn_distributions.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/yakovenko_2002_reproduction/plots/figure2_mn_distributions.png)
- Numerical Table: [`results/table1_rostral_caudal_counts.csv`](file:///c:/Users/LAB/Documents/GitHub/ibrain/yakovenko_2002_reproduction/results/table1_rostral_caudal_counts.csv)
- Test Suite: [`tests/test_figure2.py`](file:///c:/Users/LAB/Documents/GitHub/ibrain/yakovenko_2002_reproduction/tests/test_figure2.py) (4/4 tests passing).
