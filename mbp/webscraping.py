BASE_URL = "https://stats.ncaa.org"

TEAMS_URL = f"{BASE_URL}/teams"
SCOREBOARD_URL = f"{BASE_URL}/contests/livestream_scoreboards"
TEAM_LIST_URL = f"{BASE_URL}/team/inst_team_list"

import time
from bs4 import BeautifulSoup as soup
from urllib.parse import urlencode, urljoin, urlparse
import pandas as pd
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://stats.ncaa.org"

from mbp.utils import get_formatted_year


def activate_web_driver(browser: str, headless: bool = True) -> webdriver:
    options = [
        "--log-level=3",
        "--window-size=1920,1200",
        "--start-maximized",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--ignore-certificate-errors",
        "--disable-extensions",
        "--disable-popup-blocking",
        "--disable-notifications",
        # "--remote-debugging-port=9222",  # https://stackoverflow.com/questions/56637973/how-to-fix-selenium-devtoolsactiveport-file-doesnt-exist-exception-in-python
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        "--disable-blink-features=AutomationControlled",
    ]

    if headless:
        options.append("--headless")

    from selenium import webdriver

    if browser == "firefox":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager

        # executable_path = GeckoDriverManager().install()
        executable_path = "/Users/auser/.local/bin/geckodriver"
        service = FirefoxService(executable_path=executable_path)

        firefox_options = webdriver.FirefoxOptions()
        for option in options:
            firefox_options.add_argument(option)

        driver = webdriver.Firefox(service=service, options=firefox_options)
    else:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service as ChromiumService
        from webdriver_manager.core.os_manager import ChromeType

        chrome_options = Options()
        for option in options:
            chrome_options.add_argument(option)

        executable_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        driver = webdriver.Chrome(service=ChromiumService(executable_path))

    return driver


# TODO: split up this method
def get_team_name_to_ids(driver: webdriver, params: dict = {}) -> dict:
    wait = WebDriverWait(driver, 10)
    TEAM_LIST_URL = f"{BASE_URL}/team/inst_team_list"

    # def scrape_team_names(driver: webdriver, params: dict):
    # "academic_year": float(2023),
    defaults = {
        "sport_code": "MBB",
        "division": int(1),
    }
    merged_params = {k: params.get(k, v) for k, v in defaults.items()}
    query_string = urlencode(merged_params)

    # start_url = urljoin(TEAM_LIST_URL, query_string)
    start_url = f"{TEAM_LIST_URL}?{query_string}"

    driver.get(start_url)
    time.sleep(2)
    # source = soup(driver.page_source, "html.parser")

    # Get team names to real url
    teams = {}

    columns = driver.find_elements(By.CSS_SELECTOR, "table>tbody>tr")

    for col in columns:
        elems = col.find_elements(By.CSS_SELECTOR, "td > a")
        for a in elems:
            link = a.get_attribute("href")
            team_name = a.text
            teams[team_name] = link

    # Finally translate teams to team ids
    team_ids = {}
    for name, link in teams.items():
        driver.get(link)
        wait.until(lambda d: driver.find_element(By.CSS_SELECTOR, "a").is_displayed())
        url = urlparse(driver.current_url)
        team_id = url.path.split("/")[-1]
        team_ids[name] = team_id

    return team_ids


# Direct the webdriver to the team page
def get_team_page(
    driver: webdriver, df: pd.DataFrame, team_name: str, raw_year: int = 2023
) -> pd.DataFrame:
    team_id = df[:][df["team_name"].str.contains(team_name)]["team_id"].iloc[0]

    team_url = f"{TEAMS_URL}/{team_id}"
    driver.get(team_url)

    wait = WebDriverWait(driver, 10)
    wait.until(
        lambda d: driver.find_element(By.CSS_SELECTOR, "a[target=ATHLETICS_URL]")
    )
    # Format date
    formatted_date = get_formatted_year(raw_year)

    select_form = driver.find_element(By.NAME, "year_id")
    select = Select(select_form)
    select.select_by_visible_text(formatted_date)


# Select the schedule and results page
def get_schedule_and_results_page(driver: webdriver) -> list:
    # Select schedule and results
    tables = driver.find_elements(By.CSS_SELECTOR, "#contentarea table>tbody")

    schedule_result_element = None
    for table in tables:
        try:
            legend = table.find_element(By.CSS_SELECTOR, "fieldset>legend")
            if legend.text == "Schedule/Results":
                schedule_result_element = table
        except:
            pass

    # Find the game dates, opponent, results, and attendance (if available)
    listing = schedule_result_element.find_elements(
        By.CSS_SELECTOR, "fieldset table > tbody tr"
    )
    games = []
    for li in listing:
        if li.get_attribute("style") == "":
            games.append(li)

    return games


# Get team games for the year
def get_team_games_for_year(
    driver: webdriver, df: pd.DataFrame, team_name: str, raw_year: int = 2023
) -> pd.DataFrame:
    from mbp.webscraping import TEAMS_URL
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.by import By

    get_team_page(driver, df, team_name, raw_year)

    # Select schedule and results
    games = get_schedule_and_results_page(driver)

    # Get all the dates
    season_games = []
    for idx, game in enumerate(games[1:]):
        # for i in range(4):
        rows = game.find_elements(By.CSS_SELECTOR, "td")
        date = rows[0].text
        try:
            opponent = rows[1].text
        except:
            opponent = None
        try:
            result = rows[2].text or None
        except:
            result = None
        try:
            attendance = rows[3].text or None
        except:
            attendance = None

        res = (date, opponent, result, attendance)
        season_games.append(res)

    # Save to a dataframe
    games_df = pd.DataFrame(season_games)
    games_df.rename(
        columns={
            0: "raw_datetime",
            1: "opponent",
            2: "result",
            3: "attendance",
            4: "home",
        },
        inplace=True,
    )

    # Format datetime
    games_df2 = games_df.copy()
    for idx, row in games_df.iterrows():
        dt = split_and_parse_datetime(row["raw_datetime"])
        games_df2.at[idx, "datetime"] = pd.to_datetime(dt)

        opp = row["opponent"]
        # ncaa.stats isn't for machines
        if "#" in opp:
            opp = opp.split(" ")[1]

        if "@" in opp:
            parts = opp.split("@")

            if parts[0] == "":
                opp_name = parts[1]
            else:
                opp_name = parts[0]

            games_df2.at[idx, "home"] = 0
            games_df2.at[idx, "opponent"] = opp_name.strip()
        else:
            games_df2.at[idx, "home"] = 1
            games_df2.at[idx, "opponent"] = opp.strip()

    games_df3 = games_df2.drop(columns="raw_datetime")
    games_df3 = games_df2
    return games_df3


# Get team roster
def get_team_roster(
    driver: webdriver, df: pd.DataFrame, team_name: str, raw_year: int = 2023
) -> pd.DataFrame:
    from mbp.webscraping import TEAMS_URL
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.by import By

    get_team_page(driver, df, team_name, raw_year)

    # Get roster tab
    roster_link = driver.find_element(By.LINK_TEXT, "Roster")
    roster_link.click()
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: driver.find_element(By.CSS_SELECTOR, "table.dataTable"))
    # Pluck roster table
    roster_table = driver.find_element(By.CSS_SELECTOR, "table#stat_grid")

    players = []
    player_rows = roster_table.find_elements(By.CSS_SELECTOR, "tbody tr")
    for row in player_rows:
        jersey = row.find_element(By.XPATH, f"td[1]").text
        player = row.find_element(By.XPATH, f"td[2]").text
        position = row.find_element(By.XPATH, f"td[3]").text
        height = row.find_element(By.XPATH, f"td[4]").text
        year = row.find_element(By.XPATH, f"td[5]").text
        games_played = row.find_element(By.XPATH, f"td[6]").text
        games_scored = row.find_element(By.XPATH, f"td[7]").text
        players.append(
            {
                "jersey": jersey,
                "player": player,
                "position": position,
                "height": height,
                "year": year,
                "games_played": games_played,
                "games_scored": games_scored,
            }
        )

    # Beautify name
    team_roster = pd.DataFrame(players)
    team_roster1 = team_roster.copy()
    team_roster1["first_name"] = ""
    team_roster1["last_name"] = ""
    for idx, row in team_roster1.iterrows():
        last_name, first_name = row["player"].split(",")
        feet, inch = row["height"].split("-")

        # TODO: fix the dtype error
        team_roster1.loc[idx, "first_name"] = first_name.strip()
        team_roster1.loc[idx, "last_name"] = last_name.strip()
        team_roster1.loc[idx, "height_ft"] = int(feet)
        team_roster1.loc[idx, "height_in"] = int(inch)

    team_roster1 = team_roster1.drop(columns=["player", "height"])
    return team_roster1


# Get team stats
def get_team_stats(
    driver: webdriver, df: pd.DataFrame, team_name: str, raw_year: int = 2023
) -> pd.DataFrame:
    from mbp.webscraping import TEAMS_URL
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.by import By

    # Get the roster stats
    get_team_page(driver, df, team_name, raw_year)
    formatted_year = get_formatted_year(raw_year)

    # Get roster tab
    roster_link = driver.find_element(By.LINK_TEXT, "Team Statistics")
    roster_link.click()
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: driver.find_element(By.CSS_SELECTOR, "table.dataTable"))

    # Huh?
    # This might be the latest, which for whatever reason does not show up
    # as a link on stats.ncaa.org (fruuuussstraing)
    try:
        date_link = driver.find_element(By.LINK_TEXT, formatted_year)
        date_link.click()
    except:
        # Latest date, so don't do anything
        pass

    stats_table = driver.find_element(By.CSS_SELECTOR, "table#stat_grid")
    stats_headings = stats_table.find_elements(By.CSS_SELECTOR, "thead th")
    headings = [h.text for h in stats_headings]
    # df = pd.DataFrame(columns=headings)
    data_df = []
    stats_rows = driver.find_elements(By.CSS_SELECTOR, "table#stat_grid tbody tr")
    for row in stats_rows:
        local_data = []
        for idx in range(len(stats_headings)):
            dat = row.find_element(By.XPATH, f"td[{idx + 1}]")
            local_data.append(dat.text)
        data_df.append(local_data)
        # df = pd.concat([df, local_df])

    team_stats = pd.DataFrame(data_df, columns=headings)
    return team_stats


# Utils


def split_and_parse_datetime(s: str) -> datetime:
    parts = s.split(" ")
    dt = datetime.strptime(parts[0], "%m/%d/%Y")

    if len(parts) == 1:
        return dt

    if parts[1] == "TBA":
        time = None
    else:
        if len(parts) == 1:
            time_str = " ".join(parts[1:])
        else:
            time_str = s

        time = datetime.strptime(time_str, "%I:%M %p")
        dt = dt.replace(hour=time.hour, minute=time.minute)

    return dt
