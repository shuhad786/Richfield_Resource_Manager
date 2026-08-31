import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "simple_booking.db"

# 1. DATABASE SETUP
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            resource_name TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            hours INTEGER NOT NULL
        )
    ''')
    
    # Add default resources if empty
    cursor.execute("SELECT COUNT(*) FROM resources")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO resources (name, type) VALUES (?, ?)", [
            ("Computer Lab 1", "Lab"),
            ("HD Projector A", "Projector"),
            ("Seminar Hall", "Room")
        ])
        
    conn.commit()
    conn.close()

# 2. MAIN APPLICATION GUI
class SimpleBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resource Booking System")
        self.geometry("450x450")
        
        # --- INPUT FIELDS ---
        tk.Label(self, text="Campus Resource Booking", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Your Name:").pack()
        self.ent_user = tk.Entry(self)
        self.ent_user.pack(pady=2)

        tk.Label(self, text="Select Resource:").pack()
        self.cmb_resource = ttk.Combobox(self, values=self.get_resources(), state="readonly")
        self.cmb_resource.pack(pady=2)
        if self.cmb_resource["values"]:
            self.cmb_resource.current(0)

        tk.Label(self, text="Date (YYYY-MM-DD):").pack()
        self.ent_date = tk.Entry(self)
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_date.pack(pady=2)

        tk.Label(self, text="Duration (Hours, Max 4):").pack()
        self.ent_hours = tk.Entry(self)
        self.ent_hours.insert(0, "2")
        self.ent_hours.pack(pady=2)

        tk.Button(self, text="Book Resource", command=self.save_booking, bg="#4CAF50", fg="white").pack(pady=10)

        # --- RECENT BOOKINGS LIST ---
        tk.Label(self, text="Current Bookings:", font=("Arial", 10, "bold")).pack(pady=5)
        self.tree = ttk.Treeview(self, columns=("User", "Resource", "Date", "Hours"), show="headings", height=6)
        for col in ("User", "Resource", "Date", "Hours"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)
        self.tree.pack(fill="x", px=10)

        self.load_bookings()

    def get_resources(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM resources")
        items = [row[0] for row in cursor.fetchall()]
        conn.close()
        return items

    def save_booking(self):
        user = self.ent_user.get().strip()
        resource = self.cmb_resource.get()
        date = self.ent_date.get().strip()
        hours = self.ent_hours.get().strip()

        # Simple Validation Check
        if not user:
            messagebox.showerror("Error", "Please enter your name.")
            return
        
        try:
            hrs = int(hours)
            if hrs < 1 or hrs > 4:
                messagebox.showerror("Error", "Hours must be between 1 and 4.")
                return
        except ValueError:
            messagebox.showerror("Error", "Hours must be a number.")
            return

        # Insert into Database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bookings (user_name, resource_name, booking_date, hours) VALUES (?, ?, ?, ?)",
            (user, resource, date, hrs)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Booking Saved!")
        self.load_bookings()

    def load_bookings(self):
        # Refresh the list view
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_name, resource_name, booking_date, hours FROM bookings")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

if __name__ == "__main__":
    init_db()
    app = SimpleBookingApp()
    app.mainloop()