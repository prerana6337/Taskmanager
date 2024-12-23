import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("900x700")
        
        # Initialize database first
        self.init_database()
        
        # Task variables
        self.task_title = tk.StringVar()
        self.task_description = tk.StringVar()
        self.task_priority = tk.StringVar(value="Medium")
        self.task_status = tk.StringVar(value="Pending")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_tasks)
        
        # Set color scheme - Modern and friendly colors
        self.colors = {
            'bg': '#f5f6fa',            # Light background
            'header': '#6c5ce7',        # Soft purple
            'button': '#00b894',        # Mint green
            'button_hover': '#00a885',  # Darker mint
            'High': '#ff7675',          # Soft red
            'Medium': '#fdcb6e',        # Soft yellow
            'Low': '#81ecec',           # Soft blue
            'Complete': '#00b894',      # Mint green
            'Complete_bg': '#55efc4',   # Light mint
            'Incomplete': '#a4b0be'     # Soft gray
        }
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles for different priorities and states
        self.style.configure('Header.TLabel', 
                           background=self.colors['header'], 
                           foreground='white', 
                           font=('Segoe UI', 14, 'bold'), 
                           padding=10)
        
        self.style.configure('Custom.TButton', 
                           font=('Segoe UI', 11),
                           padding=10)
        
        self.style.configure('Stats.TLabel', 
                           font=('Segoe UI', 11, 'bold'),
                           padding=5)

        # Configure Treeview colors
        self.style.configure('Custom.Treeview', 
                           background=self.colors['bg'],
                           fieldbackground=self.colors['bg'],
                           font=('Segoe UI', 11),
                           rowheight=30)
        
        self.style.configure('Custom.Treeview.Heading', 
                           font=('Segoe UI', 11, 'bold'),
                           padding=5)
        
        self.create_gui()
        self.load_tasks()
        self.update_clock()
        
    def create_gui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Clock Frame at the top
        clock_frame = ttk.Frame(main_container)
        clock_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.time_label = ttk.Label(clock_frame, 
                                  text="", 
                                  font=('Segoe UI', 14, 'bold'),
                                  foreground=self.colors['header'])
        self.time_label.pack(side=tk.RIGHT)

        # Date label
        self.date_label = ttk.Label(clock_frame, 
                                  text="", 
                                  font=('Segoe UI', 14),
                                  foreground=self.colors['header'])
        self.date_label.pack(side=tk.LEFT)

        # Left Frame for input
        left_frame = ttk.Frame(main_container, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Header
        header_label = ttk.Label(left_frame, 
                               text="Task Details", 
                               style='Header.TLabel')
        header_label.pack(fill=tk.X, pady=(0, 20))

        # Task input fields
        ttk.Label(left_frame, text="Title:", font=('Segoe UI', 11)).pack(fill=tk.X)
        title_entry = ttk.Entry(left_frame, textvariable=self.task_title, font=('Segoe UI', 11))
        title_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(left_frame, text="Description:", font=('Segoe UI', 11)).pack(fill=tk.X)
        desc_entry = ttk.Entry(left_frame, textvariable=self.task_description, font=('Segoe UI', 11))
        desc_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(left_frame, text="Due Date:", font=('Segoe UI', 11)).pack(fill=tk.X)
        self.due_date = DateEntry(left_frame, width=12, 
                                background=self.colors['button'],
                                foreground='white', 
                                borderwidth=2)
        self.due_date.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(left_frame, text="Priority:", font=('Segoe UI', 11)).pack(fill=tk.X)
        priority_combo = ttk.Combobox(left_frame, 
                                    textvariable=self.task_priority,
                                    font=('Segoe UI', 11))
        priority_combo['values'] = ('High', 'Medium', 'Low')
        priority_combo.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(left_frame, text="Status:", font=('Segoe UI', 11)).pack(fill=tk.X)
        status_combo = ttk.Combobox(left_frame, 
                                  textvariable=self.task_status,
                                  font=('Segoe UI', 11))
        status_combo['values'] = ('Pending', 'In Progress', 'Complete')
        status_combo.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(left_frame, text="Categories:", font=('Segoe UI', 11)).pack(fill=tk.X)
        self.categories_entry = ttk.Entry(left_frame, font=('Segoe UI', 11))
        self.categories_entry.pack(fill=tk.X, pady=(0, 20))

        # Action Buttons Section
        action_label = ttk.Label(left_frame, text="Task Actions", style='Header.TLabel')
        action_label.pack(fill=tk.X, pady=(10, 10))

        # Main buttons
        ttk.Button(left_frame, text="Add Task", command=self.add_task).pack(fill=tk.X, pady=2)
        ttk.Button(left_frame, text="Update Task", command=self.update_task).pack(fill=tk.X, pady=2)
        ttk.Button(left_frame, text="Delete Task", command=self.delete_task).pack(fill=tk.X, pady=2)
        ttk.Button(left_frame, text="Clear Completed", command=self.clear_completed_tasks).pack(fill=tk.X, pady=2)

        # Separator
        ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Recycle Bin button
        recycle_btn = ttk.Button(left_frame, text="Recycle Bin", command=self.show_recycle_bin)
        recycle_btn.pack(fill=tk.X, pady=2)

        # Right Frame
        right_frame = ttk.Frame(main_container, padding="10")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Search bar
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(search_frame, text="Search:", 
                 font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(search_frame, textvariable=self.search_var,
                 font=('Segoe UI', 11)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Task list with scrollbar
        self.tree = ttk.Treeview(right_frame, 
                                columns=('Title', 'Description', 'Due Date', 'Priority', 'Status', 'Categories'),
                                show='headings',
                                selectmode='browse',
                                style='Custom.Treeview')

        # Configure column headings
        self.tree.heading('Title', text='Title')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Due Date', text='Due Date')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Categories', text='Categories')

        # Configure column widths
        self.tree.column('Title', width=150)
        self.tree.column('Description', width=200)
        self.tree.column('Due Date', width=100)
        self.tree.column('Priority', width=80)
        self.tree.column('Status', width=100)
        self.tree.column('Categories', width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)

        # Statistics Frame
        stats_frame = ttk.LabelFrame(right_frame, text="Task Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(10, 0))

        # Statistics labels
        stats_left = ttk.Frame(stats_frame)
        stats_left.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.completed_label = ttk.Label(stats_left, text="Completed: 0", 
                                       style='Stats.TLabel')
        self.completed_label.pack(fill=tk.X, pady=2)
        
        self.pending_label = ttk.Label(stats_left, text="Pending: 0", 
                                     style='Stats.TLabel')
        self.pending_label.pack(fill=tk.X, pady=2)
        
        self.total_label = ttk.Label(stats_left, text="Total Tasks: 0", 
                                   style='Stats.TLabel')
        self.total_label.pack(fill=tk.X, pady=2)

        stats_right = ttk.Frame(stats_frame)
        stats_right.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.due_today_label = ttk.Label(stats_right, text="Due Today: 0", 
                                       style='Stats.TLabel')
        self.due_today_label.pack(fill=tk.X, pady=2)

        self.due_week_label = ttk.Label(stats_right, text="Due This Week: 0", 
                                     style='Stats.TLabel')
        self.due_week_label.pack(fill=tk.X, pady=2)

        self.overdue_label = ttk.Label(stats_right, text="Overdue: 0", 
                                     style='Stats.TLabel')
        self.overdue_label.pack(fill=tk.X, pady=2)

    def init_database(self):
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            # Tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT,
                    status TEXT DEFAULT 'Pending',
                    categories TEXT
                )
            ''')
            # Recycle bin table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deleted_tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT,
                    status TEXT,
                    categories TEXT,
                    deleted_date TEXT
                )
            ''')
            conn.commit()

    def add_task(self):
        """Add a new task with validation and feedback"""
        title = self.task_title.get().strip()
        description = self.task_description.get().strip()
        
        # Validate required fields
        if not title:
            messagebox.showerror("Error", "Task title is required!")
            return
            
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                
                # Check for duplicate title
                cursor.execute('SELECT COUNT(*) FROM tasks WHERE title = ?', (title,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "A task with this title already exists!")
                    return
                
                # Insert task with all fields
                cursor.execute('''
                    INSERT INTO tasks (title, description, due_date, priority, status, categories)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    title,
                    description,
                    self.due_date.get_date().strftime('%Y-%m-%d'),
                    self.task_priority.get(),
                    self.task_status.get(),
                    self.categories_entry.get().strip()
                ))
                
            self.task_title.set("")
            self.task_description.set("")
            self.due_date.set_date(datetime.now())
            self.task_priority.set("Medium")
            self.task_status.set("Pending")
            self.categories_entry.delete(0, tk.END)
            self.load_tasks()
            messagebox.showinfo("Success", "✅ Task added successfully!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add task: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def update_clock(self):
        """Update the clock display"""
        current_time = datetime.now()
        
        # Update time with seconds
        time_string = current_time.strftime("%I:%M:%S %p")
        self.time_label.config(text=time_string)
        
        # Update date with day name
        date_string = current_time.strftime("%A, %B %d, %Y")
        self.date_label.config(text=date_string)
        
        # Schedule the next update
        self.root.after(1000, self.update_clock)

    def load_tasks(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks')
            tasks = cursor.fetchall()

            for task in tasks:
                self.tree.insert('', tk.END, values=task[1:7])  # Exclude ID from display

        self.set_tree_item_colors()
        self.update_statistics()

    def set_tree_item_colors(self):
        # Configure tags for different states
        self.tree.tag_configure('completed', 
                              background=self.colors['Complete_bg'],
                              foreground=self.colors['Complete'],
                              font=('Arial', 10, 'overstrike'))  # Strikethrough effect
        
        self.tree.tag_configure('high_priority',
                              background=self.colors['High'],
                              foreground='white')
        
        self.tree.tag_configure('medium_priority',
                              background=self.colors['Medium'],
                              foreground='white')
        
        self.tree.tag_configure('low_priority',
                              background=self.colors['Low'],
                              foreground='white')

        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            priority = values[3]  # Priority column
            status = values[4]    # Status column
            
            if status == 'Complete':
                self.tree.item(item, tags=('completed',))
            else:
                # Apply priority-based tags for incomplete items
                if priority == 'High':
                    self.tree.item(item, tags=('high_priority',))
                elif priority == 'Medium':
                    self.tree.item(item, tags=('medium_priority',))
                else:  # Low priority
                    self.tree.item(item, tags=('low_priority',))

    def item_selected(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item = self.tree.item(selected_item[0])
        values = item['values']
        
        self.task_title.set(values[0])
        self.task_description.set(values[1])
        self.due_date.set_date(values[2])
        self.task_priority.set(values[3])
        self.task_status.set(values[4])
        self.categories_entry.delete(0, tk.END)
        self.categories_entry.insert(0, values[5])

    def update_task(self):
        """Update selected task with validation and feedback"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to update!")
            return
            
        title = self.task_title.get().strip()
        if not title:
            messagebox.showerror("Error", "Task title is required!")
            return
            
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                
                # Get current task ID
                current_values = self.tree.item(selected_item[0])['values']
                cursor.execute('SELECT id FROM tasks WHERE title = ?', (current_values[0],))
                task_id = cursor.fetchone()[0]
                
                # Check for duplicate title (excluding current task)
                cursor.execute('SELECT COUNT(*) FROM tasks WHERE title = ? AND id != ?', 
                             (title, task_id))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "A task with this title already exists!")
                    return
                
                # Update task
                cursor.execute('''
                    UPDATE tasks 
                    SET title=?, description=?, due_date=?, priority=?, status=?, categories=?
                    WHERE id=?
                ''', (
                    title,
                    self.task_description.get().strip(),
                    self.due_date.get_date().strftime('%Y-%m-%d'),
                    self.task_priority.get(),
                    self.task_status.get(),
                    self.categories_entry.get().strip(),
                    task_id
                ))
                
            self.task_title.set("")
            self.task_description.set("")
            self.due_date.set_date(datetime.now())
            self.task_priority.set("Medium")
            self.task_status.set("Pending")
            self.categories_entry.delete(0, tk.END)
            self.load_tasks()
            messagebox.showinfo("Success", "✅ Task updated successfully!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update task: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def delete_task(self):
        """Move selected task to recycle bin"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to delete!")
            return

        task_values = self.tree.item(selected_item[0])['values']
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Move task to recycle bin:\n'{task_values[0]}'?"):
            return

        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                # Move to recycle bin
                cursor.execute('''
                    INSERT INTO deleted_tasks 
                    (title, description, due_date, priority, status, categories, deleted_date)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                ''', task_values)
                
                # Remove from tasks
                cursor.execute('DELETE FROM tasks WHERE title = ?', (task_values[0],))

            self.task_title.set("")
            self.task_description.set("")
            self.due_date.set_date(datetime.now())
            self.task_priority.set("Medium")
            self.task_status.set("Pending")
            self.categories_entry.delete(0, tk.END)
            self.load_tasks()
            messagebox.showinfo("Success", "Task moved to recycle bin!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete task: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def clear_completed_tasks(self):
        """Clear all completed tasks with confirmation and feedback"""
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                
                # Get count of completed tasks
                cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "Complete"')
                completed_count = cursor.fetchone()[0]
                
                if completed_count == 0:
                    messagebox.showinfo("Info", "No completed tasks to clear!")
                    return
                
                # Ask for confirmation
                if not messagebox.askyesno("Confirm Clear", 
                                         f"Are you sure you want to clear {completed_count} completed task(s)?"):
                    return
                
                # Delete completed tasks
                cursor.execute('DELETE FROM tasks WHERE status = "Complete"')
                
            self.load_tasks()
            messagebox.showinfo("Success", 
                              f"🧹 Successfully cleared {completed_count} completed task(s)!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to clear tasks: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def filter_tasks(self, *args):
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks')
            tasks = cursor.fetchall()

            for task in tasks:
                if (search_term in task[1].lower() or  # Title
                    search_term in task[2].lower() or  # Description
                    search_term in task[4].lower() or  # Priority
                    search_term in task[6].lower()):   # Categories
                    self.tree.insert('', tk.END, values=task[1:7])

        self.set_tree_item_colors()
        self.update_statistics()

    def update_statistics(self):
        """Update all statistics in real-time"""
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            
            current_time = datetime.now()
            current_date = current_time.strftime('%Y-%m-%d')
            
            # Basic statistics
            cursor.execute('SELECT COUNT(*) FROM tasks')
            total_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "Complete"')
            completed_count = cursor.fetchone()[0]
            
            pending_count = total_count - completed_count
            
            # Time-based queries
            cursor.execute('''
                SELECT COUNT(*) FROM tasks 
                WHERE date(due_date) = date(?) 
                AND status != "Complete"
            ''', (current_date,))
            due_today = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM tasks 
                WHERE date(due_date) BETWEEN date(?) AND date(?, '+6 days')
                AND status != "Complete"
            ''', (current_date, current_date))
            due_week = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM tasks 
                WHERE date(due_date) < date(?) 
                AND status != "Complete"
            ''', (current_date,))
            overdue = cursor.fetchone()[0]

            # Update statistics labels with emoji and color coding
            self.total_label.config(
                text=f"Total Tasks: {total_count}")
            
            self.completed_label.config(
                text=f"Completed: {completed_count}")
            
            self.pending_label.config(
                text=f"Pending: {pending_count}")
            
            self.due_today_label.config(
                text=f"Due Today: {due_today}")
            
            self.due_week_label.config(
                text=f"Due This Week: {due_week}")
            
            # Add warning emoji if there are overdue tasks
            overdue_text = f"Overdue: {overdue}" if overdue > 0 else f"No Overdue Tasks"
            self.overdue_label.config(text=overdue_text)

            # Update label colors based on values
            if overdue > 0:
                self.overdue_label.config(foreground=self.colors['High'])
            else:
                self.overdue_label.config(foreground=self.colors['Complete'])
                
            # Call this method whenever tasks are modified
            self.root.update_idletasks()

    def load_deleted_tasks(self):
        """Load deleted tasks from the database and display them."""
        # Create a new window for deleted tasks
        recycle_bin_window = tk.Toplevel(self.root)
        recycle_bin_window.title("Recycle Bin")
        recycle_bin_window.geometry("600x400")

        # Create a Treeview to display deleted tasks
        deleted_tree = ttk.Treeview(recycle_bin_window, columns=('Title', 'Description', 'Due Date', 'Priority', 'Status', 'Categories'), show='headings')
        deleted_tree.heading('Title', text='Title')
        deleted_tree.heading('Description', text='Description')
        deleted_tree.heading('Due Date', text='Due Date')
        deleted_tree.heading('Priority', text='Priority')
        deleted_tree.heading('Status', text='Status')
        deleted_tree.heading('Categories', text='Categories')

        deleted_tree.pack(fill=tk.BOTH, expand=True)

        # Fetch deleted tasks from the database
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT title, description, due_date, priority, status, categories FROM deleted_tasks')
            deleted_tasks = cursor.fetchall()

            for task in deleted_tasks:
                deleted_tree.insert('', tk.END, values=task)

    def show_recycle_bin(self):
        """Show recycle bin window with deleted tasks."""
        self.load_deleted_tasks()

    def load_stored_tasks(self):
        connection = sqlite3.connect('tasks.db')  # Connect to the database
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM tasks')  # Assuming 'tasks' is the table name
        tasks = cursor.fetchall()
        connection.close()
        return tasks

    def display_tasks(self):
        tasks = self.load_stored_tasks()
        for task in tasks:
            print(task)  # You can format this as needed

# Store user credentials in a simple list for demonstration
user_credentials = []

# Load credentials from a file
def load_credentials():
    if os.path.exists('credentials.txt'):
        with open('credentials.txt', 'r') as file:
            for line in file:
                username, password = line.strip().split(',')
                user_credentials.append((username, password))

# Save credentials to a file
def save_credentials(username, password):
    with open('credentials.txt', 'a') as file:
        file.write(f'{username},{password}\n')

class AuthPage:
    def __init__(self, master):
        self.master = master
        self.master.title('Login / Register')
        self.master.geometry('300x300')

        self.label_username = tk.Label(master, text='Username:')
        self.label_username.pack(pady=5)
        self.entry_username = tk.Entry(master)
        self.entry_username.pack(pady=5)

        self.label_password = tk.Label(master, text='Password:')
        self.label_password.pack(pady=5)
        self.entry_password = tk.Entry(master, show='*')
        self.entry_password.pack(pady=5)

        self.button_action = tk.Button(master, text='Register', command=self.register)
        self.button_action.pack(pady=20)

        self.button_toggle = tk.Button(master, text='Switch to Login', command=self.toggle)
        self.button_toggle.pack(pady=5)

        self.button_forgot_password = tk.Button(master, text='Forgot Password?', command=self.forgot_password)
        self.button_forgot_password.pack(pady=5)

    def forgot_password(self):
        email = simpledialog.askstring('Forgot Password', 'Enter your registered email:')
        if email:
            # Here you would implement the logic to send an email
            self.send_reset_email(email)

    def send_reset_email(self, email):
        # Set up your email server and credentials
        sender_email = 'your_email@example.com'
        sender_password = 'your_password'
        subject = 'Password Reset Request'
        body = 'Click the link to reset your password: <reset_link>'

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            messagebox.showinfo('Success', 'Password reset email sent!')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to send email: {str(e)}')

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if any(user[0] == username for user in user_credentials):
            messagebox.showerror('Error', 'Username already exists. Please choose another.')
            return
        user_credentials.append((username, password))  # Store as tuple
        save_credentials(username, password)  # Save to file
        messagebox.showinfo('Success', 'Registration successful! You can now log in.')
        self.toggle_to_login()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if (username, password) in user_credentials:
            self.master.destroy()  # Close auth window
            self.open_task_manager()
        else:
            messagebox.showerror('Error', 'Invalid credentials')

    def toggle(self):
        if self.button_action['text'] == 'Register':
            self.button_action['text'] = 'Login'
            self.button_toggle['text'] = 'Switch to Register'
            self.button_action['command'] = self.login
        else:
            self.button_action['text'] = 'Register'
            self.button_toggle['text'] = 'Switch to Login'
            self.button_action['command'] = self.register

    def toggle_to_login(self):
        self.button_action['text'] = 'Login'
        self.button_toggle['text'] = 'Switch to Register'

    def open_task_manager(self):
        root = tk.Tk()
        app = TaskManager(root)
        app.load_tasks()  # Load tasks after successful login
        root.mainloop()

if __name__ == '__main__':
    load_credentials()  # Load credentials on startup
    auth_root = tk.Tk()
    auth_app = AuthPage(auth_root)
    auth_root.mainloop()
