"""Reset admin password for testing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import bcrypt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

def reset_admin_password():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            new_hash = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin.password_hash = new_hash
            db.commit()
            print(f"Reset password for {admin.email} to 'Admin123!'")
        else:
            print("No admin user found")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
