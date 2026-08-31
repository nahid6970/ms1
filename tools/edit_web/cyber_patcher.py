import sys
import os
import re
import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from pathlib import Path

console = Console()

def print_banner():
    banner = Text()
    banner.append(r"   _____  _____  ____  ____  ____  ____  _  _  ____  ____  ____ " + "\n", style="bold magenta")
    banner.append(r"  (  _  )(  _  )(  _ \(  _ \(  _ \(  _ \/ )( \(  _ \(  __)(  _ " + "\\\n", style="bold cyan")
    banner.append(r"   ) _ (  )(_)(  ) __/ ) __/ )   / ) __/) \/ ( ) __/ ) _)  )   /" + "\n", style="bold magenta")
    banner.append(r"  (___  )(_____)(__)(__)(__)(_)\_)(__)  \____/(__)  (____)(_)\_)" + "\n", style="bold cyan")
    banner.append("\n          >>> CYBER WEB AI PATCHER v1.0 <<<          ", style="bold bright_white on blue")
    
    console.print(Panel(banner, border_style="bright_magenta", expand=False))

def apply_patch(content):
    # Regex to find blocks of:
    # FILE: <path>
    # <<<<<<< SEARCH
    # <original>
    # =======
    # <new>
    # >>>>>>> REPLACE
    
    # We use (?:...)* to handle potential variations in whitespace
    block_pattern = re.compile(
        r"FILE:\s*(?P<path>[^\n]+)\n"
        r"<<<<<<< SEARCH\n"
        r"(?P<search>.*?)\n"
        r"=======\n"
        r"(?P<replace>.*?)\n"
        r">>>>>>> REPLACE",
        re.DOTALL
    )

    matches = list(block_pattern.finditer(content))
    
    if not matches:
        console.print("[bold red]ERROR:[/bold red] No valid SEARCH/REPLACE blocks detected in clipboard.")
        console.print("[dim]Ensure you used the prompt_web_ai.md instructions with the AI.[/dim]")
        return

    console.print(f"\n[bold cyan]⚡ Detected {len(matches)} neural change-link(s)...[/bold cyan]\n")

    successful_changes = 0
    failed_changes = 0

    for match in matches:
        file_path = match.group("path").strip()
        # Clean up path (remove potential backticks or quotes AI might add)
        file_path = file_path.strip("`\"' ")
        
        search_content = match.group("search").replace("\r\n", "\n")
        replace_content = match.group("replace").replace("\r\n", "\n")
        
        full_path = Path(file_path).resolve()
        
        # New File Logic
        if not search_content.strip() and not full_path.exists():
            console.print(f"[bold yellow]CREATE[/bold yellow] [blue]→[/blue] {file_path}")
            try:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(replace_content)
                successful_changes += 1
                continue
            except Exception as e:
                console.print(f"  [red]FAILED TO CONSTRUCT:[/red] {e}")
                failed_changes += 1
                continue

        if not full_path.exists():
            console.print(f"[bold red]PATH NOT FOUND:[/bold red] {file_path}")
            failed_changes += 1
            continue

        # Existing File Patching
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                file_text = f.read().replace("\r\n", "\n")

            if search_content in file_text:
                new_text = file_text.replace(search_content, replace_content, 1)
                
                # Check line endings of the original file to maintain them
                with open(full_path, "r", encoding="utf-8") as f:
                    original_raw = f.read()
                    line_ending = "\r\n" if "\r\n" in original_raw else "\n"
                
                with open(full_path, "w", encoding="utf-8", newline=line_ending) as f:
                    f.write(new_text)
                
                console.print(f"[bold green]PATCHED[/bold green] [blue]→[/blue] {file_path}")
                successful_changes += 1
            else:
                console.print(f"[bold red]MISMATCH[/bold red]  [blue]→[/blue] {file_path} [dim](Searching block not found)[/dim]")
                failed_changes += 1
        except Exception as e:
            console.print(f"  [bold red]SYSTEM ERROR:[/bold red] {e}")
            failed_changes += 1

    # Final Report
    table = Table(box=None)
    table.add_column("METRIC", style="cyan")
    table.add_column("VALUE", justify="right")
    table.add_row("SUCCESSFUL UPLOADS", f"[bold green]{successful_changes}[/bold green]")
    table.add_row("FAILED SEQUENCES", f"[bold red]{failed_changes}[/bold red]")
    
    console.print("\n", Panel(table, title="[bold magenta]SESSION SUMMARY[/bold magenta]", border_style="bright_blue"))

def main():
    print_banner()
    
    try:
        clipboard_content = pyperclip.paste()
        if not clipboard_content:
            console.print("[yellow]Clipboard buffer empty. Awaiting data...[/yellow]")
            return
        
        apply_patch(clipboard_content)
    except KeyboardInterrupt:
        console.print("\n[bold red]SIGNAL TERMINATED.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]CRITICAL SYSTEM FAILURE:[/bold red] {e}")

if __name__ == "__main__":
    main()
