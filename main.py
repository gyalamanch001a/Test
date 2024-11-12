import sys
import os
import tkinter as tk  # Import Tkinter for GUI
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui_handler import StockApp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        logging.info("Starting the Stock Analysis Application")
        root = tk.Tk()
        app = StockApp(root)  # Pass the root window to StockApp
        root.mainloop()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
