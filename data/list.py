import requests

from rich import print
from rich.console import Console

console = Console()


# Handler for the choices dictionary
class Choice:
    def __init__(self, type, name, url, filename):
        self.type = type
        self.name = name
        self.url = url
        self.filename = filename


def fetch_choices():
    with console.status(
        "[bold green]Fetching choices remotely...", spinner="dots"
    ) as status:
        remote_choices_url = "https://gist.githubusercontent.com/NoobToolzz/c3df31c9dd4356e91ff5ec77bf5f986b/raw/89136ec8f2c5027efd0a4e4d882d6a9f680d383a/gistfile1.txt"

        try:
            response = requests.get(remote_choices_url)
            response.raise_for_status()

            choices_data = response.text.split("\n")
            choices = {}

            for choice_line in choices_data:
                if not choice_line.strip():
                    continue

                parts = choice_line.strip().split(",")
                if len(parts) == 4:
                    type, name, url, filename = parts
                    key = str(len(choices) + 1)
                    choices[key] = Choice(type, name, url, filename)
                else:
                    print(f"[bold red]Invalid line format: {choice_line}")

            status.stop()
            print(f"[bold green]Successfully fetched choices remotely!")
            return choices
        except requests.RequestException as e:
            status.stop()
            print(f"[bold red]Error fetching remote choices: {e}")
            return None


# Choices
choices = fetch_choices()
