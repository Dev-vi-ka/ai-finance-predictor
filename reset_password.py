"""Reset user password by email."""

import sqlite3
from werkzeug.security import generate_password_hash

def reset_password(email, new_password):
    """Reset password for a user by email."""
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    
    # Check if user exists
    user = cursor.execute("SELECT id, name FROM users WHERE email = ?", (email,)).fetchone()
    
    if not user:
        print(f"Error: No user found with email '{email}'")
        conn.close()
        return False
    
    # Hash the new password
    password_hash = generate_password_hash(new_password)
    
    # Update password
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (password_hash, email))
    conn.commit()
    conn.close()
    
    print(f"Success! Password reset for {user[1]} ({email})")
    print(f"You can now login with this password.")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <email> <new_password>")
        print()
        print("Example: python reset_password.py anildevika99@gmail.com mypassword123")
        sys.exit(1)
    
    email = sys.argv[1]
    new_password = sys.argv[2]
    
    # Validate password
    if len(new_password) < 6:
        print("Error: Password must be at least 6 characters long.")
        sys.exit(1)
    
    if not any(c.isalpha() for c in new_password):
        print("Error: Password must contain at least one letter.")
        sys.exit(1)
    
    if not any(c.isdigit() for c in new_password):
        print("Error: Password must contain at least one digit.")
        sys.exit(1)
    
    reset_password(email, new_password)
