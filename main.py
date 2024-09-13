import os

from rich import print
from pathlib import Path
from rich.align import Align
from rich.panel import Panel
from data.list import choices
from rich.prompt import Prompt
from typing import Callable, Dict
from data.side_functions import SideFunctions
from data.main_functions import MainFunctions

side_functions = SideFunctions()
main_functions = MainFunctions(side_functions)


def exit_program() -> None:
    print(Align.center("[bold red]Exiting..."))
    exit()


def main() -> None:
    commands: Dict[str, Callable[[], None]] = {
        "settings": main_functions.display_settings,
        "status": main_functions.check_link_statuses,
        "exit": exit_program,
        "quit": exit_program,
        "stop": exit_program,
    }

    while True:
        os.system("cls" if os.name == "nt" else "clear")

        print(
            Align.center(
                Panel(
                    main_functions.table_gen(),
                    title="Available Downloads",
                    subtitle=f"Multi-Installer v{side_functions.get_version()}",
                    style="bold purple",
                    border_style="bold green",
                )
            )
        )
        print(
            Align.center(
                "\n[bold white][[bold yellow]settings[bold white]] [bold cyan]Modify settings\n[bold white][[bold yellow]status[bold white]] [bold cyan]Check link availability\n[bold white][[bold yellow]quit[bold white]] [bold red]Exit"
            )
        )

        user_choice = Prompt.ask(
            "\n[bold white][[bold yellow]>[bold white]] [bold cyan]Choice"
        )

        if user_choice.lower() in commands:
            commands[user_choice.lower()]()
        elif user_choice in choices.keys():
            main_functions.download_and_run(user_choice)
            main_functions.clean_up_files(user_choice, Path(__file__).resolve().parent)


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    side_functions.clean_up_cache()
    main()
