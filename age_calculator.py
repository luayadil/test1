from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox

class AgeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Age Calculator")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Age Calculator", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Date picker
        ttk.Label(main_frame, text="Select your birth date:").grid(row=1, column=0, pady=10, sticky=tk.W)
        self.date_picker = DateEntry(main_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_picker.grid(row=1, column=1, pady=10, sticky=tk.W)
        
        # Calculate button
        calculate_btn = ttk.Button(main_frame, text="Calculate Age", command=self.calculate_age)
        calculate_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Result label
        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 12))
        self.result_label.grid(row=3, column=0, columnspan=2, pady=10)
        
    def calculate_age(self):
        try:
            birth_date = self.date_picker.get_date()
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            self.result_label.config(text=f"Your age is: {age} years")
        except Exception as e:
            messagebox.showerror("Error", "Please select a valid date")

def main():
    root = tk.Tk()
    app = AgeCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main() 