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
    output_text_box = tk.Text(main_window, height = 30, width = 100)
    output_text_box.pack()
    input_text_box = tk.Text(main_window, height = 15, width = 100)
    input_text_box.pack()
    button = tk.Button(main_window, text='Send', width=25, command=main_window.destroy) 
    button.pack()
    main_window.mainloop() 


########################################################################################

if __name__ == '__main__':
    main()