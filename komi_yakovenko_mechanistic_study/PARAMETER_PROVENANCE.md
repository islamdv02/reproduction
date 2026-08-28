# Parameter Provenance Audit
## Exhaustive Parameter Grounding, Transfer Rationale, and Sensitivity

---

### 1. Complete Parameter Provenance Table

| Parameter | Komi (2026) Value | Yakovenko (2002) Value | Transferred Value | Literature Source | Transfer Rationale | Measured? | Assumed? | Fitted? | Sensitivity |
| :--- | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **Spinal Length ($L_{\text{cord}}$)** | $11.0\text{ mm}$ (Mouse T13-S4) | $28.8\text{ mm}$ (Cat L4-S1) | $28.8\text{ mm}$ | Yakovenko Table 1 | Cat anatomical cord extent | **Yes** | No | No | Linear scale |
| **Hemicord Width ($w_{\text{cord}}$)** | $1.2\text{ mm}$ | $3.6\text{ mm}$ | $3.6\text{ mm}$ | Yakovenko Methods | Cat transverse dimensions | **Yes** | No | No | Low |
| **Dorsoventral Height ($h_{\text{cord}}$)** | $1.5\text{ mm}$ | $5.5\text{ mm}$ | $5.5\text{ mm}$ | Yakovenko Methods | Cat transverse dimensions | **Yes** | Ventral horn: 1.2-4.2 mm | No | Low |
| **Motoneuron Count & Map ($N_{m,s}$)** | 35 Generic pools | 27 Cat hindlimb pools (4034 MNs) | 27 Cat hindlimb pools (4034 MNs) | VanderHorst & Holstege 1997 | Cat motoneuron output somatotopy | **Yes** | No | No | High |
| **Excitatory Reach ($\sigma_{z, \text{exc}}$)** | $1.8\text{ mm}$ | Not measured | $6.0\text{ mm}$ | Scaled to cat cord | Spans 6-8 slices (~2 segments) | No | **Yes** | No | Moderate |
| **Inhibitory Reach ($\sigma_{z, \text{inh}}$)** | $0.8\text{ mm}$ | Not measured | $2.5\text{ mm}$ | Scaled to cat cord | Local inhibition within 2-3 slices | No | **Yes** | No | High |
| **Descending Bias ($\mu_{z, \text{exc}}$)** | $+1.2\text{ mm}$ | Not measured | $+3.5\text{ mm}$ | Scaled to cat cord | Breaks symmetry for rostrocaudal wave | No | **Yes** | No | High |
| **Time Constant ($\tau$)** | $20.0\text{ ms}$ | Not modeled | $20.0\text{ ms}$ | Komi Dynamics/Simulate.m | Standard biophysical rate integration | No | **Yes** | No | Moderate |
| **Tonic Somatic Drive ($I^{\text{tonic}}$)** | $15.0\text{ pA}$ | Not modeled | $15.0\text{ pA}$ | Komi Dynamics/Simulate.m | Unpatterned somatic driving current | No | **Yes** | No | Low (10-30 pA) |
| **Firing Saturation ($f_{\max}, T$)** | $100\text{ Hz}, 0\text{ pA}$ | Not modeled | $100\text{ Hz}, 0\text{ pA}$ | Komi Compound Tanh | Standard rate non-linearity | No | **Yes** | No | Low |
| **Commissural Fraction** | $15\%$ of network | Not measured | $15\%$ of network | V0v/V0d literature | Cross-cord contralateral inhibition | No | **Yes** | No | High for L/R |
| **Commissural E/I Ratio** | 60:40 | Not measured | 60:40 | V0v/V0d literature | Mammalian commissural electrophysiology | No | **Yes** | No | Moderate |
| **Spectral Radius ($g_{\text{spec}}$)** | $1.25$ | Not modeled | $1.25$ | BergLab RescaleConnectivity.m | Stabilizes rotational limit cycle | No | **Yes** | No | High |

---

### 2. Critical Audit of Newly Introduced Assumptions

1. **Interneuron Functional Abstraction**:
   - *Status*: `NEW-ASSUMPTION`.
   - *Rationale*: Yakovenko et al. (2002) reconstructed motoneuron activity but did not measure premotor interneurons. To apply Komi's recurrent equations, we placed functional populations (RFlex-E/I, CExt-E/I, CRet-E/I, Comm-Contra) co-localized with their respective motor pools.
2. **Axonal Reach Scaling ($\sigma_z = 6.0\text{ mm}$ vs $1.8\text{ mm}$)**:
   - *Status*: `NEW-ASSUMPTION`.
   - *Rationale*: The cat lumbar cord ($28.8\text{ mm}$) is $2.6\times$ longer than the mouse thoracolumbar cord ($11.0\text{ mm}$). Axonal length constants were scaled proportionally to span equivalent segment distances.
3. **Zero Parameter Fitting Against Target Trajectory**:
   - *Verification*: No parameter was optimized or fitted against Yakovenko's center-of-activity curve $r_{\text{cm}}(t)$. All parameters were set prior to simulation.
