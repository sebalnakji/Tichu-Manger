import pytest

from services.score_service import ScoreService


@pytest.mark.parametrize(
    ("team_a_base", "team_b_base", "events", "expected"),
    [
        (70, 30, [], (70, 30)),
        (
            100,
            0,
            [{"type": "tichu", "player_id": 1, "success": True}],
            (200, 0),
        ),
        (
            100,
            0,
            [{"type": "grand", "player_id": 3, "success": False}],
            (100, -200),
        ),
        (
            0,
            0,
            [
                {"type": "one_two", "team": "A"},
                {"type": "tichu", "player_id": 1, "success": True},
            ],
            (300, 0),
        ),
    ],
)
def test_calculate_round_score(
    team_a_base,
    team_b_base,
    events,
    expected,
):
    result = ScoreService.calculate_round_score(
        team_a_base,
        team_b_base,
        events,
        [1, 2],
        [3, 4],
    )

    assert (result["team_a_total"], result["team_b_total"]) == expected
