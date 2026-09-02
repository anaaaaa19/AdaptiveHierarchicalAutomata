"""
Tests for Zero-Downtime Live Model Switch & Version Provenance.
"""

from experiments.phase8.model_switch_test import run_model_switch_test


def test_live_model_switch_and_rollback():
    run_model_switch_test()
