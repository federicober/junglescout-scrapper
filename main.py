import requests
import rich.console
import typer
from typer import Typer


cli = Typer(name="JungleScout Scrapper")

LOGIN_URL = "https://members.junglescout.com/users/sign_in.json"
USER_AGENT = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
)


def _login(session: requests.Session, username: str, password: str):
    response = session.post(
        LOGIN_URL,
        data={"user": {"login": username, "password": password}},
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": USER_AGENT,
        },
    )
    response.raise_for_status()


@cli.command()
def scrap(
    username: str = typer.Option(..., prompt="JungleScout username", envvar="JUNGLESCOUT_USER"),
    password: str = typer.Option(
        ..., prompt="JungleScout password", hide_input=True, confirmation_prompt=True, envvar="JUNGLESCOUT_PASS"
    ),
):
    console = rich.console.Console()
    with requests.Session() as session:
        console.print("Login in with", username)
        _login(session, username, password)


if __name__ == "__main__":
    cli()
