import click
import os
import sys

from mai.llm import LLM
from mai.helpers.styles import purple, red
from mai.helpers.taskmanager import TaskManager


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
def main(rag):
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")

    llm = LLM(rag)

    while True:
        user_input = input("[You] ").lower()
        if user_input == "exit":
            break
        else:
            if user_input:
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
