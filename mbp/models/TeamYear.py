import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from mbp.paths import SEASONS_DIR, team_save_dir
from mbp.data import (
    download_team_data,
    download_roster_data,
    download_and_save_team_roster,
    download_raw_team_stats_for_year,
    download_raw_team_games_for_year,
)


def get_next_game(team_year, year: int = date.today().year, date_from=date.today()):
    """
    Get the next game object for the next opponent
    """
    from .TeamGame import TeamGame

    next_opponent = team_year.get_next_opponent_or_last(date_from)

    return TeamGame(team_year, next_opponent, year)


class TeamYear:
    def __init__(self, team_name: str, year: int) -> None:
        self.team_name = team_name
        self.year = year
        self.team_dir = team_save_dir(team_name, year)
        self.games = None
        self.roster = None
        self.stats = None

    def download_roster_data(self, force: bool = False):
        """
        Must be run at first
        """
        return download_roster_data(self.team_name, self.year, force)

    def download_updated_data(self, force_update: bool = False):
        """
        Download the latest data for this team
        """
        if not self.team_dir.exists() or force_update:
            # New team we haven't seen before
            return download_team_data(self.team_name, self.year, force_update)
        else:
            # Get the latest stat and compare it to the date today
            df = self.get_games()
            today_date = pd.to_datetime(datetime.now())
            min_date = pd.to_datetime(df["datetime"].min())
            max_date = pd.to_datetime(df["datetime"].max())
            # This isn't all that complex, but could really be a lot better
            # update checking. For now, it will always update everytime
            # in the future, we should check to see if there is a new update
            # in the scores because the date has passed, otherwise skip
            if max_date < today_date or min_date > today_date:
                # If the last date is before today or the min date is after today
                pass
            else:
                # We do need to update because we're in the middle of the season
                return download_team_data(self.team_name, self.year, True)

    def get_next_opponent_or_last(self, date_from=date.today()) -> pd.DataFrame:
        """
        Get the next opponent for this team
        """

        df2 = self.get_games()
        df2["datetime"] = pd.to_datetime(df2["datetime"])
        df2["difference"] = df2["datetime"].dt.date - date_from
        future_dates = df2[df2["difference"] > timedelta(days=0)]
        if future_dates.empty:
            # Return the last possible row
            return df2.iloc[-1]
        else:
            next_future_date = future_dates.loc[future_dates["difference"].idxmin()]
            return next_future_date

    def get_games(self, reload: bool = False) -> pd.DataFrame:
        """
        Get the games previously save for a team
        """
        if self.games is not None and not reload:
            return self.games

        if reload:
            download_raw_team_games_for_year(self.team_name, self.year)

        self.games = pd.read_csv(self.team_dir / "games.csv", index_col=0)
        return self.games

    def get_stats(self, reload: bool = False) -> pd.DataFrame:
        """
        Get the stats previously save for a team
        """
        if self.stats is not None and not reload:
            return self.stats

        if reload:
            download_raw_team_stats_for_year(self.team_name, self.year)

        self.stats = pd.read_csv(self.team_dir / "stats.csv", index_col=0)
        return self.stats

    def get_roster(self, reload: bool = False) -> pd.DataFrame:
        """
        Get the roster previously save for a team
        """
        if self.roster is not None and not reload:
            return self.roster

        if reload:
            download_and_save_team_roster(self.team_name, self.year)

        team_roster_file = self.team_dir / "roster.csv"

        self.roster = pd.read_csv(team_roster_file, index_col=0)
        return self.roster

    def get_roster_stats(self, reload: bool = False):
        """
        Get roster details along with game stats merged
        """
        roster = self.get_roster(reload)
        stats = self.get_stats(reload)
        return pd.merge(roster, stats, on="player")
