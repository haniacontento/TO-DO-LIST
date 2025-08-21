import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import os

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت وظایف - Task Manager")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.init_database()
        
        # Create GUI
        self.create_widgets()
        
        # Load tasks
        self.load_tasks()
    
    def init_database(self):
        """Initialize SQLite database and create tasks table"""
        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()
        
        # Create tasks table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_date TIMESTAMP NULL
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="مدیریت وظایف", 
                              font=('Arial', 24, 'bold'), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='#f0f0f0')
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="جستجو:", font=('Arial', 12), 
                bg='#f0f0f0', fg='#2c3e50').pack(side=tk.RIGHT, padx=(10, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_tasks)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                                    font=('Arial', 12), width=30)
        self.search_entry.pack(side=tk.RIGHT)
        
        # Add task frame
        add_frame = tk.Frame(main_frame, bg='#f0f0f0')
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(add_frame, text="وظیفه جدید:", font=('Arial', 12), 
                bg='#f0f0f0', fg='#2c3e50').pack(side=tk.RIGHT, padx=(10, 5))
        
        self.task_entry = tk.Entry(add_frame, font=('Arial', 12), width=40)
        self.task_entry.pack(side=tk.RIGHT, padx=(0, 10))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        add_button = tk.Button(add_frame, text="افزودن", command=self.add_task,
                              font=('Arial', 12, 'bold'), 
                              bg='#27ae60', fg='white', 
                              relief=tk.FLAT, padx=20)
        add_button.pack(side=tk.RIGHT)
        
        # Tasks listbox with scrollbar
        list_frame = tk.Frame(main_frame, bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview for better display
        columns = ('id', 'title', 'status', 'created_date')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('id', text='شناسه')
        self.tree.heading('title', text='عنوان وظیفه')
        self.tree.heading('status', text='وضعیت')
        self.tree.heading('created_date', text='تاریخ ایجاد')
        
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('title', width=300, anchor='w')
        self.tree.column('status', width=100, anchor='center')
        self.tree.column('created_date', width=150, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for editing
        self.tree.bind('<Double-1>', self.edit_selected_task)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#f0f0f0')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Action buttons
        edit_button = tk.Button(buttons_frame, text="ویرایش", command=self.edit_selected_task,
                               font=('Arial', 12, 'bold'), 
                               bg='#3498db', fg='white', 
                               relief=tk.FLAT, padx=20)
        edit_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        complete_button = tk.Button(buttons_frame, text="انجام شده", command=self.mark_completed,
                                   font=('Arial', 12, 'bold'), 
                                   bg='#f39c12', fg='white', 
                                   relief=tk.FLAT, padx=20)
        complete_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        delete_button = tk.Button(buttons_frame, text="حذف", command=self.delete_selected_task,
                                 font=('Arial', 12, 'bold'), 
                                 bg='#e74c3c', fg='white', 
                                 relief=tk.FLAT, padx=20)
        delete_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Sort buttons
        sort_frame = tk.Frame(main_frame, bg='#f0f0f0')
        sort_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(sort_frame, text="مرتب‌سازی:", font=('Arial', 12), 
                bg='#f0f0f0', fg='#2c3e50').pack(side=tk.RIGHT, padx=(10, 5))
        
        sort_date_button = tk.Button(sort_frame, text="بر اساس تاریخ", command=self.sort_by_date,
                                    font=('Arial', 11), 
                                    bg='#9b59b6', fg='white', 
                                    relief=tk.FLAT, padx=15)
        sort_date_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        sort_status_button = tk.Button(sort_frame, text="بر اساس وضعیت", command=self.sort_by_status,
                                      font=('Arial', 11), 
                                      bg='#9b59b6', fg='white', 
                                      relief=tk.FLAT, padx=15)
        sort_status_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def add_task(self):
        """Add a new task to the database"""
        title = self.task_entry.get().strip()
        if not title:
            messagebox.showwarning("هشدار", "لطفاً عنوان وظیفه را وارد کنید!")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO tasks (title, status, created_date)
                VALUES (?, ?, ?)
            ''', (title, 'pending', datetime.now()))
            self.conn.commit()
            
            self.task_entry.delete(0, tk.END)
            self.load_tasks()
            messagebox.showinfo("موفق", "وظیفه با موفقیت اضافه شد!")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در افزودن وظیفه: {str(e)}")
    
    def load_tasks(self):
        """Load tasks from database and display in treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.cursor.execute('''
                SELECT id, title, status, created_date, completed_date
                FROM tasks
                ORDER BY created_date DESC
            ''')
            tasks = self.cursor.fetchall()
            
            for task in tasks:
                task_id, title, status, created_date, completed_date = task
                
                # Format dates
                created_str = datetime.fromisoformat(created_date).strftime('%Y-%m-%d %H:%M')
                
                # Status text
                status_text = "انجام شده" if status == 'completed' else "در انتظار"
                
                # Insert into treeview
                item = self.tree.insert('', 'end', values=(task_id, title, status_text, created_str))
                
                # Color coding
                if status == 'completed':
                    self.tree.set(item, 'status', '✅ انجام شده')
                    self.tree.item(item, tags=('completed',))
                else:
                    self.tree.set(item, 'status', '⏳ در انتظار')
                    self.tree.item(item, tags=('pending',))
            
            # Configure tags for colors
            self.tree.tag_configure('completed', background='#d5f4e6', foreground='#27ae60')
            self.tree.tag_configure('pending', background='#fff3cd', foreground='#856404')
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری وظایف: {str(e)}")
    
    def filter_tasks(self, *args):
        """Filter tasks based on search text"""
        search_text = self.search_var.get().strip().lower()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            if search_text:
                self.cursor.execute('''
                    SELECT id, title, status, created_date, completed_date
                    FROM tasks
                    WHERE LOWER(title) LIKE ?
                    ORDER BY created_date DESC
                ''', (f'%{search_text}%',))
            else:
                self.cursor.execute('''
                    SELECT id, title, status, created_date, completed_date
                    FROM tasks
                    ORDER BY created_date DESC
                ''')
            
            tasks = self.cursor.fetchall()
            
            for task in tasks:
                task_id, title, status, created_date, completed_date = task
                
                # Format dates
                created_str = datetime.fromisoformat(created_date).strftime('%Y-%m-%d %H:%M')
                
                # Status text
                status_text = "انجام شده" if status == 'completed' else "در انتظار"
                
                # Insert into treeview
                item = self.tree.insert('', 'end', values=(task_id, title, status_text, created_str))
                
                # Color coding
                if status == 'completed':
                    self.tree.set(item, 'status', '✅ انجام شده')
                    self.tree.item(item, tags=('completed',))
                else:
                    self.tree.set(item, 'status', '⏳ در انتظار')
                    self.tree.item(item, tags=('pending',))
            
            # Configure tags for colors
            self.tree.tag_configure('completed', background='#d5f4e6', foreground='#27ae60')
            self.tree.tag_configure('pending', background='#fff3cd', foreground='#856404')
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در فیلتر کردن وظایف: {str(e)}")
    
    def get_selected_task_id(self):
        """Get the ID of the currently selected task"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک وظیفه را انتخاب کنید!")
            return None
        
        item = self.tree.item(selection[0])
        return item['values'][0]  # First column is ID
    
    def edit_selected_task(self, event=None):
        """Edit the selected task"""
        task_id = self.get_selected_task_id()
        if not task_id:
            return
        
        try:
            self.cursor.execute('SELECT title FROM tasks WHERE id = ?', (task_id,))
            current_title = self.cursor.fetchone()[0]
            
            new_title = simpledialog.askstring("ویرایش وظیفه", 
                                             "عنوان جدید را وارد کنید:", 
                                             initialvalue=current_title)
            
            if new_title and new_title.strip():
                self.cursor.execute('''
                    UPDATE tasks 
                    SET title = ? 
                    WHERE id = ?
                ''', (new_title.strip(), task_id))
                self.conn.commit()
                
                self.load_tasks()
                messagebox.showinfo("موفق", "وظیفه با موفقیت ویرایش شد!")
            elif new_title is not None:  # User clicked Cancel
                messagebox.showwarning("هشدار", "عنوان نمی‌تواند خالی باشد!")
                
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ویرایش وظیفه: {str(e)}")
    
    def delete_selected_task(self):
        """Delete the selected task with confirmation"""
        task_id = self.get_selected_task_id()
        if not task_id:
            return
        
        # Get task title for confirmation
        try:
            self.cursor.execute('SELECT title FROM tasks WHERE id = ?', (task_id,))
            task_title = self.cursor.fetchone()[0]
            
            result = messagebox.askyesno("تأیید حذف", 
                                       f"آیا مطمئن هستید که می‌خواهید وظیفه زیر را حذف کنید؟\n\n'{task_title}'")
            
            if result:
                self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                self.conn.commit()
                
                self.load_tasks()
                messagebox.showinfo("موفق", "وظیفه با موفقیت حذف شد!")
                
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در حذف وظیفه: {str(e)}")
    
    def mark_completed(self):
        """Mark the selected task as completed"""
        task_id = self.get_selected_task_id()
        if not task_id:
            return
        
        try:
            self.cursor.execute('''
                UPDATE tasks 
                SET status = 'completed', completed_date = ?
                WHERE id = ?
            ''', (datetime.now(), task_id))
            self.conn.commit()
            
            self.load_tasks()
            messagebox.showinfo("موفق", "وظیفه به عنوان انجام شده علامت‌گذاری شد!")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در علامت‌گذاری وظیفه: {str(e)}")
    
    def sort_by_date(self):
        """Sort tasks by creation date"""
        self.search_var.set("")  # Clear search
        self.load_tasks()  # This already sorts by date
    
    def sort_by_status(self):
        """Sort tasks by status (completed first, then pending)"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.cursor.execute('''
                SELECT id, title, status, created_date, completed_date
                FROM tasks
                ORDER BY 
                    CASE WHEN status = 'completed' THEN 0 ELSE 1 END,
                    created_date DESC
            ''')
            tasks = self.cursor.fetchall()
            
            for task in tasks:
                task_id, title, status, created_date, completed_date = task
                
                # Format dates
                created_str = datetime.fromisoformat(created_date).strftime('%Y-%m-%d %H:%M')
                
                # Status text
                status_text = "انجام شده" if status == 'completed' else "در انتظار"
                
                # Insert into treeview
                item = self.tree.insert('', 'end', values=(task_id, title, status_text, created_str))
                
                # Color coding
                if status == 'completed':
                    self.tree.set(item, 'status', '✅ انجام شده')
                    self.tree.item(item, tags=('completed',))
                else:
                    self.tree.set(item, 'status', '⏳ در انتظار')
                    self.tree.item(item, tags=('pending',))
            
            # Configure tags for colors
            self.tree.tag_configure('completed', background='#d5f4e6', foreground='#27ae60')
            self.tree.tag_configure('pending', background='#fff3cd', foreground='#856404')
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در مرتب‌سازی وظایف: {str(e)}")
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = TaskManager(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
