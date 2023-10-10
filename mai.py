import os
import sys
import tkinter as tk

from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory

from utils import bedrock

def main(args=None):
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")

    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_PROFILE"] = "default"

    boto3_bedrock = bedrock.get_bedrock_client(
        assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
        region=os.environ.get("AWS_DEFAULT_REGION", None)
    )

    cl_llm = Bedrock(
        model_id="anthropic.claude-v2",
        client=boto3_bedrock,
        model_kwargs={"max_tokens_to_sample": 1000},
    )
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=cl_llm, verbose=True, memory=memory
    )

    # Create GUI
    main_window = tk.Tk() 
    main_window.title("Mai")
    output_text = tk.Text(main_window, height = 30, width = 100)
    output_text.pack()
    input_text = tk.Text(main_window, height = 15, width = 100)
    input_text.pack()
    button = tk.Button(main_window, text='Send', width=25, command=lambda:send(input_text, output_text, conversation)) 
    button.pack()
    main_window.mainloop()

def send(input_text, output_text, conversation):
    input = input_text.get("1.0", "end-1c")
    if input:
        ai_response = conversation.predict(input=input)
        output_text.insert(tk.END, "[You] " + input + "\n\n")
        output_text.insert(tk.END, "[AI] " + ai_response + "\n\n")
        input_text.delete('1.0', tk.END)
        output_text.see("end")

########################################################################################

if __name__ == '__main__':
    main()