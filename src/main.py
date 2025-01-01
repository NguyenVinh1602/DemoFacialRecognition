from tkinter import *
from app import App

def create_main_window():
    window = Tk()
    app = App(window)
    window.mainloop()

if __name__ == "__main__":
    create_main_window()
