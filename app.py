from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

BASE_DIR = Path(_file_).resolve().parent
DB_PATH = BASE_DIR / "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not DB_PATH.exists():
        conn = get_db_connection()
        conn.execute("""
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)
        conn.commit()
        conn.close()

app = Flask(_name_)
app.secret_key = "task_secret"

@app.before_first_request
def setup():
    init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        if not title:
            flash('Title is required.')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO tasks (title, description) VALUES (?, ?)', (title, description))
            conn.commit()
            conn.close()
            flash('Task created successfully!')
            return redirect(url_for('index'))
    return render_template('form.html', action='Create', task=None)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()
    if not task:
        conn.close()
        flash('Task not found.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        status = request.form['status']
        if not title:
            flash('Title is required.')
        else:
            conn.execute('UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?',
                         (title, description, status, id))
            conn.commit()
            conn.close()
            flash('Task updated successfully!')
            return redirect(url_for('index'))

    conn.close()
    return render_template('form.html', action='Edit', task=task)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Task deleted.')
    return redirect(url_for('index'))

if _name_ == '_main_':
    app.run(debug=True)
