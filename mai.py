import os
import sys
import tkinter as tk
import tkinter.scrolledtext as tkst

from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory

from utils import bedrock

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
            model_kwargs={"max_tokens_to_sample": 350},
        )
        memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=cl_llm, verbose=True, memory=memory
        )

        # Output Text
        self.output_text = tkst.ScrolledText(self, height = 30, width = 125)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.grid(row=0, column=0)

        # Input Text
        self.input_text = tk.Text(self, height = 1, width = 100)
        self.input_text.grid(row=1, column=0)

    def send(self, event=None):
        input = self.input_text.get("1.0", tk.END)
        self.input_text.delete("1.0", tk.END)
        if input:
            ai_response = self.conversation.predict(input=input)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, "[You] " + input)
            self.output_text.insert(tk.END, "[Mai] " + ai_response + "\n\n")
            self.output_text.config(state=tk.DISABLED)
            self.output_text.see("end")

if __name__ == '__main__':
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")
    
    root = tk.Tk() 
    root.title("Mai")
    frame = Gui(root)
    root.bind('<Return>', frame.send)
    frame.pack(fill="both", expand=True)
    root.mainloop()