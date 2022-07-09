import logging
import time
from typing import Optional, Any

import typer
from selenium.webdriver.remote.webelement import WebElement, By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Firefox
from typer import Typer
import dotenv

LOGIN_URL = "https://members.junglescout.com"
SALES_ESTIMATOR_URL = "https://members.junglescout.com/#/toolbox/sales-estimator"

dotenv.load_dotenv(".env")
logger = logging.getLogger(__name__)
cli = Typer(name="JungleScout Scrapper")


def configure_logging():
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler("scraper.log")
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)


def block(message: str = "Press enter to continue"):
    input(message)


class BetterWebDriverMixin(WebDriver):
    def raise_error(self):
        logger.debug("=" * 10 + "\n%r\n" + "=" * 10, self.page_source)
        raise RuntimeError("Unexpected HTML, please check the logs")

    def find_one_element(
        self, by: By = By.ID, value: Optional[str] = None
    ) -> WebElement:
        elements = self.find_elements(by=by, value=value)
        if len(elements) != 1:
            self.raise_error()
        element: WebElement = elements[0]
        return element

    def set_text(self, id_value: str, text: str):
        element = self.find_one_element(value=id_value)
        element.send_keys(text)
        time.sleep(0.5)


class BetterFirefox(Firefox, BetterWebDriverMixin):
    pass


def _login(driver: BetterWebDriverMixin, username: str, password: str) -> None:
    driver.get(LOGIN_URL)
    while not driver.title.startswith("Login"):
        logger.debug("Waiting for login page")
        time.sleep(0.5)
    block("Please complete captcha and return")
    driver.set_text("email", username)
    driver.set_text("current-password", password)
    logger.debug("Login details entered")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    button: WebElement
    (button,) = filter(lambda btn: btn.text == "Log in", buttons)
    button.click()
    time.sleep(1)


def _get_item(driver: BetterWebDriverMixin, item_name: str) -> None:
    driver.get(SALES_ESTIMATOR_URL)


@cli.command()
def scrap(
    username: str = typer.Option(
        ..., prompt="JungleScout username", envvar="JUNGLESCOUT_USER"
    ),
    password: str = typer.Option(
        ...,
        prompt="JungleScout password",
        hide_input=True,
        confirmation_prompt=True,
        envvar="JUNGLESCOUT_PASS",
    ),
):
    with BetterFirefox() as driver:
        _login(driver, username, password)
        _get_item(driver, "cane")
        time.sleep(100)


if __name__ == "__main__":
    cli()
