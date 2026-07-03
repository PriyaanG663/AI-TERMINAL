import os
import subprocess
from rich.console import Console
from rich.panel import Panel 

console=Console()

def execute_windows_command(command):
    """
    Execute a raw command in powershell
    returns a dictionary containing stdout stderr and return code
    """
    cleaned_cmd = command.strip()
    if cleaned_cmd.lower().startswith("cd ") or cleaned_cmd.lower() == "cd":
        try:
            # If it's just 'cd' with nothing else, go to user home directory
            if cleaned_cmd.lower() == "cd":
                target_dir = os.path.expanduser("~")
            else:
                # Extract the path, removing 'cd ' and stripping quotes
                target_dir = cleaned_cmd[3:].strip().strip('"').strip("'")
            
            if target_dir:
                os.chdir(target_dir)
                return {
                    "success": True,
                    "stdout": f"Changed directory to: {os.getcwd()}",
                    "stderr": "",
                    "returncode": 0
                }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Error changing directory: {str(e)}",
                "returncode": -1
            }
    try:
        result = subprocess.run(["powershell","-Command",command],
        capture_output=True,
        text=True,
        shell=True,
        timeout=30
        )
        return {
            "success":result.returncode==0,
            "stdout":result.stdout.strip(),
            "stderr":result.stderr.strip(),
            "returncode":result.returncode
        }
    except subprocess.TimeoutExpired:
        return{
            "success":False,
            "stdout":"",
            "stderr":f"Error: Command execution timed out after 30 seconds.",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "returncode": -1
        }
def main():
    console.print(
        Panel(
            "[bold magenta]Project-1: AI Terminal Shell[/bold magenta]\n"
            "[dim]Milestone 2: Raw Command Execution Engine[/dim]",
            title="Initialized"
        )
    )
    console.print("Type [bold red]'exit'[\bold red] to quit the session.\n")
    while True:
        try:
            user_input=console.input(f"[bold cyan]AI-Shell:{os.getcwd()}>[/bold cyan] ").strip()
            if user_input.lower()=='exit':
                console.print("[bold yellow]Exiting AI Terminal... Goodbye![/bold yellow]")
                break
            if not user_input:
                continue
            response = execute_windows_command(user_input)
            if response["success"]:
                if response["stdout"]:
                    console.print("[bold green]Output:[/bold green]")
                    console.print(response["stdout"])
                else:
                    console.print("[bold green]Command executed successfully with no output.[/bold green]")
            else:
                console.print("[bold red]Error:[/bold red]")
                console.print(response["stderr"], style="red")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Session interrupted. Goodbye![/bold yellow]")
            break
if __name__ == "__main__":
    main()