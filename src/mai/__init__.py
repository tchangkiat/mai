import click
import os
import sys

from mai.llm import LLM
from mai.helpers.styles import purple, red
from mai.helpers.taskmanager import TaskManager
from mai.helpers.transcriber import Transcriber


@click.command()
@click.version_option(
    "0.0.1",
    package_name="Mai",
    message="%(package)s v%(version)s",
)
@click.option(
    "--rag",
    is_flag=True,
    help="Enable Retrieval Augmented Generation",
)
@click.option(
    "--listen",
    is_flag=True,
    help="Listen and transribe audio. For macOS, use 'sudo mai --listen'.",
)
def main(rag, listen):
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")

    llm = LLM(rag)

    if listen:
        tsb = Transcriber(llm, callback_func=llm_prompt)
        tsb.set_hotkey("space")
    else:
        while True:
            user_input = input("[You] ").lower()
            if user_input.lower() in ["bye", "exit", "quit"]:
                break
            else:
                if user_input:
                    llm_prompt(llm, user_input)


def llm_prompt(llm, user_input):
    tm = TaskManager()
    tm.add_task(llm.prompt, user_input)
    for result in tm.run_tasks():
        ai_response = result
        if ai_response is not None:
            print(purple(ai_response + "\n"))
        else:
            print(red("No response from AI"))
    # llm.synthesize(ai_response)


if __name__ == "__main__":
    main()
