import pandas as pd
from datetime import datetime
from .TeamYear import TeamYear
from mbp.paths import team_save_dir
from mbp.data import download_game_data


class TeamGame:
    def __init__(
        self, team_a: TeamYear, game_details: pd.DataFrame, year: datetime
    ) -> None:
        self.team_a = team_a
        team_b_name = game_details["opponent"]
        self.team_b = TeamYear(team_b_name, team_a.year)
        self.is_home_game = game_details["home"] == True
        self.date = pd.to_datetime(game_details["datetime"])
        self.year = year

        # Raw stats
        self.team_a_stats = None
        self.team_b_stats = None
        self.game_stats = None

    def __str__(self) -> str:
        if self.is_home_game:
            return f"{self.team_a.team_name} faces {self.team_b.team_name}"
        else:
            return f"{self.team_b.team_name} faces {self.team_a.team_name}"

    def get_game_players(self, reload: bool = False):
        """
        Get players who played in the game
        """
        (team_a_stats, team_b_stats) = self.get_game_stats(reload)
        all_team_a_players = self.team_b.get_roster(reload)
        print(all_team_a_players)

    def get_game_stats(self, reload: bool = False):
        """
        Get game stats for the game
        """
        if self.game_stats is not None and not reload:
            return self.game_stats

        team1_stats_file = self.team_a.team_dir / f"{self.team_b.team_name}.csv"
        team2_stats_file = self.team_b.team_dir / f"{self.team_a.team_name}.csv"

        if not team1_stats_file.exists() or not team2_stats_file.exists():
            (team1, stats1, team2, stats2) = download_game_data(
                self.team_a.team_name, self.team_b.team_name, self.year
            )
        else:
            stats1 = pd.read_csv(team1_stats_file)
            stats2 = pd.read_csv(team2_stats_file)

        self.game_stats = pd.concat([stats1, stats2], ignore_index=True)
        return self.game_stats
