import pytest

from hangmanapi import utils


def test_get_points_won():
    """Test a subsample of possible point outcomes"""
    assert utils.get_points_won(0, "__") == -20
    assert utils.get_points_won(1, "_") == 5
    assert utils.get_points_won(2, "_aa_") == 20
    assert utils.get_points_won(3, "bar") == 15
    assert utils.get_points_won(3, "_11__") == 45
    assert utils.get_points_won(4, "_____") == 100
    assert utils.get_points_won(5, "_____") == 125


def test_update_points():
    "Test a subsample of possible updates"
    session = {'score' : 20}
    utils.update_points(session, 20)
    assert session['score'] == 40

    session = {'score': 30}
    utils.update_points(session, -20)
    assert session['score'] == 10

    session = {'score': 10}
    utils.update_points(session, -20)
    assert session['score'] == 0