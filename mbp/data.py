from mbp.webscraping import (
    get_team_games_for_year,
    activate_web_driver,
    get_team_name_to_ids,
    get_team_roster,
    get_team_stats,
    get_game_stats,
)
from mbp.paths import SEASONS_DIR, RAW_DATA_DIR, team_save_dir
import pandas as pd
import os
from pathlib import Path


def download_team_names_to_id():
    """
    Download the raw team names to transform them from a string
    to the unique id at stats.ncaa.org
    """
    driver = activate_web_driver("firefox")

    team_ids = get_team_name_to_ids(driver, {})

    df = pd.DataFrame.from_dict(team_ids.items())
    df.head()

    df = df.rename(columns={0: "team_name", 1: "team_id"})
    df.reset_index()
    # Save to raw data directory
    df.to_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv")


def get_team_games(team_name: str, year: int) -> pd.DataFrame:
    """
    Get the games previously save for a team
    """
    team_dir = Path(SEASONS_DIR) / str(year) / team_name
    return pd.read_csv(team_dir / "games.csv")


def download_roster_data(team_name: str, year: int, force_new_download: bool = False):
    """
    The roster does not change between games per-year, so
    this only needs to be run once
    """
    driver = activate_web_driver("firefox")

    # Read team names
    df = pd.read_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv", index_col=0)
    save_dir = team_save_dir(team_name, year)

    roster_file = save_dir / "roster.csv"
    if not roster_file.exists() or force_new_download:
        print(f"Downloading {team_name} team roster")
        team_roster = get_team_roster(driver, df, team_name, year)
        team_roster.to_csv(roster_file)
    else:
        roster_file = pd.read_csv(roster_file)

    return roster_file


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
        games_df = games_df.replace("", 0)
        games_df.to_csv(games_file)
    else:
        games_df = pd.read_csv(games_file)

    stats_file = save_dir / "stats.csv"
    if not stats_file.exists() or force_new_download:
        print(f"Downloading {team_name} team stats")
        stats_df = get_team_stats(driver, df, team_name, year)
        stats_df = stats_df.replace("", 0)
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
    games_df = games_df.replace("", 0)

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
    team_roster = team_roster.replace("", 0)
    string_columns = ["player", "pos", "position", "jersey", "team", "year"]
    for col in team_roster.columns:
        print(f"column {col}")
        if not col in string_columns:
            team_roster[col] = team_roster[col].astype(int)

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
    stats_df = stats_df.replace("0", 0)
    string_columns = ["jersey", "player", "position", "pos", "ht", "team"]

    for col in stats_df.columns:
        if not col in string_columns:
            stats_df[col] = stats_df[col].astype(str)

    stats_df["ht"] = stats_df["ht"].apply(convert_height_to_inches)
    stats_df["year"] = stats_df["yr"].apply(convert_student_year_to_int)

    save_dir = team_save_dir(team_name, year)
    # Save
    save_path = save_dir / f"stats.csv"
    stats_df.to_csv(save_path)

    driver.quit()

    return stats_df


def convert_height_to_inches(height: str) -> int:
    """
    Convert height from feet-inches to inches
    """
    if height == "0":
        return 0
    else:
        (feet, inches) = height.split("-")
        return int(feet) * 12 + int(inches)


def convert_student_year_to_int(year: str) -> int:
    """
    Convert student year to season
    """
    year = year.lower()
    if year == "fr":
        return 1
    elif year == "so":
        return 2
    elif year == "jr":
        return 3
    elif year == "sr":
        return 4
    else:
        return 5


def download_game_data(
    team_a: str, team_b: str, year: int
) -> (str, pd.DataFrame, str, pd.DataFrame):
    driver = activate_web_driver("firefox")
    df = pd.read_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv", index_col=0)

    ret = get_game_stats(driver, df, team_a, team_b, year)

    (team1, stats_team1, team2, stats_team2) = ret

    stats_team1 = stats_team1.replace("", 0)
    stats_team2 = stats_team2.replace("", 0)

    team1_games_save_dir = team_save_dir(team1, year) / "games"
    if not team1_games_save_dir.exists():
        team1_games_save_dir.mkdir(exist_ok=True, parents=True)
    stats_team2.to_csv(team1_games_save_dir / f"{team2}.csv")

    team2_games_save_dir = team_save_dir(team2, year) / "games"
    if not team2_games_save_dir.exists():
        team2_games_save_dir.mkdir(exist_ok=True, parents=True)
    stats_team1.to_csv(team2_games_save_dir / f"{team1}.csv")

    return ret
