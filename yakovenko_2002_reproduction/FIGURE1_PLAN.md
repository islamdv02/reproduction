# Figure 1 Reproduction Plan
## Anatomical Organization of Lumbosacral Motoneuron Pools

### 1. Scientific Purpose
Figure 1 presents the 3D anatomical models of motoneuron (MN) pools in the cat lumbar enlargement ($L_4 \to S_1$, $28.8\text{ mm}$ length, normalized to 100 levels / 30 slices) reconstructed from 30 summary drawings in VanderHorst & Holstege (1997). The pools are partitioned into muscles acting across the **Hip**, **Knee**, and **Ankle**.

### 2. Biological Interpretation
- **Fusiform, Intertwined Architecture**: Lumbosacral motoneuron pools are long, column-shaped, and overlapping in the ventral horn.
- **Rostrocaudal Distribution Gradient**:
  - Hip flexors (Psoas, Sartorius, Iliacus) are rostral ($L_4 - L_5$, levels 0–30), while hip extensors (SMa, BFa, GlutMed, GlutMax) are caudal ($L_6 - L_7$, levels 50–90).
  - Knee extensors (VL, VM, VI, RF) are rostral ($L_5 - L_6$, levels 20–50), while knee flexors (BFp, ST, SMp) are caudal ($L_7 - S_1$, levels 60–95).
  - Ankle flexors (TA, EDL) are in mid-enlargement ($L_6$, levels 45–65), while ankle extensors (Soleus, MG, LG, Plantaris, FHL, TP) are in caudal enlargement ($L_7$, levels 65–90).
- **Unit Oscillator Separation**:
  - Hip half-centers separated by ~61 levels ($17.5\text{ mm}$).
  - Knee half-centers separated by ~58 levels ($16.7\text{ mm}$).
  - Ankle half-centers separated by ~20 levels ($5.6\text{ mm}$).

### 3. Panel Breakdown
- **Fig 1 Left (Hip Pools)**: Schematic bars showing rostrocaudal extent, centers of mass, and 3D ventral horn reconstruction for Psoas, SRTm, SRTa, Iliacus, RF, Gracilis, AdFM, SMa, SMp, GlutMed, ST, CF, BFa, GlutMax, BFp.
- **Fig 1 Middle (Knee Pools)**: Schematic bars, centers of mass, and 3D reconstruction for SRTm, VM, VL, RF, VI, SMp, ST, BFp, Gracilis.
- **Fig 1 Right (Ankle Pools)**: Schematic bars, centers of mass, and 3D reconstruction for EDL, FDL, TA, FHL, TP, Plantaris, Soleus, LG, MG.

### 4. Mathematical Equations & Metrics
$$\text{Center of Mass: } z_{\text{cm}, m} = \frac{\sum_{s=1}^{30} z_s \cdot N_{m, s}}{\sum_{s=1}^{30} N_{m, s}}$$
where $z_s$ is slice position in normalized levels ($0 - 100$) or physical millimeters ($0 - 28.8\text{ mm}$).

### 5. Validation Criteria
- All 27 pools accurately mapped with correct centers of mass ($Psoas \approx 15.0$, $BFp \approx 89.6$).
- Unit oscillator separations match the published values (Hip $\approx 61$ levels, Knee $\approx 58$ levels, Ankle $\approx 20$ levels).
