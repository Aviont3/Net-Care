"""
Seed script to add sample children to the database
"""
import sys
import os
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.child import Child
from app.models.user import User


def create_sample_children(db: Session):
    """Create sample children with various attributes"""

    # Get the first admin user to assign as creator
    admin_user = db.query(User).filter(User.role == "admin").first()
    if not admin_user:
        print("No admin user found. Please create an admin user first.")
        return

    # Sample children data
    children_data = [
        {
            "first_name": "Emma",
            "last_name": "Johnson",
            "date_of_birth": date.today() - timedelta(days=365 * 3 + 120),  # 3 years 4 months
            "gender": "Female",
            "allergies": "Peanuts, Tree nuts",
            "dietary_restrictions": "Nut-free diet",
            "medical_conditions": None,
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=180),
            "is_active": True,
        },
        {
            "first_name": "Liam",
            "last_name": "Smith",
            "date_of_birth": date.today() - timedelta(days=365 * 4 + 60),  # 4 years 2 months
            "gender": "Male",
            "allergies": None,
            "dietary_restrictions": None,
            "medical_conditions": "Asthma - requires inhaler",
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=365),
            "is_active": True,
        },
        {
            "first_name": "Olivia",
            "last_name": "Williams",
            "date_of_birth": date.today() - timedelta(days=365 * 2 + 180),  # 2 years 6 months
            "gender": "Female",
            "allergies": "Dairy",
            "dietary_restrictions": "Lactose-free diet",
            "medical_conditions": None,
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=90),
            "is_active": True,
        },
        {
            "first_name": "Noah",
            "last_name": "Brown",
            "date_of_birth": date.today() - timedelta(days=365 * 3 + 30),  # 3 years 1 month
            "gender": "Male",
            "allergies": None,
            "dietary_restrictions": "Vegetarian",
            "medical_conditions": None,
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=200),
            "is_active": True,
        },
        {
            "first_name": "Ava",
            "last_name": "Jones",
            "date_of_birth": date.today() - timedelta(days=365 * 4 + 200),  # 4 years 6 months
            "gender": "Female",
            "allergies": "Eggs, Shellfish",
            "dietary_restrictions": "Egg-free, No seafood",
            "medical_conditions": None,
            "special_needs": "Speech therapy - Tuesdays",
            "enrollment_date": date.today() - timedelta(days=400),
            "is_active": True,
        },
        {
            "first_name": "Ethan",
            "last_name": "Garcia",
            "date_of_birth": date.today() - timedelta(days=365 * 2 + 90),  # 2 years 3 months
            "gender": "Male",
            "allergies": None,
            "dietary_restrictions": None,
            "medical_conditions": None,
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=60),
            "is_active": True,
        },
        {
            "first_name": "Sophia",
            "last_name": "Martinez",
            "date_of_birth": date.today() - timedelta(days=365 * 3 + 270),  # 3 years 9 months
            "gender": "Female",
            "allergies": "Gluten",
            "dietary_restrictions": "Gluten-free diet",
            "medical_conditions": "Celiac disease",
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=250),
            "is_active": True,
        },
        {
            "first_name": "Mason",
            "last_name": "Davis",
            "date_of_birth": date.today() - timedelta(days=365 * 4 + 150),  # 4 years 5 months
            "gender": "Male",
            "allergies": None,
            "dietary_restrictions": None,
            "medical_conditions": None,
            "special_needs": "Autism spectrum - requires quiet time",
            "enrollment_date": date.today() - timedelta(days=300),
            "is_active": True,
        },
        {
            "first_name": "Isabella",
            "last_name": "Rodriguez",
            "date_of_birth": date.today() - timedelta(days=365 * 2 + 210),  # 2 years 7 months
            "gender": "Female",
            "allergies": "Bee stings - EpiPen on file",
            "dietary_restrictions": None,
            "medical_conditions": "Severe bee allergy",
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=120),
            "is_active": True,
        },
        {
            "first_name": "Lucas",
            "last_name": "Wilson",
            "date_of_birth": date.today() - timedelta(days=365 * 3 + 150),  # 3 years 5 months
            "gender": "Male",
            "allergies": None,
            "dietary_restrictions": None,
            "medical_conditions": "Diabetes Type 1 - insulin required",
            "special_needs": "Blood sugar monitoring",
            "enrollment_date": date.today() - timedelta(days=220),
            "is_active": True,
        },
        {
            "first_name": "Mia",
            "last_name": "Anderson",
            "date_of_birth": date.today() - timedelta(days=365 * 1 + 300),  # 1 year 10 months
            "gender": "Female",
            "allergies": None,
            "dietary_restrictions": None,
            "medical_conditions": None,
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=30),
            "is_active": True,
        },
        {
            "first_name": "James",
            "last_name": "Taylor",
            "date_of_birth": date.today() - timedelta(days=365 * 4 + 90),  # 4 years 3 months
            "gender": "Male",
            "allergies": "Latex",
            "dietary_restrictions": None,
            "medical_conditions": None,
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=450),
            "is_active": True,
        },
        {
            "first_name": "Charlotte",
            "last_name": "Thomas",
            "date_of_birth": date.today() - timedelta(days=365 * 2 + 240),  # 2 years 8 months
            "gender": "Female",
            "allergies": None,
            "dietary_restrictions": None,
            "medical_conditions": None,
            "special_needs": None,
            "enrollment_date": date.today() - timedelta(days=500),
            "is_active": False,  # Withdrawn
            "withdrawal_date": date.today() - timedelta(days=30),
        },
    ]

    created_count = 0

    for child_data in children_data:
        # Check if child already exists
        existing = db.query(Child).filter(
            Child.first_name == child_data["first_name"],
            Child.last_name == child_data["last_name"]
        ).first()

        if existing:
            print(f"Child {child_data['first_name']} {child_data['last_name']} already exists, skipping...")
            continue

        # Create child
        child = Child(
            **child_data,
            created_by=admin_user.id
        )

        db.add(child)
        created_count += 1
        print(f"Created: {child_data['first_name']} {child_data['last_name']}")

    db.commit()
    print(f"\nSuccessfully created {created_count} children!")
    print(f"Total children in database: {db.query(Child).count()}")


def main():
    """Main function to run the seed script"""
    print("Seeding children data...")
    print("-" * 50)

    db = SessionLocal()
    try:
        create_sample_children(db)
    except Exception as e:
        print(f"\nError seeding data: {e}")
        db.rollback()
    finally:
        db.close()

    print("-" * 50)
    print("Seeding complete!")


if __name__ == "__main__":
    main()
