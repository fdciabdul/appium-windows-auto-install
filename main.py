import tkinter as tk
from cmd.app import AppiumSetupApp

if __name__ == "__main__":
    root = tk.Tk()
    app = AppiumSetupApp(root)
    root.mainloop()