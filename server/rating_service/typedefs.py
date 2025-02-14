from typing import NamedTuple

from server.games.game_results import GameOutcome
from server.games.typedefs import TeamRatingSummary
from server.rating import Rating

PlayerID = int
RatingDict = dict[PlayerID, Rating]


class GameRatingSummary(NamedTuple):
    """
    Holds minimal information needed to rate a game.
    Fields:
     - game_id: id of the game to rate
     - rating_type: str (e.g. "ladder1v1")
     - teams: a list of two TeamRatingSummaries
    """

    game_id: int
    rating_type: str
    teams: list[TeamRatingSummary]

    @classmethod
    def from_game_info_dict(cls, game_info: dict[str]) -> "GameRatingSummary":
        if len(game_info["teams"]) != 2:
            raise ValueError("Detected other than two teams.")

        return cls(
            game_info["game_id"],
            game_info["rating_type"],
            [
                TeamRatingSummary(
                    GameOutcome(summary["outcome"]),
                    set(summary["player_ids"]),
                    summary["army_results"],
                )
                for summary in game_info["teams"]
            ],
        )


class GameRatingResult(NamedTuple):
    rating_type: str
    old_ratings: RatingDict
    new_ratings: RatingDict
    outcome_map: dict[PlayerID, GameOutcome]


class RatingServiceError(Exception):
    pass


class ServiceNotReadyError(RatingServiceError):
    pass
