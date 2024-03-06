import os
import sys

import tkinter as tk
import tkinter.scrolledtext as tkst

from mai import Mai


class Gui(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        # Output Text
        self.output_text = tkst.ScrolledText(self, height=30, width=125)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.grid(row=0, column=0)

        # Input Text
        self.input_text = tk.Text(self, height=1, width=100)
        self.input_text.grid(row=1, column=0)

        self.mai = Mai()

    def send(self, event=None):
        # Insert input in the output text box and clear input in its text box
        input = self.input_text.get("1.0", tk.END)
        self.input_text.delete("1.0", tk.END)

        if input:
            ai_response = self.mai.prompt(input)
            # Insert the response in the output text box
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, "[You] " + input)
            self.output_text.insert(tk.END, ai_response + "\n\n")
            self.output_text.config(state=tk.DISABLED)
            self.output_text.see("end")
            # self.mai.synthesize(ai_response)


if __name__ == "__main__":
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear")

    root = tk.Tk()
    root.title("Mai")
    frame = Gui(root)
    root.bind("<Return>", frame.send)
    frame.pack(fill="both", expand=True)
    root.mainloop()
