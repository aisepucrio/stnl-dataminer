import tkinter as tk
from view.menu_view import DataMinerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = DataMinerApp(root)
    root.mainloop()