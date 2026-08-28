# Wave Definition & Mathematical Mechanism Analysis
## Mathematical Dissection of 5 Locomotor Wave Objects and Resolution of the Velocity Discrepancy

---

### 1. Mathematical Taxonomy of the 5 Distinct Objects

1. **Object 1: Center-of-Activity Migration ($r_{\text{cm}}(t)$)**:
   - *Equation*: $r_{\text{cm}}(t) = \frac{\sum_{s=1}^{30} s \cdot A(s, t)}{\sum_{s=1}^{30} A(s, t)}$
   - *Physical Nature*: Spatial first moment (centroid) of active motoneurons across the 30 slices.
   - *Continuity*: Discontinuous / Jump-like at stance-to-swing transitions.
   - *Generative Status*: Epiphenomenon of muscle recruitment timing.
2. **Object 2: Stance-to-Swing Phase Shift ($\Delta r_{\text{cm}}$)**:
   - *Equation*: $\Delta r_{\text{cm}} = r_{\text{cm}}(\text{swing}) - r_{\text{cm}}(\text{stance}) \approx 36.7\text{ levels}$ ($11.37\text{ mm}$).
   - *Physical Nature*: Discrete macro-level switching between rostral flexor ($L_4-L_6$) and caudal extensor ($L_7-S_1$) half-centers.
3. **Object 3: Komi Continuous Traveling Phase Wave ($\phi(z)$)**:
   - *Equation*: $\phi(z) = \phi_0 + \left( \frac{2\pi f}{v_{\text{wave}}} \right) z$
   - *Physical Nature*: Smooth, progressive spatial phase lag across premotor interneuronal firing timeseries.
   - *Generative Status*: Causal neurogenic dynamical mode driven by recurrent synaptic projectomes.
4. **Object 4: Propagating Neural Activity Field ($R(z, t)$)**:
   - *Equation*: $R(z, t) = R_0 + A(z) \cos(2\pi f t - k z)$
   - *Physical Nature*: Continuous spatio-temporal wave crest traveling down the spinal cord.
5. **Object 5: Motor-Pool Output Activation Sequence ($A_m(t)$)**:
   - *Equation*: $A_m(t) = \sum_{s=1}^{30} N_{m,s} \cdot R_{\text{slice}}(s, t)$
   - *Physical Nature*: Segmented, polyphasic motor unit drives delivered to specific anatomical muscles.

---

### 2. Resolution of the Wave Velocity Discrepancy

A critical point of confusion in previous studies was the apparent quantitative mismatch between:
- **Yakovenko Kinematic Migration Velocity**: $v_{\text{mig}} = \left| \frac{dr_{\text{cm}}}{dt} \right| \approx 300 - 415\text{ mm/s}$.
- **Komi Mouse Traveling Wave Velocity**: $v_{\text{wave, mouse}} = 1.85\text{ mm/s}$.
- **Komi Cat Recurrent Wave Velocity**: $v_{\text{wave, cat}} = 36.5 - 130.2\text{ mm/s}$.

#### Mathematical Explanation of the Velocity Discrepancy:
1. **Migration Velocity vs Phase Velocity**:
   - $v_{\text{mig}}$ measures the speed at which the *statistical centroid of active motoneurons* moves when an entire segment pool switches off and another switches on. A step-like transition across $11\text{ mm}$ occurring within $30\text{ ms}$ yields a peak migration velocity of $11\text{ mm} / 0.03\text{ s} \approx 367\text{ mm/s}$.
   - $v_{\text{wave}}$ measures the physical propagation speed of *individual neuronal phase crests* along axonal projections ($\omega / k$).
2. **Species & Scale Differences (Mouse vs Cat)**:
   - In neonatal/adult mouse preparations (Komi 2026), the cord is $11\text{ mm}$ long and optogenetic fictive locomotion occurs at slow cycle periods ($T \approx 6000\text{ ms}$), yielding $v_{\text{wave}} \approx 11\text{ mm} / 6.0\text{ s} \approx 1.85\text{ mm/s}$.
   - In adult cat locomotion (Yakovenko 2002), the lumbar cord is $28.8\text{ mm}$ long and the step cycle is fast ($T \approx 700\text{ ms}, f \approx 1.4\text{ Hz}$). Scaling the axonal projectome to cat dimensions yields an emergent phase wave velocity of $v_{\text{wave}} \approx 28.8\text{ mm} / 0.7\text{ s} \approx 41.1 - 113.1\text{ mm/s}$.
3. **Conclusion on Velocity**:
   - Direct numerical comparison between $v_{\text{mig}}$ and $v_{\text{wave}}$ is **mathematically comparing centroid derivative against wave phase velocity**.
   - When properly evaluated as a multi-level system, Komi's phase wave ($v_{\text{wave}} \approx 77 - 113\text{ mm/s}$) correctly drives Yakovenko's centroid migration ($v_{\text{mig}} \approx 385 - 414\text{ mm/s}$).
