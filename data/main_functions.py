import os
import time
import requests
import fake_headers

from tqdm import tqdm
from rich import print
from pathlib import Path
from rich.live import Live
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.console import Console
from data.list import Choice, choices
from data.side_functions import SideFunctions
from concurrent.futures import ThreadPoolExecutor

console = Console()


class MainFunctions:
    def __init__(self, side_functions: SideFunctions) -> None:
        self.side_functions = side_functions
        self.config = side_functions.config
        self.version = side_functions.get_version()

    @staticmethod
    def table_gen() -> Table:
        table = Table()
        table.add_column("Key", justify="center", style="bold yellow", no_wrap=True)
        table.add_column("Name", justify="center", style="bold cyan", no_wrap=True)
        table.add_column("Type", justify="center", style="bold magenta", no_wrap=True)

        for key, choice in choices.items():
            table.add_row(key, choice.name, choice.type)

        return table

    async def check_link_statuses(self) -> None:
        def check_link_status(choice: Choice, table: Table) -> None:
            try:
                r = requests.head(
                    choice.url,
                    headers=fake_headers.Headers().generate(),
                    allow_redirects=True,
                    timeout=10,
                )

                status = (
                    f"[bold green]{r.status_code} [bold cyan]OK"
                    if r.status_code == 200
                    else f"[bold red]{r.status_code} [bold yellow]ERROR"
                )

                table.add_row(choice.name, status)
            except Exception as e:
                table.add_row(choice.name, f"[bold red]ERROR: {str(e)}")

        os.system("cls" if os.name == "nt" else "clear")

        table = Table()
        table.add_column("Name", justify="center", style="bold cyan", no_wrap=True)
        table.add_column("Status", justify="center")

        with Live(Align.center(table), refresh_per_second=4, transient=True):
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(check_link_status, choice, table)
                    for choice in choices.values()
                ]

                for future in futures:
                    future.result()

        print(
            Align.center(
                Panel.fit(
                    table,
                    title="Link Statuses",
                    subtitle=f"Multi-Installer v{self.version}",
                    border_style="bold green",
                )
            )
        )

        console.input(Align.center("[bold cyan] Press any key to return to menu..."))

    def clean_up_files(self, choice: str, directory: Path) -> None:
        if self.config["cleanup"]:
            file_path = directory / choices[choice].filename
            print(Align.center(f"[bold cyan]Deleting [bold yellow]{file_path.name}"))

            try:
                file_path.unlink()
                print(
                    Align.center(
                        f"[bold cyan]Successfully deleted [bold yellow]{file_path.name}"
                    )
                )
            except Exception as e:
                print(
                    Align.center(
                        f"[bold red]Error when deleting [bold yellow]{file_path.name} | [bold magenta]{e}"
                    )
                )
        else:
            print(Align.center(f"[bold cyan]Skipping cleanup..."))

    def download_and_run(self, choice: str) -> None:
        os.system("cls" if os.name == "nt" else "clear")
        file_path = Path(choices[choice].filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            response = requests.get(choices[choice].url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024  # 1 KB

            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                dynamic_ncols=True,
                leave=False,
                desc="Progress",
            ) as progress_bar:
                start_timer = time.time()
                with file_path.open("wb") as file:
                    for data in response.iter_content(block_size):
                        file.write(data)
                        progress_bar.update(len(data))

            stop_timer = time.time()
            download_elapsed_time = round(stop_timer - start_timer)

            print(
                Align.center(
                    f"[bold cyan]Downloaded [bold yellow]{file_path.name} [bold cyan]in [bold magenta]{download_elapsed_time} [bold cyan]seconds"
                )
            )

            time.sleep(1)

            run_file = Prompt.ask(
                f"\n[bold cyan]Would you like to install/run [bold yellow]{file_path.name}[bold cyan]?[bold magenta]",
            )

            if run_file.lower() in ["no", "n"]:
                print(
                    Align.center(
                        f"\n[bold cyan]Total time elapsed: [bold magenta]{download_elapsed_time} [bold cyan]seconds"
                    )
                )

                if self.config["cleanup"]:
                    print(
                        Align.center(
                            f"[bold cyan]Cleaning up [bold yellow]{file_path.name} [bold cyan]and exiting..."
                        )
                    )
                    time.sleep(2)

                return

            with console.status(
                f"[bold cyan]Running [bold yellow]{file_path.name}",
                spinner="dots",
            ) as status:
                start_timer = time.time()

                os.system(f'"{file_path.resolve()}"')

                status.stop()
                stop_timer = time.time()
                run_elapsed_time = round(stop_timer - start_timer)

                print(
                    Align.center(
                        f"[bold cyan]Successfully ran [bold yellow]{file_path.name} [bold cyan]in [bold magenta]{run_elapsed_time} [bold cyan]seconds\n"
                    )
                )

            print(
                Align.center(
                    f"[bold cyan]Total time elapsed: [bold magenta]{run_elapsed_time + download_elapsed_time} [bold cyan]seconds"
                )
            )

            console.input(f"[bold cyan]Press any key to return to menu")

        except Exception as e:
            print(f"Error: {e}")

    def display_settings(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

        cleanup_value = self.config.get("cleanup", True)

        print(
            Align.center(
                Panel(
                    f"[bold cyan]Cleanup: [bold yellow]{cleanup_value}",
                    title="Settings",
                    subtitle=f"Multi-Installer v{self.version}",
                    style="bold purple",
                    border_style="bold green",
                )
            )
        )

        print(
            Align.center(
                "\n[bold white][[bold yellow]cleanup[bold white]] [bold cyan]Toggle cleanup\n[bold white][[bold yellow]back[bold white]] [bold red]Back to menu"
            )
        )

        user_choice = Prompt.ask(
            "\n[bold white][[bold yellow]>[bold white]] [bold cyan]Choice"
        )

        if user_choice.lower() in ["cleanup", "toggle", "toggle cleanup"]:
            self.config["cleanup"] = not cleanup_value
            self.side_functions.save_config()

            print(
                Align.center(
                    f"[bold cyan]Cleanup is now set to [bold yellow]{self.config['cleanup']}"
                )
            )

            time.sleep(1)
            self.display_settings()
        elif user_choice.lower() in ["quit", "back", "menu"]:
            return
        else:
            print(Align.center("[bold red]Invalid choice"))
            return self.display_settings()
