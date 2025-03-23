from models import db, User
from app import app  # Import your Flask app
from werkzeug.security import generate_password_hash

# Ensure we run inside an application context
with app.app_context():
    # Create an Admin user
    admin = User(
        username="adminv1", password=generate_password_hash("admin1234"), role="Admin"
    )

    # Add to the database
    db.session.add(admin)
    db.session.commit()

    print("Admin user created successfully!")
