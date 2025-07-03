import sqlite3
import bcrypt

# Connect to the database (creates it if not exists)
conn = sqlite3.connect('pneumonia.db')
cursor = conn.cursor()

# Drop old tables if they exist (optional - for dev resets)
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS predictions")

# Create `users` table
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Create `predictions` table
cursor.execute('''
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    prediction TEXT NOT NULL,
    confidence REAL NOT NULL
)
''')

# Insert default test user: admin / admin123 (password is hashed)
default_username = "admin"
default_password = "admin123"
hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())

cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (default_username, hashed_password.decode()))

# Commit and close
conn.commit()
conn.close()

print("✅ Database initialized with default user: admin / admin123")
