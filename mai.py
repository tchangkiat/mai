from argparse import ArgumentParser
import os
import sys
import tkinter as tk

def main(args=None):
    # Clear the console screen
    if "win32" in sys.platform:
        _ = os.system("cls")
    else:
        _ = os.system("clear") 

    parser = ArgumentParser(description="Mai")
    parser.add_argument("-p", "--prompt", help="Prompt", nargs="?", dest="prompt", default=None)
    args = parser.parse_args(args)

    main_window = tk.Tk() 
    main_window.title("Mai")
    output_text = tk.Text(main_window, height = 30, width = 100)
    output_text.pack()
    input_text = tk.Text(main_window, height = 15, width = 100)
    input_text.pack()
    button = tk.Button(main_window, text='Send', width=25, command=lambda:send(input_text, output_text)) 
    button.pack()
    main_window.mainloop()

def send(input_text, output_text):
    input = input_text.get("1.0", "end-1c")
    output_text.insert(tk.END, "[You] " + input + "\n")
    input_text.delete('1.0', tk.END)

########################################################################################

if __name__ == '__main__':
    main()