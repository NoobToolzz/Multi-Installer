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
        remote_choices_url = "https://paste.gg/p/not_noob/fb60e2abb17143ed981929025b80b988/files/9d5d4557674343738a980f8bf5e9a777/raw"

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
