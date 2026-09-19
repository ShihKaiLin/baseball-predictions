"""Regression tests for team-name matching (Red/White Sox collision)."""

from page_utils import team_matches


def test_exact_full_name_match():
    assert team_matches("Boston Red Sox", "Boston Red Sox")


def test_full_name_matches_short_form():
    # statsapi/ESPN full name vs Retrosheet standings short name.
    assert team_matches("Chicago White Sox", "White Sox")
    assert team_matches("White Sox", "Chicago White Sox")


def test_sox_teams_do_not_collide():
    # The old last-word + str.contains logic matched both to "Sox".
    assert not team_matches("Boston Red Sox", "White Sox")
    assert not team_matches("Chicago White Sox", "Red Sox")
    assert not team_matches("Red Sox", "White Sox")
    assert not team_matches("White Sox", "Red Sox")


def test_non_trailing_substring_never_matches():
    # A word that is not a trailing whole word never matches.
    assert not team_matches("Chicago White Sox", "Boston Red Sox")
    assert not team_matches("White", "Chicago White Sox")
    assert not team_matches("Chi", "Chicago White Sox")


def test_no_match_across_teams():
    assert not team_matches("New York Yankees", "Boston Red Sox")
    assert not team_matches("Arizona Diamondbacks", "Yankees")


def test_empty_names_never_match():
    assert not team_matches("", "Yankees")
    assert not team_matches("Yankees", "")
    assert not team_matches("", "")
