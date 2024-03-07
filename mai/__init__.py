import click
import os
import sys

from mai.llm import LLM
from mai.helpers.colors import purple
from mai.helpers.taskmanager import TaskManager


@click.command()
@click.version_option(
    "0.0.1",
    package_name="Mai",
    message="%(package)s v%(version)s",
)
def main():
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")

    llm = LLM()

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
                    print(purple(ai_response + "\n"))
                # llm.synthesize(ai_response)


if __name__ == "__main__":
    main()
