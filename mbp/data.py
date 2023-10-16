from mbp.webscraping import (
    get_team_games_for_year,
    activate_web_driver,
    get_team_name_to_ids,
    get_team_roster,
    get_team_stats,
)
from mbp.paths import SEASONS_DIR, RAW_DATA_DIR
import pandas as pd
import os
from pathlib import Path


def download_team_names_to_id():
    driver = activate_web_driver("firefox")

    team_ids = get_team_name_to_ids(driver, {})

    df = pd.DataFrame.from_dict(team_ids.items())
    df.head()

    df = df.rename(columns={0: "team_name", 1: "team_id"})
    df.reset_index()
    # Save to raw data directory
    df.to_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv")


def download_team_data(
    team_name: str, year: int = 2023, force_new_download: bool = False
):
    """
    Download all relevant team data
    """
    driver = activate_web_driver("firefox")

    # Read team names
    df = pd.read_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv", index_col=0)

    # Previous games
    save_dir = team_save_dir(team_name, year)
    games_file = save_dir / "games.csv"
    if not games_file.exists() or force_new_download:
        print(f"Downloading {team_name} team games")
        games_df = get_team_games_for_year(driver, df, team_name, year)
        games_df.to_csv(games_file)
    else:
        games_df = pd.read_csv(games_file)

    roster_file = save_dir / "roster.csv"
    if not roster_file.exists() or force_new_download:
        print(f"Downloading {team_name} team roster")
        team_roster = get_team_roster(driver, df, team_name, year)
        team_roster.to_csv(roster_file)
    else:
        roster_file = pd.read_csv(roster_file)

    stats_file = save_dir / "stats.csv"
    if not stats_file.exists() or force_new_download:
        print(f"Downloading {team_name} team stats")
        stats_df = get_team_stats(driver, df, team_name, year)
        stats_df.to_csv(stats_file)
    else:
        stats_df = pd.read_csv(stats_file)

    driver.quit()


def download_raw_team_games_for_year(team_name: str, year: int):
    driver = activate_web_driver("firefox")

    # Read team names
    df = pd.read_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv", index_col=0)
    # Select games for year
    games_df = get_team_games_for_year(driver, df, team_name, year)

    save_dir = team_save_dir(team_name, year)
    # Save
    save_path = save_dir / f"games.csv"
    games_df.to_csv(save_path)

    driver.quit()

    return games_df


def download_and_save_team_roster(team_name: str, year: int) -> pd.DataFrame:
    driver = activate_web_driver("firefox")
    df = pd.read_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv", index_col=0)

    team_roster = get_team_roster(driver, df, team_name, year)

    save_dir = team_save_dir(team_name, year)

    team_roster.to_csv(save_dir / f"roster.csv")

    driver.quit()
    return team_roster


def download_raw_team_stats_for_year(team_name: str, year: str) -> pd.DataFrame:
    """
    Download raw team stats for the year
    """
    driver = activate_web_driver("firefox")

    # Read team names
    df = pd.read_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv", index_col=0)
    # Select games for year
    stats_df = get_team_stats(driver, df, team_name, year)
    save_dir = team_save_dir(team_name, year)
    # Save
    save_path = save_dir / f"stats.csv"
    stats_df.to_csv(save_path)

    driver.quit()

    return stats_df


def team_save_dir(team_name: str, year: int = 2023) -> Path:
    """
    Get the team save directory
    """
    save_dir = Path(SEASONS_DIR / str(year) / team_name)
    if not save_dir.exists():
        save_dir.mkdir(exist_ok=True, parents=True)
    return save_dir
