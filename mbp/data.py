from mbp.webscraping import get_team_games_for_year, activate_web_driver
from mbp.paths import SEASONS_DIR, RAW_DATA_DIR
import pandas as pd


def download_raw_data_for_team(team_name: str, year: str):
    driver = activate_web_driver("firefox")

    # Read team names
    df = pd.read_csv(f"{RAW_DATA_DIR}/mbb_team_names_to_number.csv", index_col=0)
    # Select games for year
    games_df = get_team_games_for_year(driver, df, team_name, year)

    # Save
    save_path = SEASONS_DIR / year / f"{team_name}.csv"
    games_df.to_csv(save_path)

    driver.quit()

    return games_df
