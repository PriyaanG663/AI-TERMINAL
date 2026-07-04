import os
import subprocess
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel 
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
console=Console()
def initialize_gemini():
    """ initializes the gemini model using langchain"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0
    )

def ask_gemini_for_command(llm,user_intent):
    """ Translates natural language into a clean windows powershell command"""
    system_instruction=(
        "You are the internal translation engine of an AI-powered Windows Terminal.\n"
        "Your task is to translate the user's natural language request into a valid Windows PowerShell or CMD command.\n\n"
        "RULES:\n"
        "1. Output ONLY the raw command string ready to run.\n"
        "2. Do NOT wrap your output in markdown syntax like ```powershell or ```.\n"
        "3. Do NOT include explanations, introduction text, warnings, or politeness.\n"
        "4. Focus entirely on Windows 11 environments."
    )
    prompt_template=ChatPromptTemplate.from_messages([
        ("system",system_instruction),
        ("user","{user_request}")
    ])
    chain =prompt_template | llm
    response=chain.invoke({"user_request":user_intent})
    return response.content.strip()

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
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]Error: GOOGLE_API_KEY is missing from your .env file.[/bold red]")
        return

    llm = initialize_gemini()

    tog='AI Terminal'

    console.print(
        Panel(
            "[bold magenta]Project-1: AI Terminal Shell[/bold magenta]\n",
            title="Initialized"
        )
    )
    console.print("Type [bold red]'exit'[\bold red] to quit the session.\n")
    while True:
        try:
            user_input=console.input(f"[bold cyan]{tog}:{os.getcwd()}>[/bold cyan] ").strip()
            if user_input.lower()=='exit':
                console.print("[bold yellow]Exiting AI Terminal... Goodbye![/bold yellow]")
                break
            if user_input.lower()=='toggle':
                console.print("[bold orange]Changing Terminal...[/bold orange]")
                if tog=='AI Terminal':
                    tog='Terminal'
                else:
                    tog='AI Terminal'
                continue

            if not user_input:
                continue
            generated_cmd=user_input
            if tog=='AI Terminal':
                with console.status("[bold green]Gemini is generating command...[/bold green]"):
                    generated_cmd = ask_gemini_for_command(llm, user_input)
                console.print(Panel(f"[bold yellow]AI generated command:[/bold yellow] {generated_cmd}", border_style="dim"))
            response = execute_windows_command(generated_cmd)
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