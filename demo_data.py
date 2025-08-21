#!/usr/bin/env python3
"""
Demo script to populate the task manager database with sample data
برای اضافه کردن داده‌های نمونه به پایگاه داده
"""

import sqlite3
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample tasks in the database"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    # Sample tasks
    sample_tasks = [
        ("خواندن کتاب Python Programming", "completed", datetime.now() - timedelta(days=2)),
        ("انجام پروژه دانشگاه", "pending", datetime.now() - timedelta(days=1)),
        ("خرید مواد غذایی", "completed", datetime.now() - timedelta(hours=6)),
        ("تماس با دوستان", "pending", datetime.now() - timedelta(hours=3)),
        ("ورزش کردن", "pending", datetime.now() - timedelta(hours=1)),
        ("بررسی ایمیل‌ها", "completed", datetime.now() - timedelta(minutes=30)),
        ("برنامه‌ریزی برای فردا", "pending", datetime.now()),
    ]
    
    try:
        # Clear existing data
        cursor.execute('DELETE FROM tasks')
        
        # Insert sample tasks
        for title, status, created_date in sample_tasks:
            if status == 'completed':
                completed_date = created_date + timedelta(hours=2)
            else:
                completed_date = None
                
            cursor.execute('''
                INSERT INTO tasks (title, status, created_date, completed_date)
                VALUES (?, ?, ?, ?)
            ''', (title, status, created_date, completed_date))
        
        conn.commit()
        print("✅ داده‌های نمونه با موفقیت اضافه شدند!")
        print("📋 تعداد وظایف اضافه شده:", len(sample_tasks))
        print("\nبرای مشاهده وظایف، برنامه task_manager.py را اجرا کنید:")
        print("python task_manager.py")
        
    except Exception as e:
        print(f"❌ خطا در اضافه کردن داده‌های نمونه: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🎯 اضافه کردن داده‌های نمونه به برنامه مدیریت وظایف")
    print("=" * 50)
    create_sample_data()
