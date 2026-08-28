"""
Unit tests for Figure 2 and Table 1 of Yakovenko et al. (2002).
Verifies exact Table 1 motoneuron counts, percentages, and slice distributions for Panels 2A, 2B, 2C.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from anatomy import CatLumbosacralAnatomy
from figure2_analysis import compute_figure2_distributions, generate_figure2_complete, export_table1_csv


def test_table1_exact_counts_and_percentages():
    """Verify Table 1 values exactly match published table in Yakovenko et al. (2002)."""
    anat = CatLumbosacralAnatomy()
    t1 = anat.get_table1_counts(fdl_as_retractor=True)

    # Extensor MNs: Rostral 549 (23%), Caudal 1817 (77%), Total 2366
    assert t1['extensor']['rostral'] == 549
    assert t1['extensor']['caudal'] == 1817
    assert t1['extensor']['total'] == 2366
    assert round(t1['extensor']['rostral'] / t1['extensor']['total'] * 100) == 23
    assert round(t1['extensor']['caudal'] / t1['extensor']['total'] * 100) == 77

    # Retractor MNs: Rostral 155 (17%), Caudal 752 (83%), Total 907
    assert t1['retractor']['rostral'] == 155
    assert t1['retractor']['caudal'] == 752
    assert t1['retractor']['total'] == 907
    assert round(t1['retractor']['rostral'] / t1['retractor']['total'] * 100) == 17
    assert round(t1['retractor']['caudal'] / t1['retractor']['total'] * 100) == 83

    # Flexor MNs: Rostral 620 (81%), Caudal 141 (19%), Total 761
    assert t1['flexor']['rostral'] == 620
    assert t1['flexor']['caudal'] == 141
    assert t1['flexor']['total'] == 761
    assert round(t1['flexor']['rostral'] / t1['flexor']['total'] * 100) == 81
    assert round(t1['flexor']['caudal'] / t1['flexor']['total'] * 100) == 19

    # All MNs: Rostral 1324 (33%), Caudal 2710 (67%), Total 4034
    assert t1['all']['rostral'] == 1324
    assert t1['all']['caudal'] == 2710
    assert t1['all']['total'] == 4034
    assert round(t1['all']['rostral'] / t1['all']['total'] * 100) == 33
    assert round(t1['all']['caudal'] / t1['all']['total'] * 100) == 67


def test_figure2_distributions_shape_and_sums():
    """Verify Figure 2 distribution curves have 30 slices and correct overall sums."""
    anat = CatLumbosacralAnatomy()
    dists = compute_figure2_distributions(anat)

    assert len(dists['levels']) == 30
    assert len(dists['total']) == 30
    assert np.sum(dists['total']) == 4034
    assert np.sum(dists['flexor']) == 761
    assert np.sum(dists['extensor_no_fdl']) == 2366
    assert np.sum(dists['retractor_with_fdl']) == 907


def test_figure2_peaks_and_caudal_imbalance():
    """Verify flexors peak rostrally (<50) and extensors peak caudally (>50, in L7)."""
    anat = CatLumbosacralAnatomy()
    dists = compute_figure2_distributions(anat)

    # Flexor peak in rostral half
    flex_peak_slice = np.argmax(dists['flexor'])
    assert flex_peak_slice < 15, f"Flexor peak slice {flex_peak_slice} should be in rostral half (<15)"

    # Extensor peak in caudal half (L7 segment, slices 20-26)
    ext_peak_slice = np.argmax(dists['extensor_no_fdl'])
    assert 18 <= ext_peak_slice <= 26, f"Extensor peak slice {ext_peak_slice} should be in L7 (18-26)"


def test_figure2_plot_generation(tmp_path):
    """Verify composite Figure 2 plot and Table 1 CSV export succeed."""
    out_dir = str(tmp_path)
    plot_path = generate_figure2_complete(output_dir=out_dir)
    assert os.path.exists(plot_path)
    assert os.path.getsize(plot_path) > 10000

    csv_path = os.path.join(out_dir, "table1.csv")
    anat = CatLumbosacralAnatomy()
    df_t1 = export_table1_csv(anat, csv_path)
    assert os.path.exists(csv_path)
    assert len(df_t1) == 4
