import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "simple_booking.db"

# 1. DATABASE SETUP
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table supporting roles and assigned campuses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            campus TEXT NOT NULL
        )
    ''')

    # Campuses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campuses (
            campus_name TEXT PRIMARY KEY,
            max_duration INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campus TEXT NOT NULL DEFAULT 'Main Campus',
            name TEXT NOT NULL,
            type TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campus TEXT NOT NULL DEFAULT 'Main Campus',
            user_name TEXT NOT NULL,
            resource_name TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            hours INTEGER NOT NULL
        )
    ''')

    # Seed Default Campuses
    cursor.execute("SELECT COUNT(*) FROM campuses")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO campuses VALUES (?, ?)", [
            ("Main Campus", 4),
            ("Tech Hub", 2),
            ("Distance Center", 8)
        ])
    
    # Add default resources if empty
    cursor.execute("SELECT COUNT(*) FROM resources")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO resources (campus, name, type) VALUES (?, ?, ?)", [
            ("Main Campus", "Computer Lab 1", "Lab"),
            ("Main Campus", "HD Projector A", "Projector"),
            ("Tech Hub", "Seminar Hall", "Room")
        ])
        
    conn.commit()
    conn.close()

# 2. MAIN APPLICATION GUI
class SimpleBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resource Booking System")
        self.geometry("500x580")
        
        self.current_user = None
        self.current_role = None
        self.user_primary_campus = None
        self.active_campus = "Main Campus"

        # --- TTK STYLING FOR BORDERS & GRIDLINES ---
        style = ttk.Style()
        style.theme_use("clam")  # Allows full border customization
        
        # Enclose headings with borders
        style.configure(
            "Treeview.Heading",
            font=("Arial", 9, "bold"),
            background="#d9d9d9",
            relief="solid",
            borderwidth=1
        )
        
        # Add vertical gridlines between cells
        style.configure(
            "Treeview",
            gridlines=True,
            rowheight=22
        )

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- LOGIN & REGISTRATION SCREENS ---
    def show_login_screen(self):
        self.clear_container()
        frame = tk.Frame(self.container)
        frame.pack(expand=True)

        tk.Label(frame, text="Campus System Login", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        tk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e", pady=5)
        ent_user = tk.Entry(frame)
        ent_user.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        ent_pass = tk.Entry(frame, show="*")
        ent_pass.grid(row=2, column=1, pady=5)

        def do_login():
            u = ent_user.get().strip()
            p = ent_pass.get().strip()

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT username, role, campus FROM users WHERE username=? AND password=?", (u, p))
            row = cursor.fetchone()
            conn.close()

            if row:
                self.current_user = row[0]
                self.current_role = row[1]
                self.user_primary_campus = row[2]
                self.show_campus_selection()
            else:
                messagebox.showerror("Error", "Invalid username or password.")

        tk.Button(frame, text="Login", command=do_login, bg="#0E01C4", fg="white", width=15).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Register New Account", command=self.show_register_screen, bg="#e0e0e0", width=20).grid(row=4, column=0, columnspan=2, pady=5)

    def show_register_screen(self):
        self.clear_container()
        frame = tk.Frame(self.container)
        frame.pack(expand=True)

        tk.Label(frame, text="Register New Account", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        tk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e", pady=5)
        ent_user = tk.Entry(frame)
        ent_user.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        ent_pass = tk.Entry(frame, show="*")
        ent_pass.grid(row=2, column=1, pady=5)

        tk.Label(frame, text="Role:").grid(row=3, column=0, sticky="e", pady=5)
        cmb_role = ttk.Combobox(frame, values=["Lecturer", "Campus Administrator", "System Operator"], state="readonly")
        cmb_role.set("Lecturer")
        cmb_role.grid(row=3, column=1, pady=5)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT campus_name FROM campuses")
        campuses = [r[0] for r in cursor.fetchall()]
        conn.close()

        tk.Label(frame, text="Primary Campus:").grid(row=4, column=0, sticky="e", pady=5)
        cmb_campus = ttk.Combobox(frame, values=campuses, state="readonly")
        if campuses:
            cmb_campus.set(campuses[0])
        cmb_campus.grid(row=4, column=1, pady=5)

        def do_register():
            u = ent_user.get().strip()
            p = ent_pass.get().strip()
            r = cmb_role.get()
            c = "All Campuses" if r == "System Operator" else cmb_campus.get()

            if not u or not p:
                messagebox.showerror("Error", "All fields are required.")
                return

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (u, p, r, c))
                conn.commit()
                messagebox.showinfo("Success", "Account registered successfully!")
                self.show_login_screen()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            finally:
                conn.close()

        tk.Button(frame, text="Register", command=do_register, bg="#0E01C4", fg="white", width=15).grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Back to Login", command=self.show_login_screen, bg="#e0e0e0", width=15).grid(row=6, column=0, columnspan=2, pady=5)

    def show_campus_selection(self):
        self.clear_container()
        frame = tk.Frame(self.container)
        frame.pack(expand=True)

        tk.Label(frame, text=f"Welcome, {self.current_user}", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(frame, text=f"Role: {self.current_role}", font=("Arial", 10, "italic")).pack(pady=2)

        tk.Label(frame, text="Select Active Working Campus:").pack(pady=10)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT campus_name FROM campuses")
        campuses = [r[0] for r in cursor.fetchall()]
        conn.close()

        cmb_active = ttk.Combobox(frame, values=campuses, state="readonly")
        cmb_active.pack(pady=5)

        if self.user_primary_campus in campuses:
            cmb_active.set(self.user_primary_campus)
        elif campuses:
            cmb_active.set(campuses[0])

        def proceed():
            self.active_campus = cmb_active.get()
            self.build_dashboard()

        tk.Button(frame, text="Enter Campus Workspace", command=proceed, bg="#0E01C4", fg="white").pack(pady=15)

    # --- MAIN DASHBOARD INTERFACE ---
    def build_dashboard(self):
        self.clear_container()

        # Header Bar
        top_bar = tk.Frame(self.container, bg="#e6e6e6", padx=10, pady=5)
        top_bar.pack(fill="x")

        tk.Label(
            top_bar, 
            text=f"Active Campus: {self.active_campus} | User: {self.current_user} ({self.current_role})", 
            bg="#e6e6e6", 
            font=("Arial", 9, "bold"), 
            fg="#0E01C4"
        ).pack(side="left")

        tk.Button(top_bar, text="Logout", command=self.show_login_screen, bg="#d9534f", fg="white", font=("Arial", 8)).pack(side="right")

        body = tk.Frame(self.container, padx=10, pady=10)
        body.pack(fill="both", expand=True)

        # Render role-specific interface
        if self.current_role == "Lecturer":
            self.build_lecturer_view(body)
        elif self.current_role == "Campus Administrator":
            self.build_admin_view(body)
        elif self.current_role == "System Operator":
            self.build_operator_view(body)

    # --- LECTURER ROLE INTERFACE ---
    def build_lecturer_view(self, parent):
        tk.Label(parent, text="Campus Resource Booking", font=("Arial", 14, "bold")).pack(pady=5)

        tk.Label(parent, text="Your Name:").pack()
        self.ent_user = tk.Entry(parent)
        self.ent_user.insert(0, self.current_user)
        self.ent_user.config(state="readonly")
        self.ent_user.pack(pady=2)

        tk.Label(parent, text="Select Resource:").pack()
        self.cmb_resource = ttk.Combobox(parent, values=self.get_resources(), state="readonly")
        self.cmb_resource.pack(pady=2)
        if self.cmb_resource["values"]:
            self.cmb_resource.current(0)

        tk.Label(parent, text="Date (YYYY-MM-DD):").pack()
        self.ent_date = tk.Entry(parent)
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_date.pack(pady=2)

        tk.Label(parent, text="Duration (Hours, Max 4):").pack()
        self.ent_hours = tk.Entry(parent)
        self.ent_hours.insert(0, "2")
        self.ent_hours.pack(pady=2)

        tk.Button(parent, text="Book Resource", command=self.save_booking, bg="#0E01C4", fg="white").pack(pady=10)

        tk.Label(parent, text="Current Campus Bookings:", font=("Arial", 10, "bold")).pack(pady=5)
        self.tree = ttk.Treeview(parent, columns=("User", "Resource", "Date", "Hours"), show="headings", height=6)
        
        for col in ("User", "Resource", "Date", "Hours"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
            
        self.tree.pack(fill="x", padx=10, pady=5)

        self.load_bookings()

    # --- CAMPUS ADMIN INTERFACE ---
    def build_admin_view(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)

        tab_res = ttk.Frame(notebook, padding=10)
        notebook.add(tab_res, text="Manage Resources")

        tk.Label(tab_res, text="Resource Name:").grid(row=0, column=0, sticky="e", pady=5)
        ent_res_name = tk.Entry(tab_res)
        ent_res_name.grid(row=0, column=1, pady=5)

        tk.Label(tab_res, text="Type (Lab/Projector/Room):").grid(row=1, column=0, sticky="e", pady=5)
        ent_res_type = tk.Entry(tab_res)
        ent_res_type.grid(row=1, column=1, pady=5)

        tree_res = ttk.Treeview(tab_res, columns=("ID", "Name", "Type"), show="headings", height=6)
        for col in ("ID", "Name", "Type"):
            tree_res.heading(col, text=col)
            tree_res.column(col, width=120, anchor="center")
        tree_res.grid(row=3, column=0, columnspan=2, pady=10)

        def load_campus_resources():
            for r in tree_res.get_children():
                tree_res.delete(r)
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, type FROM resources WHERE campus=?", (self.active_campus,))
            for row in cursor.fetchall():
                tree_res.insert("", "end", values=row)
            conn.close()

        def add_resource():
            n = ent_res_name.get().strip()
            t = ent_res_type.get().strip()
            if not n or not t:
                messagebox.showerror("Error", "All fields are required.")
                return

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO resources (campus, name, type) VALUES (?, ?, ?)", (self.active_campus, n, t))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Resource added successfully!")
            ent_res_name.delete(0, 'end')
            ent_res_type.delete(0, 'end')
            load_campus_resources()

        tk.Button(tab_res, text="Add Resource", command=add_resource, bg="#0E01C4", fg="white").grid(row=2, column=0, columnspan=2, pady=5)
        load_campus_resources()

        # Analytics Tab
        tab_analytics = ttk.Frame(notebook, padding=10)
        notebook.add(tab_analytics, text="Campus Analytics")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), IFNULL(AVG(hours), 0) FROM bookings WHERE campus=?", (self.active_campus,))
        tot, avg_h = cursor.fetchone()
        conn.close()

        tk.Label(tab_analytics, text=f"Total Campus Bookings: {tot}", font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
        tk.Label(tab_analytics, text=f"Average Booking Duration: {round(avg_h, 2)} Hours", font=("Arial", 11, "bold")).pack(anchor="w", pady=5)

    # --- SYSTEM OPERATOR INTERFACE ---
    def build_operator_view(self, parent):
        tk.Label(parent, text="Cross-Campus Analytical Report", font=("Arial", 12, "bold")).pack(pady=10)

        tree = ttk.Treeview(parent, columns=("Campus", "Total Resources", "Total Bookings", "Avg Hours"), show="headings", height=8)
        for col in ("Campus", "Total Resources", "Total Bookings", "Avg Hours"):
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor="center")
        tree.pack(fill="both", expand=True, pady=10)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.campus_name,
                (SELECT COUNT(*) FROM resources r WHERE r.campus = c.campus_name),
                COUNT(b.id),
                IFNULL(ROUND(AVG(b.hours), 2), 0)
            FROM campuses c
            LEFT JOIN bookings b ON c.campus_name = b.campus
            GROUP BY c.campus_name
        """)
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    # --- SHARED DATA FUNCTIONS ---
    def get_resources(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM resources WHERE campus=?", (self.active_campus,))
        items = [row[0] for row in cursor.fetchall()]
        conn.close()
        return items

    def save_booking(self):
        user = self.current_user
        resource = self.cmb_resource.get()
        date = self.ent_date.get().strip()
        hours = self.ent_hours.get().strip()

        if not resource:
            messagebox.showerror("Error", "No resource selected or available.")
            return

        try:
            hrs = int(hours)
            if hrs < 1 or hrs > 4:
                messagebox.showerror("Error", "Hours must be between 1 and 4.")
                return
        except ValueError:
            messagebox.showerror("Error", "Hours must be a number.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bookings (campus, user_name, resource_name, booking_date, hours) VALUES (?, ?, ?, ?, ?)",
            (self.active_campus, user, resource, date, hrs)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Booking Saved!")
        self.load_bookings()

    def load_bookings(self):
        if not hasattr(self, 'tree'):
            return

        for row in self.tree.get_children():
            self.tree.delete(row)
            
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_name, resource_name, booking_date, hours FROM bookings WHERE campus=?", (self.active_campus,))
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

if __name__ == "__main__":
    init_db()
    app = SimpleBookingApp()
    app.mainloop()
    