"""
Unit tests for Figure 1 of Yakovenko et al. (2002).
Verifies 27 MN pools, 30 slices, 100 levels, centers of mass, and unit oscillator distances.
"""

import sys, os
import pytest
import numpy as np

# Ensure reproduction src is on path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from anatomy import CatLumbosacralAnatomy, MUSCLE_NAMES, JOINT_GROUPS
from figure1_analysis import generate_figure1_complete, compute_figure1_metrics


def test_anatomy_initialization_and_dimensions():
    """Test 30 slices, 28.8 mm length, and 100 levels."""
    anat = CatLumbosacralAnatomy(length_mm=28.8, n_slices=30)
    assert anat.n_slices == 30
    assert anat.length_mm == 28.8
    assert anat.slice_thickness_mm == pytest.approx(0.96, rel=1e-3)
    assert anat.levels_per_slice == pytest.approx(3.333, rel=1e-2)
    assert len(anat.slice_centers_mm) == 30
    assert len(anat.slice_centers_level) == 30


def test_motoneuron_pool_count_and_presence():
    """Test that all 27 hindlimb muscles are present with positive motoneuron counts."""
    anat = CatLumbosacralAnatomy()
    assert len(MUSCLE_NAMES) == 27
    for m in MUSCLE_NAMES:
        assert m in anat.df_distribution.index
        cnt = np.sum(anat.df_distribution.loc[m])
        assert cnt > 0, f"Muscle {m} has 0 motoneurons"


def test_joint_group_memberships():
    """Test that hip, knee, and ankle joint groups contain expected muscles."""
    assert len(JOINT_GROUPS['hip']) == 14
    assert len(JOINT_GROUPS['knee']) == 9
    assert len(JOINT_GROUPS['ankle']) == 9
    assert 'Psoas' in JOINT_GROUPS['hip']
    assert 'VL' in JOINT_GROUPS['knee']
    assert 'Soleus' in JOINT_GROUPS['ankle']


def test_centers_of_mass_rostral_caudal_gradient():
    """Test that hip flexor Psoas is rostral and knee flexor BFp is caudal."""
    anat = CatLumbosacralAnatomy()
    df_metrics = compute_figure1_metrics(anat)

    psoas_cm = anat.centers_of_mass_level['Psoas']
    bfp_cm = anat.centers_of_mass_level['BFp']

    assert psoas_cm < 20.0, f"Psoas center of mass ({psoas_cm}) should be rostral (<20)"
    assert bfp_cm > 80.0, f"BFp center of mass ({bfp_cm}) should be caudal (>80)"
    assert bfp_cm > psoas_cm


def test_unit_oscillator_separation_distances():
    """
    Test the separation distances between flexor and extensor half-centers:
    Hip oscillator ~61 levels, Knee oscillator ~58 levels, Ankle oscillator ~20 levels.
    """
    anat = CatLumbosacralAnatomy()

    # Hip flexor center (Psoas ~15.0) vs Hip extensor center (BFa ~77.0)
    hip_flex_cm = anat.centers_of_mass_level['Psoas']
    hip_ext_cm = anat.centers_of_mass_level['BFa']
    hip_sep = abs(hip_ext_cm - hip_flex_cm)
    assert 55.0 <= hip_sep <= 67.0, f"Hip separation {hip_sep} not in expected range ~61"

    # Knee extensor (RF ~35.0) vs Knee flexor/retractor (BFp ~89.6)
    knee_ext_cm = anat.centers_of_mass_level['RF']
    knee_flex_cm = anat.centers_of_mass_level['BFp']
    knee_sep = abs(knee_flex_cm - knee_ext_cm)
    assert 50.0 <= knee_sep <= 65.0, f"Knee separation {knee_sep} not in expected range ~58"

    # Ankle flexor (TA ~58.0) vs Ankle extensor (Soleus ~80.0)
    ankle_flex_cm = anat.centers_of_mass_level['TA']
    ankle_ext_cm = anat.centers_of_mass_level['Soleus']
    ankle_sep = abs(ankle_ext_cm - ankle_flex_cm)
    assert 15.0 <= ankle_sep <= 28.0, f"Ankle separation {ankle_sep} not in expected range ~20"


def test_figure1_plot_generation(tmp_path):
    """Test that composite Figure 1 generates successfully."""
    out_dir = str(tmp_path)
    out_path = generate_figure1_complete(output_dir=out_dir)
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 10000
