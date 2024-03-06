from mai import Mai
from utils.colors import purple

if __name__ == "__main__":
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
