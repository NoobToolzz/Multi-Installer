from rich import print
from data.plugins import *
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt

side_functions = SideFunctions()
main_functions = MainFunctions(side_functions.config)

def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")

        print(
            Align.center(
                Panel(
                    main_functions.tableGen(),
                    title="Available Downloads",
                    subtitle=f"Multi-Installer v{version}",
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

        if user_choice.lower() in [
            "exit",
            "quit",
            "stop",
        ]: 
            print(Align.center("[bold red]Exiting..."))
            exit()
        elif user_choice.lower() in ["status", "check", "check status"]:
            main_functions.checkLinkStatuses()
        elif user_choice.lower() in ["settings", "setting"]:
            side_functions.displaySettings()
        elif user_choice in choices.keys():
            main_functions.download_and_run(user_choice)
            main_functions.cleanUpFiles(user_choice, Path(__file__).resolve().parent)
            time.sleep(2)


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")

    side_functions.cleanUpCache() # Prevent Python from writing bytecode to .pyc files and __pycache__ directories
    main()
