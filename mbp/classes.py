import pandas as pd
from datetime import datetime
from pathlib import Path
from mbp.paths import SEASONS_DIR
from mbp.data import download_team_data, download_roster_data


class TeamYear:
    def __init__(self, team_name: str, year: int) -> None:
        self.team_name = team_name
        self.year = year
        self.team_dir = Path(SEASONS_DIR) / str(year) / team_name

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

    def get_next_opponent(self) -> pd.DataFrame:
        """
        Get the next opponent for this team
        """
        pass

    def get_games(self) -> pd.DataFrame:
        """
        Get the games previously save for a team
        """
        return pd.read_csv(self.team_dir / "games.csv", index_col=0)

    def get_stats(self) -> pd.DataFrame:
        """
        Get the stats previously save for a team
        """
        return pd.read_csv(self.team_dir / "stats.csv", index_col=0)

    def get_roster(self) -> pd.DataFrame:
        """
        Get the roster previously save for a team
        """
        return pd.read_csv(self.team_dir / "roster.csv", index_col=0)
