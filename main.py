import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "simple_booking.db"

# ---------------------------------------------------------
# SECTION 5.2: MODULAR BOOKING POLICY SYSTEM (STRATEGY PATTERN)
# ---------------------------------------------------------
class BookingPolicy:
    def get_max_duration(self) -> int:
        raise NotImplementedError

    def get_description(self) -> str:
        raise NotImplementedError

class MainCampusPolicy(BookingPolicy):
    def get_max_duration(self) -> int:
        return 4
    
    def get_description(self) -> str:
        return "Max 4 Hours | Standard Booking Rules"

class TechHubPolicy(BookingPolicy):
    def get_max_duration(self) -> int:
        return 2
    
    def get_description(self) -> str:
        return "Max 2 Hours | High Demand Policy"

class DistanceCenterPolicy(BookingPolicy):
    def get_max_duration(self) -> int:
        return 8
    
    def get_description(self) -> str:
        return "Max 8 Hours | Extended Booking Rules"

CAMPUS_POLICIES = {
    "Main Campus": MainCampusPolicy(),
    "Tech Hub": TechHubPolicy(),
    "Distance Center": DistanceCenterPolicy()
}

def get_policy_for_campus(campus_name: str) -> BookingPolicy:
    return CAMPUS_POLICIES.get(campus_name, MainCampusPolicy())

# ---------------------------------------------------------
# 1. DATABASE SETUP
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            campus TEXT NOT NULL
        )
    ''')

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

    cursor.execute("SELECT COUNT(*) FROM campuses")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO campuses VALUES (?, ?)", [
            ("Main Campus", 4),
            ("Tech Hub", 2),
            ("Distance Center", 8)
        ])
    
    cursor.execute("SELECT COUNT(*) FROM resources")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO resources (campus, name, type) VALUES (?, ?, ?)", [
            ("Main Campus", "Computer Lab 1", "Lab"),
            ("Main Campus", "HD Projector A", "Projector"),
            ("Main Campus", "Lecture Hall 101", "Room"),
            ("Tech Hub", "Seminar Hall", "Room"),
            ("Tech Hub", "VR Workstation", "Lab"),
            ("Distance Center", "Recording Studio", "Room")
        ])
        
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 2. MAIN APPLICATION GUI
# ---------------------------------------------------------
class SimpleBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resource Booking System")
        self.geometry("550x620")
        
        self.current_user = None
        self.current_role = None
        self.user_primary_campus = None
        self.active_campus = "Main Campus"

        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Treeview.Heading",
            font=("Arial", 9, "bold"),
            background="#d9d9d9",
            relief="solid",
            borderwidth=1
        )
        
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

        if "Lecturer" in self.current_role:
            self.build_lecturer_view(body)
        elif "Administrator" in self.current_role:
            self.build_admin_view(body)
        elif "Operator" in self.current_role:
            self.build_operator_view(body)

    # --- SECTION 5 & 6: LECTURER ROLE INTERFACE WITH POLICY & MANAGEMENT ---
    def build_lecturer_view(self, parent):
        policy = get_policy_for_campus(self.active_campus)

        tk.Label(parent, text="Campus Resource Booking", font=("Arial", 14, "bold")).pack(pady=2)

        # 5.1 Clear Policy Indicator
        policy_lbl = tk.Label(parent, text=f"Active Policy ({self.active_campus}): {policy.get_description()}", font=("Arial", 9, "bold"), fg="#0E01C4", bg="#EAF2FF", padx=5, pady=3)
        policy_lbl.pack(pady=4)

        # Form Container
        form_frame = tk.Frame(parent)
        form_frame.pack(pady=5)

        tk.Label(form_frame, text="Select Resource:").grid(row=0, column=0, sticky="e", pady=2)
        resources = self.get_resources()
        self.cmb_resource = ttk.Combobox(form_frame, values=resources, state="readonly", width=22)
        self.cmb_resource.grid(row=0, column=1, pady=2, padx=5)
        if resources:
            self.cmb_resource.current(0)

        tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="e", pady=2)
        self.ent_date = tk.Entry(form_frame, width=25)
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_date.grid(row=1, column=1, pady=2, padx=5)

        tk.Label(form_frame, text=f"Duration (Hours, Max {policy.get_max_duration()}):").grid(row=2, column=0, sticky="e", pady=2)
        self.ent_hours = tk.Entry(form_frame, width=25)
        self.ent_hours.insert(0, str(min(2, policy.get_max_duration())))
        self.ent_hours.grid(row=2, column=1, pady=2, padx=5)

        tk.Button(parent, text="Book Resource", command=self.save_booking, bg="#0E01C4", fg="white", width=18).pack(pady=6)

        # 6.1 Notebook for Active Bookings, Cancellation, and History
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True, pady=5)

        # Tab 1: Active & Future Bookings
        tab_active = ttk.Frame(notebook, padding=5)
        notebook.add(tab_active, text="Active / Future Bookings")

        self.tree_active = ttk.Treeview(tab_active, columns=("ID", "Resource", "Date", "Hours"), show="headings", height=5)
        for col, width in [("ID", 40), ("Resource", 150), ("Date", 100), ("Hours", 60)]:
            self.tree_active.heading(col, text=col)
            self.tree_active.column(col, width=width, anchor="center")
        self.tree_active.pack(fill="both", expand=True)

        tk.Button(tab_active, text="Cancel Selected Booking", command=self.cancel_selected_booking, bg="#d9534f", fg="white").pack(pady=4)

        # Tab 2: Booking History
        tab_history = ttk.Frame(notebook, padding=5)
        notebook.add(tab_history, text="Past Booking History")

        self.tree_history = ttk.Treeview(tab_history, columns=("ID", "Resource", "Date", "Hours"), show="headings", height=5)
        for col, width in [("ID", 40), ("Resource", 150), ("Date", 100), ("Hours", 60)]:
            self.tree_history.heading(col, text=col)
            self.tree_history.column(col, width=width, anchor="center")
        self.tree_history.pack(fill="both", expand=True)

        self.load_lecturer_bookings()

    def cancel_selected_booking(self):
        selected = self.tree_active.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an active booking to cancel.")
            return

        booking_id = self.tree_active.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirm Cancellation", f"Are you sure you want to cancel booking ID #{booking_id}?"):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Booking cancelled successfully.")
            self.load_lecturer_bookings()

    def load_lecturer_bookings(self):
        if not hasattr(self, 'tree_active') or not hasattr(self, 'tree_history'):
            return

        for tree in (self.tree_active, self.tree_history):
            for row in tree.get_children():
                tree.delete(row)

        today_str = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Active & Future Bookings
        cursor.execute(
            "SELECT id, resource_name, booking_date, hours FROM bookings WHERE user_name=? AND campus=? AND booking_date >= ? ORDER BY booking_date ASC",
            (self.current_user, self.active_campus, today_str)
        )
        for row in cursor.fetchall():
            self.tree_active.insert("", "end", values=row)

        # Past History
        cursor.execute(
            "SELECT id, resource_name, booking_date, hours FROM bookings WHERE user_name=? AND campus=? AND booking_date < ? ORDER BY booking_date DESC",
            (self.current_user, self.active_campus, today_str)
        )
        for row in cursor.fetchall():
            self.tree_history.insert("", "end", values=row)

        conn.close()

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

        # 5.1 Enforce Policy Max Duration Automatically
        policy = get_policy_for_campus(self.active_campus)
        max_hrs = policy.get_max_duration()

        try:
            hrs = int(hours)
            if hrs < 1 or hrs > max_hrs:
                messagebox.showerror("Policy Error", f"Duration for {self.active_campus} must be between 1 and {max_hrs} hours.")
                return
        except ValueError:
            messagebox.showerror("Error", "Hours must be a valid number.")
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
        self.load_lecturer_bookings()

if __name__ == "__main__":
    init_db()
    app = SimpleBookingApp()
    app.mainloop()