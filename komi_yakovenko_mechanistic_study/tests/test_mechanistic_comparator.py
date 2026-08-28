"""
Tests for MechanisticComparator and multi-seed Monte Carlo execution.
"""

import sys, os
import pytest
import numpy as np

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from mechanistic_comparator import MechanisticComparator


def test_mechanistic_comparator_multi_seed():
    comparator = MechanisticComparator(seeds=[42, 101])
    df, stats = comparator.run_multi_seed_comparison()

    assert len(df) == 2
    assert 'correlation_r' in df.columns
    assert 'rmse_levels' in df.columns
    assert 'nrmse' in df.columns
    assert 'correlation_r' in stats
    assert -1.0 <= stats['correlation_r']['mean'] <= 1.0
