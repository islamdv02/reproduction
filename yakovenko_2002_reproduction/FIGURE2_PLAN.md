# Figure 2 Reproduction Plan
## Motoneuron Distribution Along the Rostrocaudal Axis of the Cat Lumbosacral Spinal Cord

### 1. Scientific Purpose
Figure 2 quantitatively plots the number of motoneurons digitized per slice (30 slices across $L_4 \to S_1$) for:
- **Panel 2A**: Flexor motoneurons (levels 0–50, rostral focus).
- **Panel 2B**: Extensor motoneurons (levels 50–100, peak in $L_7$ at level ~80; with and without FDL).
- **Panel 2C**: Retractor motoneurons (BFp, Gracilis, SMp, ST; with and without FDL).
- **Total Motoneuron Distribution** (dashed curve in all panels): Demonstrating the severe anatomical imbalance between rostral ($33\%$) and caudal ($67\%$) halves.

### 2. Table 1 Quantitative Grounding
- **Extensor Motoneurons**: Rostral 549 ($23\%$), Caudal 1817 ($77\%$), Total 2366.
- **Retractor Motoneurons (BFp, FDL, Gracilis, SMp, ST)**: Rostral 155 ($17\%$), Caudal 752 ($83\%$), Total 907.
- **Flexor Motoneurons**: Rostral 620 ($81\%$), Caudal 141 ($19\%$), Total 761.
- **All Motoneurons**: Rostral 1324 ($33\%$), Caudal 2710 ($67\%$), Total 4034.

### 3. Implementation Details
- `src/figure2_analysis.py`: Functions to compute slice-wise distributions, plot individual panels 2A, 2B, 2C, and assemble the composite publication figure matching Figure 2.
- `tests/test_figure2.py`: Automated tests verifying slice sums, peak locations, and Table 1 exact counts.
- `results/table1_rostral_caudal_counts.csv`: Exported Table 1 data.

### 4. Validation Criteria
- Total MN count equals 4034 across all 30 slices.
- 81% of flexors in rostral half ($L_4 - L_6$).
- 77% of extensors in caudal half ($L_7 - S_1$) with peak at slice 24–25 (level ~80).
- 83% of retractors in caudal half.
