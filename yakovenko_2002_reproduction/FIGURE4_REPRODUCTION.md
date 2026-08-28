# Figure 4 Reproduction Report
## Modeled 3D Spatiotemporal Motoneuron Activity During Locomotion

**Paper**: Yakovenko et al., *Journal of Neurophysiology* (2002)  
**Figure**: Figure 4 (3D Spatiotemporal activity landscape over 2 step cycles)  
**Classification**: **[MD] Model-Derived** (Spatiotemporal landscape emerging from integrating 30-slice anatomy with 27-muscle EMG).

---

### 1. Scientific Overview
Figure 4 displays the modeled activation patterns of motoneurons across the 30 transverse slices ($L_4 \to S_1$) during two full step cycles ($200$ time bins, $\Delta t \approx 7\text{ ms}$, cycle period $700\text{ ms}$).

---

### 2. Spatiotemporal Characteristics
- **Caudal Stance Dominance**: Peak active motoneuron density reaches $\approx 204\text{ MNs/slice}$ in the caudal half of the enlargement ($L_6 - L_7$, levels 70–85) during stance phase.
- **Rostral Swing Activity**: During swing phase, a smaller focal activation emerges in rostral slices ($L_4 - L_5$, levels 15–35) reaching $\approx 60 - 80\text{ MNs/slice}$.
- **Abrupt Phase Transitions**: The migration of activity from swing to stance occurs rapidly, jumping across the enlargement.
- **Late-Stance Retractor Peak**: A distinct peak forms in caudal $L_7$ at the stance-to-swing transition, corresponding to the activation of BFp, Gracilis, ST, SMp, and FDL retractor pools.

---

### 3. Generated Artifacts
- Master Plot: [`plots/figure4_spatiotemporal_activity.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/yakovenko_2002_reproduction/plots/figure4_spatiotemporal_activity.png)
- Grid Dataset: [`results/figure4_spatiotemporal_grid.npz`](file:///c:/Users/LAB/Documents/GitHub/ibrain/yakovenko_2002_reproduction/results/figure4_spatiotemporal_grid.npz)
- Test Suite: [`tests/test_figure4.py`](file:///c:/Users/LAB/Documents/GitHub/ibrain/yakovenko_2002_reproduction/tests/test_figure4.py) (4/4 tests passing).
