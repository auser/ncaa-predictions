import pandas as pd
from .TeamYear import TeamYear


class TeamGame:
    def __init__(
        self,
        team_a: TeamYear,
        game_details: pd.DataFrame,
    ) -> None:
        self.team_a = team_a
        team_b_name = game_details["opponent"]
        self.team_b = TeamYear(team_b_name, team_a.year)
        self.is_home_game = game_details["home"] == True
        self.date = game_details["datetime"]
        print(game_details)

    def __str__(self) -> str:
        if self.is_home_game:
            return f"{self.team_a.team_name} faces {self.team_b.team_name}"
        else:
            return f"{self.team_b.team_name} faces {self.team_a.team_name}"

    def get_players(self):
        stats_a = self.team_a.get_stats()
        stats_b = self.team_b.get_stats()

        print(stats_a)
