"""Regression tests for ScoreDistribution.resolved_moneyline().

Guards against the bug where home_moneyline() and away_moneyline() leave
tie_probability() unassigned, so any caller deriving one side from the
other (``away = 1 - home``) silently misallocates the model's tie mass.
This showed up as the Today page's win-probability bar (which read
home_moneyline() directly) disagreeing with the Moneyline card's "Est"
percentage (which subtracted tie_probability()) for the same game.
"""

import numpy as np
import pytest

from src.models.score_distribution import ScoreDistribution, independent_poisson_score_distribution


def test_resolved_moneyline_sums_to_one():
    # Mirrors real 2026-season Dodgers/Giants run rates, which produced a
    # ~13.4% tie_probability - large enough to visibly desync the bar (50%)
    # from the card (36%) before the fix.
    dist = independent_poisson_score_distribution(away_rate=4.166, home_rate=4.709)
    home, away = dist.resolved_moneyline()
    assert home + away == pytest.approx(1.0, abs=1e-9)


def test_resolved_moneyline_matches_raw_split_when_no_tie_mass():
    # Construct a distribution with zero probability on the diagonal so
    # tie_probability() == 0 and resolved_moneyline() should equal the raw
    # home/away moneyline probabilities exactly.
    matrix = np.array([[0.0, 0.3], [0.7, 0.0]])
    dist = ScoreDistribution(matrix)
    assert dist.tie_probability() == 0.0
    home, away = dist.resolved_moneyline()
    assert home == pytest.approx(dist.home_moneyline())
    assert away == pytest.approx(dist.away_moneyline())


def test_resolved_moneyline_preserves_favorite_direction():
    # The favorite (higher raw moneyline prob) should stay the favorite
    # after reallocating tie mass proportionally, not flip sides.
    dist = independent_poisson_score_distribution(away_rate=3.5, home_rate=5.5)
    raw_home, raw_away = dist.home_moneyline(), dist.away_moneyline()
    home, away = dist.resolved_moneyline()
    assert (home > away) == (raw_home > raw_away)


def test_resolved_moneyline_handles_zero_probability_sides():
    # Degenerate case: both raw win probabilities are zero (all mass on the
    # diagonal). Should fall back to a neutral 50/50 split rather than
    # dividing by zero.
    matrix = np.eye(3) / 3.0
    dist = ScoreDistribution(matrix)
    home, away = dist.resolved_moneyline()
    assert home == pytest.approx(0.5)
    assert away == pytest.approx(0.5)
