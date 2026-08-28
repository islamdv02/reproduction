# Figure 4 Reproduction Plan
## Modeled 3D Spatiotemporal Motoneuron Activity in the Lumbosacral Enlargement

### 1. Scientific Purpose
Figure 4 displays the spatiotemporal landscape of motoneuron recruitment across the 30 transverse slices ($L_4 \to S_1$) over two consecutive step cycles ($0\% - 200\%$ step cycle, 200 time bins of $\approx 7\text{ ms}$ each) during forward level locomotion.

### 2. Biological Interpretation
- **Caudal Stance Dominance**: The stance phase is dominated by a massive peak of active motoneurons centered in the caudal enlargement ($L_6 - L_7$, levels 70–85) reaching up to $\approx 204\text{ active MNs/slice}$.
- **Rostral Swing Peak**: The swing phase exhibits a much smaller peak centered rostrally ($L_4 - L_5$, levels 15–35) reaching $\approx 60 - 80\text{ active MNs/slice}$.
- **Phase Transition Dynamics**: Activity shifts rapidly from rostral flexors to caudal extensors at the swing-to-stance transition, with a distinct dwell period in caudal $L_7$ during late stance (retractor activation) before switching back to rostral flexors.

### 3. Implementation Details
- `src/spatiotemporal_model.py`: Matrix multiplication of 30-slice anatomy by 27-muscle EMG timeseries across 2 cycles ($30 \times 200$ grid).
- `src/figure4_analysis.py`: 3D surface plotting routine using matplotlib `mplot3d` with custom viewpoint, color mapping, and swing/stance annotations matching Figure 4.
- `tests/test_figure4.py`: Automated tests verifying grid dimensions ($30 \times 200$), non-negativity, peak location in caudal stance, and surface plot rendering.
- `results/figure4_spatiotemporal_grid.npz`: Exported numerical activity matrix.

### 4. Validation Criteria
- 30 slices $\times$ 200 time bins.
- Peak active MNs per slice reaches $\approx 204\text{ MNs}$.
- Maximum active slice during stance is in caudal cord (slice 22–26, $L_7$).
- Maximum active slice during swing is in rostral cord (slice 5–8, $L_5$).
