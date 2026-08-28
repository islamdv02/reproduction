# Figure 5 Reproduction Plan
## Parametric Sensitivity & Center of Mass Trajectories

### 1. Scientific Purpose
Figure 5 presents plan views (2D spatiotemporal heatmaps) of motoneuron activation over two step cycles across four different recruitment assumptions, with the center of mass of net MN activity ($r_{\text{cm}}(t)$) plotted as open circles at 1% increments ($\Delta t \approx 7\text{ ms}$).

### 2. Four Experimental Conditions
- **Panel 5A (Baseline Graded 100%)**: Graded recruitment reaching $100\%$ maximum in all pools. Demonstrates rapid swing-to-stance migration, stance dwell at levels 70–85, and a distinct caudal detour at the stance-swing transition (arrows a, b, c).
- **Panel 5B (All-or-Nothing Step)**: Binarized EMG step functions (all non-zero EMG = $100\%$). Transitions are more abrupt and subtleties of migration are attenuated, but general rostrocaudal oscillation is preserved.
- **Panel 5C (Physiological Asymmetric Recruitment: 40% Extensor / 15% Flexor)**: Closely mimics real-life moderate walking where extensors are recruited more heavily than flexors. Caudal stance dominance is maintained.
- **Panel 5D (Inverted Recruitment: 15% Extensor / 40% Flexor)**: Reverses the weighting; brief caudal detours at stance-swing transition become exaggerated.

### 3. Quantitative Trajectory Metrics
- **Displacement Range**: Center of mass moves between levels $\approx 28 - 67$ (displacement $\approx 39.5\text{ levels} \approx 11.3\text{ mm}$), covering $\approx 51\%$ of the maximal possible anatomical range ($21.5\text{ mm}$).
- **Peak Migration Velocities**:
  - Swing-to-Stance Transition: $v_{\text{peak}} \approx 217 - 361\text{ mm/s}$.
  - Retraction-to-Swing Transition: $v_{\text{peak}} \approx 309 - 438\text{ mm/s}$.

### 4. Implementation Details
- `src/spatiotemporal_model.py`: Trajectory calculations for `graded`, `step`, `phys_40_15`, and `inv_15_40` modes.
- `src/figure5_analysis.py`: Multi-panel plan view plotting routine with trajectory overlays, arrow annotations, and individualized colorbars matching Figure 5.
- `tests/test_figure5.py`: Automated tests verifying all four modes, trajectory bounds, and velocity peaks.
- `results/figure5_center_of_mass_trajectories.csv`: Exported trajectory timeseries.
