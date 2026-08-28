# Scientific Conflict & Mechanistic Comparison Analysis
## Komi et al. (2026) vs. Yakovenko et al. (2002)

**Authors**: Antigravity AI Advanced Scientific Research Team  
**Date**: August 2026  

---

### 1. The Core Scientific Question

Is there a genuine scientific contradiction between **Komi et al. (2026)** and **Yakovenko et al. (2002)**, or do they represent distinct mechanistic levels and experimental conditions of the mammalian spinal motor system?

---

### 2. Systematic Deconstruction of Claims

| Dimension | Yakovenko et al. (2002) | Komi et al. (2026) | Direct Comparison & Analysis |
| :--- | :--- | :--- | :--- |
| **Primary Scientific Claim** | Lumbosacral motoneuron activity is heavily extensor/caudal biased ($77\%$ in $L_7-S_1$); the center of activity jumps rapidly between rostral flexor ($L_4-L_6$) and caudal extensor ($L_7-S_1$) centers, with an abrupt stance-to-swing transition and a caudal retractor burst. | Symmetrical/asymmetric balanced projectomes with anisotropic axonal projections autonomously generate smooth, continuous, neurogenic rostrocaudal traveling waves and decoupled gain control in spinal circuits. | **Different Levels of Organization**: Yakovenko describes the *kinematic spatial consequence of motor pool layout*, whereas Komi models the *causal recurrent circuit mechanism generating rhythmic waves*. |
| **Biological Quantity Measured / Modeled** | Soma distribution of 27 motoneuron pools (retrograde HRP tracing) multiplied by empirical muscle EMG envelopes ($A(s, t) = \sum N_{m,s} \cdot \text{EMG}_m(t)$). | Firing rates $R_i(t)$ of 9 ventral interneuronal transcriptomic classes (V2a, V1, V0v, V3, etc.) coupled via recurrent synaptic connections. | **Different Cell Types**: Motoneurons (output stage) in Yakovenko vs Premotor Interneurons (rhythm & pattern generation) in Komi. |
| **Definition of "Traveling Wave"** | **Kinematic Activity Migration**: Motion of the weighted center of mass $r_{\text{cm}}(t) = \frac{\sum s \cdot A(s,t)}{\sum A(s,t)}$ across slices, driven by phase-shifted muscle recruitment. | **Dynamical Neurogenic Wave**: Spatially propagating phase crest of neuronal firing rates emerging from asymmetric descending excitation ($\mu_z > 0$) and local inhibition. | **Distinct Wave Concepts**: Yakovenko's wave is an *epiphenomenon of muscle timing*, while Komi's wave is a *neurogenic property of recurrent connectivity*. |
| **Species & Spinal Scale** | Adult Cat (*Felis catus*), Lumbosacral cord $L_4 \to S_1$, total length $= 28.8\text{ mm}$ ($30 \times 0.96\text{ mm}$ slices). | Adult Mouse (*Mus musculus*), Thoracolumbar cord $T_{13} \to S_4$, total length $= 11.0\text{ mm}$ ($20,700$ transcriptomic spots). | **Scale Difference**: Cat cord is $\approx 2.6\times$ longer, with significantly larger motoneuron pool volumes. |
| **Experimental Paradigm** | Intact / decerebrate cats walking on a motorized treadmill (empirical EMG from 26 in vivo literature studies). | Neonatal / adult isolated mouse spinal cord under tonic optogenetic or pharmacological (NMDA/5-HT) drive (fictive locomotion). | **State Difference**: In vivo intact walking with sensory feedback (Yakovenko) vs. Isolated in vitro spinal projectome without sensory feedback (Komi). |
| **Presence of Sensory & Proprioceptive Feedback** | **Yes**: Implicitly captured in the empirical EMG profiles (muscle spindles, Golgi tendon organs, cutaneous load receptors). | **No**: Pure central pattern generator (CPG) intrinsic spinal network dynamics without peripheral sensory feedback loops. | **Critical Distinction**: Sensory load feedback reinforces extensor stance dwell in Yakovenko. |
| **Recurrent Synaptic Connectivity** | **None**: No synaptic matrix $W$ or dynamical differential equations were modeled; purely algebraic feedforward reconstruction. | **Explicit**: Full recurrent matrix $W_{ij}$ with Dale's law, 3D anisotropic kernels, and exact row-wise zero-sum E/I balancing. | **Methodological Difference**: Komi models internal network wiring; Yakovenko does not. |
| **Wave Genesis** | **Reconstructed**: Imposed directly by feeding experimental EMG timing into spatial soma distributions. | **Emergent**: Spontaneously arises from unforced recurrent rate equations $\tau \dot{R}_i = -R_i + f(\sum W_{ij} R_j + I)$. | **Causal Origin**: Prescribed in Yakovenko vs Emergent in Komi. |

---

### 3. Are the Two Papers Contradictory?

**Scientific Verdict**: **No, they are not contradictory. They operate at complementary mechanistic levels.**

1. **The "Apparent Conflict"**:
   - Yakovenko et al. emphasized that the center of motoneuron activity does *not* travel as a slow, continuous wave, but rather *dwells* at caudal levels ($L_7$) during stance ($70\%$ of cycle) and *jumps* rapidly to rostral levels ($L_5$) during swing ($30\%$ of cycle), with a brief caudal detour driven by retractors.
   - Komi et al. emphasized that balanced spatial projectomes generate a continuous traveling wave of interneuronal activity from rostral to caudal cord.
2. **Resolution of the Mechanism**:
   - When Komi's recurrent network is embedded into Yakovenko's cat anatomy ($L_4 \to S_1$) and its emergent activity drives the 27 motoneuron pools, the **continuous neurogenic wave at the interneuronal level** projects onto the **spatially segregated, asymmetric motoneuron pools** ($81\%$ rostral flexors, $77\%$ caudal extensors), naturally producing the **rapid jumps and stance dwell observed by Yakovenko**.
   - Thus, Komi's recurrent projectome provides the **missing generative engine** that explains how Yakovenko's observed motoneuron activity arises without needing to hardcode empirical EMG.
