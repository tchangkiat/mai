import os
import sys

from mai import Mai
from utils.colors import purple


def main():
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")

    mai = Mai()

    while True:
        user_input = input("[You] ").lower()
        if user_input == "exit":
            break
        else:
            if user_input:
                ai_response = mai.prompt(user_input)
                print(purple(ai_response + "\n"))
                # self.mai.synthesize(ai_response)


if __name__ == "__main__":
    main()
