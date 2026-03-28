"""Shared test fixtures for Ableton MCP Extended tests."""

import pytest


@pytest.fixture
def time_signature_4_4():
    """Standard 4/4 time signature."""
    return {"numerator": 4, "denominator": 4}


@pytest.fixture
def time_signature_3_4():
    """Waltz 3/4 time signature."""
    return {"numerator": 3, "denominator": 4}


@pytest.fixture
def time_signature_6_8():
    """Compound 6/8 time signature."""
    return {"numerator": 6, "denominator": 8}
