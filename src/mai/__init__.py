import click
import os
import sys

from mai.helpers.llm import LLM


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
    help="Listen and transcribe audio before passing the transcription to the LLM. For macOS, use 'sudo mai --listen'.",
)
def main(rag, listen):
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")

    # To resolve OpenMP Error #15: Initializing libomp.dylib, but found libomp.dylib already initialized.
    os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

    llm = LLM(rag)

    if listen:
        llm.listen()
    else:
        while True:
            user_input = input("[You] ").lower()
            if user_input.lower() in ["bye", "exit", "quit"]:
                break
            else:
                if user_input:
                    llm.prompt(user_input)


if __name__ == "__main__":
    main()
