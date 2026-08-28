# Discriminating Biological Experiments
## Experimental Protocols to Test and Discriminate Between Model Y and Model K-Y

---

### 1. The Core Experimental Dilemma

- **Model Y (Yakovenko)** predicts that motoneuron activity is driven by discrete phase-locked drives to spatially segregated pools (half-centers), where the spatial shift of activity is purely a consequence of muscle timing.
- **Model K-Y (Komi)** predicts that an underlying **continuous neurogenic traveling wave of premotor interneuronal spikes** propagates along the spinal cord, driven by an **asymmetric Mexican-hat projectome with zero-sum E/I balance**.

The following four biological experiments could definitively distinguish between these two mechanistic models.

---

### 2. Proposed Experimental Protocols

#### Experiment 1: High-Density Silicon Probe Recordings of Premotor Interneurons in Cat Spinal Cord
- **Method**: Insert multi-shank 32-channel linear silicon probes along the longitudinal axis of the cat lumbar cord ($L_4 \to S_1$) during fictive locomotion (paralyzed, decerebrate, L-DOPA/clonidine-induced).
- **Discriminating Prediction**:
  - *Model Y*: Interneuronal firing should be clustered into two discrete, non-traveling bursts (a flexor burst in $L_4-L_5$ and an extensor burst in $L_7$). No continuous interneuronal wave will exist.
  - *Model K-Y*: Interneuronal unit firing will exhibit a **continuous progressive phase lag $\theta(z)$ along $L_4 \to S_1$**, propagating at $v \approx 20 - 50\text{ mm/s}$ even in the absence of motor movement and sensory feedback.

#### Experiment 2: Targeted Optogenetic Inactivation of Caudal Inhibitory Interneurons
- **Method**: Selectively express ArchT/eNpHR in inhibitory interneurons of caudal segment $L_7$ and illuminate during the stance phase of locomotion.
- **Discriminating Prediction**:
  - *Model Y*: Suppressing $L_7$ inhibition should only affect reciprocal inhibition to local flexors, without altering the spatial propagation of rhythm.
  - *Model K-Y*: Suppressing $L_7$ inhibition destroys the **surround inhibition trough ($\Pi_{\min}$) of the Mexican-hat projectome**, causing runaway excitation in $L_7$ and abolishing the rostral-to-caudal traveling wave propagation.

#### Experiment 3: Acute Focal Lesion (L5/L6 Transection) vs Targeted Axonal Reconnection
- **Method**: Make a focal partial transaction between $L_5$ and $L_6$ (separating rostral and caudal half-centers), then test whether selective optogenetic activation of descending excitatory axons bridges the gap.
- **Discriminating Prediction**:
  - *Model Y*: Lesion isolates two independent unit oscillators with uncoordinated rhythms.
  - *Model K-Y*: Restoring long-range descending excitatory projections across the lesion is sufficient to restore the global rotational limit cycle and traveling wave across the cord.

#### Experiment 4: Multi-Ventral Root Recording in Deafferented Preparations
- **Method**: Record ventral roots from $L_4, L_5, L_6, L_7, S_1$ simultaneously in complete spinal cats with bilateral dorsal rhizotomy (deafferentation).
- **Discriminating Prediction**:
  - *Model Y*: In the absence of sensory feedback, stance-dwell is prolonged or disrupted because muscle timing is lost.
  - *Model K-Y*: The spinal CPG intrinsically preserves the phase lag and directional wave from $L_4$ to $S_1$ via its internal balanced projectome.
