# Final Mechanistic Conclusion & Synthesis
## Critical Resolution of the Komi et al. (2026) and Yakovenko et al. (2002) Locomotor Models

---

### 1. Final Scientific Classification

### **FINAL VERDICT: B. PARTIAL COMPATIBILITY / COMPLEMENTARY MECHANISTIC LEVELS**

**Evidence-Based Justification**:
1. **No Fundamental Contradiction**: The two studies examine the spinal locomotor system at distinct, mutually reinforcing levels of biological organization:
   - **Yakovenko et al. (2002)** provide the **structural output stage**: a detailed 30-slice somatotopic mapping of 27 motoneuron pools that filters multi-muscle activation into hindlimb motor output.
   - **Komi et al. (2026)** provide the **generative dynamical engine**: a continuous 3D recurrent network governed by asymmetric descending excitation and exact row-wise zero-sum E/I balance that spontaneously generates stable rotational limit cycles, traveling waves, and phase sequences without requiring prescribed EMG.
2. **Quantitative Emergence**:
   - Running the untuned Komi projectome on Yakovenko's cat anatomy spontaneously produces center-of-activity trajectories that correlate strongly with Yakovenko's empirical reference curve (**median $r = 0.750$, max $r = 0.836$, $\text{NRMSE} = 0.372$** across $n=10$ independent random seeds).
   - The emergent network robustly preserves the **asymmetric Mexican-hat projectome ($\text{MHI} = 0.90 \pm 0.32$, Skew $= 1.000$)** and rotational limit cycle stability (**$73.8\% \pm 18.3\%$ planar variance**).
3. **Identified Differences & Remaining Open Questions**:
   - *Stance Duration Asymmetry*: In live walking cats, sensory load feedback ($Ia, Ib$) prolongs extensor stance duration to $70\%$ of the cycle. In the isolated intrinsic CPG model, stance and swing are more symmetrically distributed ($\sim 50\%$). Integrating peripheral afferent feedback into Model K-Y represents the key future bridge.
   - *Wave Velocity Scale*: The continuous interneuronal phase wave propagates at $v_{\text{wave}} \approx 77 - 113\text{ mm/s}$ in cat cord, which mathematically drives the rapid kinematic centroid migration jumps ($v_{\text{mig}} \approx 385 - 414\text{ mm/s}$) at the motoneuron level.

---

### 2. Multi-Level Locomotor Architecture

```text
========================================================================================
                             MAMMALIAN SPINAL LOCOMOTOR ARCHITECTURE
========================================================================================

 [LEVEL 1: PREMOTOR CPG PROJECTOME] (Komi et al. 2026)
   - Ventral Interneurons (V2a, V1, V0v, V0d, V3) in continuous 3D coordinates
   - Anisotropic Gaussian axonal kernels: Descending Excitation (mu_z=+3.5mm, sigma_z=6mm)
                                          Local Inhibition (mu_z=-1.2mm, sigma_z=2.5mm)
   - Exact row-wise zero-sum E/I balancing (sum_j W_ij = 0.0 +- 1e-15)
   - Generative Output: Continuous Traveling Phase Wave phi(z) & Rotational Limit Cycle
                                     |
                                     v
 [LEVEL 2: MOTONEURON POOL SOMATOTOPY] (Yakovenko et al. 2002)
   - 27 Anatomical Motoneuron Pools distributed non-uniformly across 30 slices (L4 -> S1)
   - Structural polarization: 81% flexors rostral (L4-L6), 77% extensors caudal (L7-S1)
   - Spatial filtering converts continuous phase wave into discrete phase-locked motor bursts
                                     |
                                     v
 [LEVEL 3: PERIPHERAL EFFECTOR & SENSORY REINFORCEMENT] (Classical Physiology)
   - Multi-joint hindlimb musculoskeletal biomechanics
   - Afferent feedback (muscle spindles, Golgi tendon organs) prolongs stance dwell to 70%
========================================================================================
```

---

### 3. Concrete Discriminating Biological Predictions

1. **Silicon Probe Recording in Cat**:
   - *Prediction*: Linear 32-channel silicon probes inserted along $L_4 \to S_1$ in paralyzed, deafferented fictive cats will record a **continuous linear phase lag $\theta(z)$ in premotor interneurons**, directly confirming the Komi traveling wave in the absence of movement.
2. **Optogenetic Inhibition of Caudal Surround**:
   - *Prediction*: Selectively silencing $L_7$ inhibitory interneurons will destroy the surround trough of the Mexican-hat projectome ($\text{MHI} \to 0$), causing runaway excitation and abolishing traveling wave coordination.
3. **Decoupled Gain Control**:
   - *Prediction*: Optogenetic stimulation of long-range descending excitatory pathways will selectively scale motor burst amplitude (force) without altering stepping frequency.
