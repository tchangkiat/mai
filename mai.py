import os
import sys
import tkinter as tk
import tkinter.scrolledtext as tkst

from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory

from utils import bedrock

def send(input_text, output_text, conversation):
    input = input_text.get("1.0", "end-1c")
    if input:
        ai_response = conversation.predict(input=input)
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, "[You] " + input + "\n\n")
        output_text.insert(tk.END, "[AI] " + ai_response + "\n\n")
        output_text.config(state=tk.DISABLED)
        input_text.delete('1.0', tk.END)
        output_text.see("end")

class Gui(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
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

        # Output Text
        output_text = tkst.ScrolledText(self, height = 30, width = 125)
        output_text.config(state=tk.DISABLED)

        # Input Text
        output_text.grid(row=0, column=0, columnspan=5)
        input_text = tkst.ScrolledText(self, height = 15, width = 100)
        input_text.grid(row=1, column=0)

        # Send Button
        button = tk.Button(self, text='Send', width=10, height=3, command=lambda:send(input_text, output_text, conversation)) 
        button.grid(row=1, column=4)

if __name__ == '__main__':
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")
    
    root = tk.Tk() 
    root.title("Mai")
    frame = Gui(root)
    frame.pack(fill="both", expand=True)
    root.mainloop()