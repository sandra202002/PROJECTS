from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import timedelta
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # "Admin", "Family", "Caregiver"
    status = db.Column(
        db.String(50), default="pending"
    )  # "pending", "approved", "rejected"

    # Common fields
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    profile_picture = db.Column(db.String(300), nullable=True)

    # Caregiver-specific fields
    experience = db.Column(db.Integer, nullable=True)
    certifications = db.Column(db.String(500), nullable=True)
    experience_file = db.Column(db.String(300), nullable=True)
    specialized_skills = db.Column(db.String(500), nullable=True)
    availability = db.Column(db.String(100), nullable=True)
    gender_preference = db.Column(db.String(50), nullable=True)
    hourly_rate = db.Column(db.Float, nullable=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caregiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    family_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    review_text = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    caregiver = db.relationship(
        "User", foreign_keys=[caregiver_id], backref="reviews_received"
    )
    family_user = db.relationship("User", foreign_keys=[family_user_id])


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caregiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    family_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default="scheduled")
    caregiver = db.relationship("User", foreign_keys=[caregiver_id])
    family_user = db.relationship("User", foreign_keys=[family_user_id])


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(
        db.Integer, db.ForeignKey("schedule.id"), nullable=False
    )  # Link to schedule
    caregiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    family_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True
    )  # Set after approval
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, approved, paid
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    caregiver = db.relationship("User", foreign_keys=[caregiver_id])
    family = db.relationship("User", foreign_keys=[family_id])
    schedule = db.relationship(
        "Schedule", backref="payments"
    )  # Establish a relationship
