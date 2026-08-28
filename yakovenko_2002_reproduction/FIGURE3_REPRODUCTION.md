# Figure 3 Reproduction Report
## EMG Patterns of 27 Hindlimb Muscles During Forward Level Locomotion

**Paper**: Yakovenko et al., *Journal of Neurophysiology* (2002)  
**Figure**: Figure 3 (Normalized 27-Muscle EMG step cycle profiles)  
**Classification**: **[DR] Directly Reproduced** (Piecewise linear waveforms collated from 26 experimental literature studies).

---

### 1. Scientific Overview
Figure 3 defines the activation timings and waveforms for all 27 hindlimb muscles digitized in the anatomical model across the normalized 100-interval locomotor step cycle (swing: $0\% - 30\%$, stance: $30\% - 100\%$, cycle period $\approx 700\text{ ms}$ at $\approx 0.6\text{ m/s}$).

---

### 2. Muscle Functional Grouping & Timing
- **Extensors (14 Muscles)**: Active during stance and late swing ($E_1$ phase, $21\% - 30\%$). Includes ankle plantarflexors (Soleus, MG, LG, Plantaris), knee extensors (VL, VM, VI, RF), and hip extensors (AdFM, BFa, CF, GlutMed, GlutMax, SMa, TP, FHL).
- **Flexors (7 Muscles)**: Active during swing ($0\% - 30\%$). Includes hip flexors (Psoas, Iliacus, SRTa, SRTm), knee flexor (RF swing burst), and ankle dorsiflexors (TA, EDL).
- **Retractors (5 Muscles: BFp, FDL, Gracilis, ST, SMp)**: Biphasic activation peaking at the stance-to-swing transition ($85\% - 100\%$ / $0\% - 10\%$) with a secondary burst in late swing ($20\% - 30\%$).

---

### 3. FDL Dual-Profile Modeling
- **Retractor Profile**: Characterized by an intense burst at the stance-swing boundary ($85\% - 100\%$) acting as a toe flexor for ground clearance.
- **Extensor Profile**: Characterized by stance-phase activity ($30\% - 80\%$) acting as a plantarflexor synergist to FHL.

---

### 4. Generated Artifacts
- Master Plot: [`plots/figure3_emg_profiles.png`](file:///c:/Users/LAB/Documents/GitHub/ibrain/yakovenko_2002_reproduction/plots/figure3_emg_profiles.png)
- Test Suite: [`tests/test_figure3.py`](file:///c:/Users/LAB/Documents/GitHub/ibrain/yakovenko_2002_reproduction/tests/test_figure3.py) (5/5 tests passing).
