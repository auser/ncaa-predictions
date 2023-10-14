#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def activate_web_driver(browser: str) -> webdriver:
    options = [
        "--log-level=3",
        "--headless",
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

    from selenium import webdriver

    if browser == "firefox":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager

        print("Installing firefox...")
        # executable_path = GeckoDriverManager().install()
        executable_path = "/Users/auser/.local/bin/geckodriver"
        print(f"executable_path: {executable_path}")
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


activate_web_driver("firefox")
