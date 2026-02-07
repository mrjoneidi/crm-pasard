from app import create_app
from modules.db import db
from modules.models import Case, Person, Ownership, Document, LeaseContract, Invoice
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid

fake = Faker(['fa_IR']) # Use Persian locale

def populate():
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        print("Populating database with sample data...")

        # Create People
        people = []
        for _ in range(15):
            p = Person(
                full_name=fake.name(),
                national_id=fake.numerify(text="##########"),
                phone=fake.phone_number(),
                alt_phone=fake.phone_number()
            )
            db.session.add(p)
            people.append(p)
        db.session.commit()

        # Create Cases
        cases = []
        for i in range(10):
            created_at = fake.date_time_this_year()
            c = Case(
                case_number=f"CASE-{fake.unique.random_number(digits=5)}",
                classification_number=f"CLS-{fake.unique.random_number(digits=4)}",
                status=random.choice(['active', 'closed', 'pending']),
                address=fake.address(),
                description=fake.text(max_nb_chars=200),
                created_at=created_at
            )
            db.session.add(c)
            cases.append(c)
        db.session.commit()

        # Assign Owners
        for c in cases:
            owner = random.choice(people)
            ownership = Ownership(
                case_id=c.id,
                person_id=owner.id,
                start_date=c.created_at.date(),
                is_current=True
            )
            db.session.add(ownership)
        db.session.commit()

        # Create Documents
        for c in cases:
            for _ in range(random.randint(1, 4)):
                doc = Document(
                    case_id=c.id,
                    title=fake.word(),
                    description=fake.sentence(),
                    file_path=f"uploads/{uuid.uuid4()}.txt", # Fake path
                    category=random.choice(['Deed', 'Contract', 'Map', 'Permit']),
                    created_at=fake.date_time_between(start_date=c.created_at)
                )
                db.session.add(doc)
        db.session.commit()

        # Create Contracts for some cases
        for c in cases[:5]: # First 5 cases have tenants
            tenant = random.choice(people)
            # Ensure tenant is not owner (simplified check)

            contract = LeaseContract(
                case_id=c.id,
                tenant_id=tenant.id,
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=365)).date(),
                base_rent=random.randint(5000000, 50000000),
                payment_period=random.choice(['monthly', 'quarterly', 'yearly']),
                annual_increase_percent=random.randint(10, 25)
            )
            db.session.add(contract)
        db.session.commit()

        print("Database populated successfully!")

if __name__ == '__main__':
    populate()
