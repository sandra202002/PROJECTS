from app import db, User
from werkzeug.security import generate_password_hash

# Create an Admin user
admin = User(
    username="adminv1", password=generate_password_hash("admin1234"), role="Admin"
)

# Add to the database
db.session.add(admin)
db.session.commit()

print("Admin user created successfully!")
