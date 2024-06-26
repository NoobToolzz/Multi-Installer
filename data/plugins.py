import os
import json
import time
import pathlib
import requests
import subprocess
import fake_headers

from . import list
from tqdm import tqdm
from rich import print
from pathlib import Path
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor

version = "1.0.3"

console = Console()
choices = list.choices
class SideFunctions:
    def __init__(self) -> None:
        self.load_config()

    def load_config(self):
        with open("config.json", 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def save_config(self):
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def cleanUpCache(self):
        [p.unlink() for p in pathlib.Path(".").rglob("*.py[co]")]
        [p.rmdir() for p in pathlib.Path(".").rglob("__pycache__")]

    def displaySettings(self):
        os.system("cls" if os.name == "nt" else "clear")
        
        cleanup_value = self.config.get("cleanup", True)  # Default value if not present

        print(
            Align.center(
                Panel(
                    f"[bold cyan]Cleanup: [bold yellow]{cleanup_value}",
                    title="Settings",
                    subtitle=f"Multi-Installer v{version}",
                    style="bold purple",
                    border_style="bold green",
                )
            )
        )
        
        print(
            Align.center(
                "\n[bold white][[bold yellow]cleanup[bold white]] [bold cyan]Toggle cleanup\n[bold white][[bold yellow]quit[bold white]] [bold red]Back to menu"
            )
        )
        
        user_choice = Prompt.ask(
            "\n[bold white][[bold yellow]>[bold white]] [bold cyan]Choice"
        )
        
        if user_choice.lower() in ["cleanup", "toggle", "toggle cleanup"]:
            self.config["cleanup"] = not cleanup_value
            self.save_config()
            
            print(
                Align.center(
                    f"[bold cyan]Cleanup is now set to [bold yellow]{self.config['cleanup']}"
                )
            )
            
            time.sleep(2)
        
        return self.displaySettings()



class MainFunctions:
    def __init__(self, config) -> None:
        self.config = config
        
    def tableGen(self):
        table = Table()

        table.add_column("Key", justify="center", style="bold yellow", no_wrap=True)
        table.add_column("Name", justify="center", style="bold cyan", no_wrap=True)
        table.add_column("Type", justify="center", style="bold magenta", no_wrap=True)

        for key, choice in choices.items():
            table.add_row(key, choice.name, choice.type)
            # print(Align.center(f"[bold white][[bold yellow]{key}[bold white]] [bold magenta]{choice.name}"))

        return table

    def checkLinkStatuses(self):
        def checkLinkStatus(choice, table):
            try:
                r = requests.head(
                    choice.url,
                    headers=fake_headers.Headers().generate(),
                    allow_redirects=True,
                )
                
                status = (
                    f"[bold green]{r.status_code} [bold cyan]OK"
                    if r.status_code == 200
                    else f"[bold red]{r.status_code} [bold yellow]ERROR"
                )
                
                table.add_row(choice.name, status)
            except Exception as e:
                table.add_row(choice.name, f"[bold red]ERROR")

        os.system("cls" if os.name == "nt" else "clear")

        table = Table()
        
        table.add_column(
            "Name",
            justify="center",
            style="bold cyan",
            no_wrap=True,
        )
        table.add_column("Status", justify="center")

        with Live(Align.center(table), refresh_per_second=4, transient=True):
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(checkLinkStatus, choice, table)
                    for key, choice in choices.items()
                ]

                for future in futures:
                    future.result()
        
        print(
            Align.center(
                Panel.fit(
                    table,
                    title="Link Statuses",
                    subtitle=f"Multi-Installer v{version}",
                    border_style="bold green",
                )
            )
        )
        
        console.input(Align.center("[bold cyan] Press any key to return to menu..."))

    def cleanUpFiles(self, choice, directory):
        if self.config["cleanup"]:
            print(
                Align.center(f"[bold cyan]Deleting [bold yellow]{choices[choice].filename}")
            )
            
            try:
                os.remove(os.path.join(directory, choices[choice].filename))
                
                print(
                    Align.center(
                        f"[bold cyan]Successfully deleted [bold yellow]{choices[choice].filename}"
                    )
                )
            except Exception as e:
                print(
                    Align.center(
                        f"[bold red]Error when deleting [bold yellow]{choices[choice].filename} | [bold magenta]{e}"
                    )
                )
        else:
            print(Align.center(f"[bold cyan]Skipping cleanup..."))
            

    def download_and_run(self, choice):
        os.system("cls" if os.name == "nt" else "clear")
        os.makedirs(os.path.dirname(choices[choice].filename), exist_ok=True)

        try:
            response = requests.get(choices[choice].url, stream=True)
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
                with open(choices[choice].filename, "wb") as file:
                    for data in response.iter_content(block_size):
                        file.write(data)
                        progress_bar.update(len(data))

            stop_timer = time.time()
            downloadElapsed_time = round(stop_timer - start_timer)
            
            print(
                Align.center(
                    f"[bold cyan]Downloaded [bold yellow]{choices[choice].filename} [bold cyan]in [bold magenta]{downloadElapsed_time} [bold cyan]seconds"
                )
            )
            
            time.sleep(1)

            runFile = Prompt.ask(
                f"\n[bold cyan]Would you like to install/run [bold yellow]{choices[choice].filename}[bold cyan]?[bold magenta]",
            )
            
            if runFile.lower() in ["No", "N", "n", "no"]:
                print(
                    Align.center(
                        f"\n[bold cyan]Total time elapsed: [bold magenta]{downloadElapsed_time} [bold cyan]seconds"
                    )
                )
                
                if self.config["cleanup"]:
                    print(
                        Align.center(
                            f"[bold cyan]Cleaning up [bold yellow]{choices[choice].filename} [bold cyan]and exiting..."
                        )
                    )
                    time.sleep(2)
                    
                return
            elif runFile.lower() in ["Yes", "Y", "y", "yes"]:
                pass

            with console.status(
                f"[bold cyan]Running [bold yellow]{choices[choice].filename}",
                spinner="dots",
            ) as status:
                start_timer = time.time()
                
                subprocess.Popen(
                    f'"{Path(__file__).resolve().parent.parent / choices[choice].filename}"',
                    cwd=Path(__file__).resolve().parent.parent,
                    shell=True,
                ).wait()

                status.stop()
                stop_timer = time.time()
                runElapsed_time = round(stop_timer - start_timer)
                
                print(
                    Align.center(
                        f"[bold cyan]Successfully ran [bold yellow]{choices[choice].filename} [bold cyan]in [bold magenta]{runElapsed_time} [bold cyan]seconds\n"
                    )
                )

            print(
                Align.center(
                    f"[bold cyan]Total time elapsed: [bold magenta]{runElapsed_time + downloadElapsed_time} [bold cyan]seconds"
                )
            )

            console.input(f"[bold cyan]Press any key to return to menu")

        except Exception as e:
            print(f"Error: {e}")
