from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
import joblib
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
import joblib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database and login manager
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load trained models
cardio_model = joblib.load("models/cardio_model.pkl")
stroke_model = joblib.load("models/stroke_model.pkl")
scaler = joblib.load("models/scaler.pkl")  # For stroke model normalization


# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # "Admin", "Family", "Caregiver"
    status = db.Column(
        db.String(50), default="pending"
    )  # "pending", "approved", "rejected"

    # Caregiver-specific fields
    experience = db.Column(db.Integer, nullable=True)
    certifications = db.Column(db.String(500), nullable=True)
    specialized_skills = db.Column(db.String(500), nullable=True)
    availability = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(200), nullable=True)
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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home Page
# Home Page - Redirect Based on Role
from datetime import timedelta


@app.route("/")
@login_required
def home():
    if current_user.role == "Admin":
        return redirect(url_for("admin_dashboard"))
    elif current_user.role == "Family":
        return render_template("dashboard_family.html")  # Family dashboard
    else:
        # Caregivers and others
        upcoming_schedules = Schedule.query.filter(
            Schedule.family_user_id == current_user.id,
            Schedule.start_time > datetime.now(),
            Schedule.start_time < datetime.now() + timedelta(days=1),
        ).all()

        if upcoming_schedules:
            flash("You have caregiving sessions scheduled for tomorrow!", "info")

        return render_template("dashboard_non_family.html")  # Caregiver dashboard


# Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(
            request.form["password"], method="pbkdf2:sha256"
        )
        role = request.form["role"]

        if role == "Caregiver":
            experience = request.form.get("experience")
            certifications = request.form.get("certifications")
            specialized_skills = ",".join(request.form.getlist("specialized_skills"))
            availability = request.form.get("availability")
            location = request.form.get("location")
            gender_preference = request.form.get("gender_preference")
            hourly_rate = request.form.get("hourly_rate")

            new_user = User(
                username=username,
                password=password,
                role=role,
                experience=experience,
                certifications=certifications,
                specialized_skills=specialized_skills,
                availability=availability,
                location=location,
                gender_preference=gender_preference,
                hourly_rate=hourly_rate,
                status="pending",
            )
        else:
            new_user = User(
                username=username, password=password, role=role, status="approved"
            )

        db.session.add(new_user)
        db.session.commit()
        flash(
            "Registration submitted. Caregiver accounts require admin approval.",
            "success",
        )
        return redirect(url_for("login"))

    return render_template("register.html")


# Admin Dashboard (View & Approve Caregivers)
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    pending_caregivers = User.query.filter_by(role="Caregiver", status="pending").all()
    approved_caregivers = User.query.filter_by(
        role="Caregiver", status="approved"
    ).all()

    return render_template(
        "admin_dashboard.html",
        pending_caregivers=pending_caregivers,
        approved_caregivers=approved_caregivers,
    )


# Approve Caregiver
@app.route("/approve_caregiver/<int:user_id>")
@login_required
def approve_caregiver(user_id):
    if current_user.role != "Admin":
        flash("Unauthorized action!", "danger")
        return redirect(url_for("home"))

    caregiver = User.query.get(user_id)
    if caregiver and caregiver.role == "Caregiver":
        caregiver.status = "approved"
        db.session.commit()
        flash(f"Caregiver {caregiver.username} approved!", "success")

    return redirect(url_for("admin_dashboard"))


# Reject Caregiver
@app.route("/reject_caregiver/<int:user_id>")
@login_required
def reject_caregiver(user_id):
    if current_user.role != "Admin":
        flash("Unauthorized action!", "danger")
        return redirect(url_for("home"))

    caregiver = User.query.get(user_id)
    if caregiver and caregiver.role == "Caregiver":
        caregiver.status = "rejected"
        db.session.commit()
        flash(f"Caregiver {caregiver.username} rejected.", "danger")

    return redirect(url_for("admin_dashboard"))


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if user.role == "Caregiver" and user.status == "pending":
                flash("Your account is pending approval by the admin.", "warning")
                return redirect(url_for("login"))
            elif user.role == "Caregiver" and user.status == "rejected":
                flash("Your caregiver registration was rejected.", "danger")
                return redirect(url_for("login"))
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")


# Cardiovascular Disease Prediction (Only for Family Users)
@app.route("/predict_cardio", methods=["POST", "GET"])
@login_required
def predict_cardio():
    if current_user.role != "Family":
        flash("Only Family users can access predictions.", "danger")
        return redirect(url_for("home"))  # Redirect to home

    try:
        # Get user input
        age = int(request.form["age"])
        gender = int(request.form["gender"])
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        ap_hi = int(request.form["ap_hi"])
        ap_lo = int(request.form["ap_lo"])
        cholesterol = int(request.form["cholesterol"])
        gluc = int(request.form["gluc"])
        smoke = int(request.form["smoke"])
        alco = int(request.form["alco"])
        active = int(request.form["active"])

        # Prepare input data
        user_input = np.array(
            [
                [
                    age,
                    gender,
                    height,
                    weight,
                    ap_hi,
                    ap_lo,
                    cholesterol,
                    gluc,
                    smoke,
                    alco,
                    active,
                ]
            ]
        )

        # Make prediction
        prediction = cardio_model.predict(user_input)[0]
        result = "Risk Detected" if prediction == 1 else "No Risk"

        return render_template(
            "predciton.html", cardio_result=result, stroke_result=None
        )

    except Exception as e:
        return render_template(
            "predciton.html", cardio_result=f"Error: {str(e)}", stroke_result=None
        )


# Stroke Prediction (Only for Family Users)
@app.route("/predict_stroke", methods=["POST", "GET"])
@login_required
def predict_stroke():
    if current_user.role != "Family":
        flash("Only Family users can access predictions.", "danger")
        return redirect(url_for("home"))  # Redirect to home

    try:
        # Get user input
        gender = request.form["gender"]
        age = int(request.form["age"])
        hypertension = int(request.form["hypertension"])
        heart_disease = int(request.form["heart_disease"])
        ever_married = request.form["ever_married"]
        work_type = request.form["work_type"]
        residence_type = request.form["residence_type"]
        avg_glucose_level = float(request.form["avg_glucose_level"])
        bmi = float(request.form["bmi"])
        smoking_status = request.form["smoking_status"]

        # Convert categorical values to match model training
        mapping = {
            "gender": {"Male": 1, "Female": 0},
            "ever_married": {"Yes": 1, "No": 0},
            "work_type": {
                "Private": 0,
                "Self-employed": 1,
                "Govt_job": 2,
                "children": 3,
                "Never_worked": 4,
            },
            "residence_type": {"Urban": 1, "Rural": 0},
            "smoking_status": {"never smoked": 0, "formerly smoked": 1, "smokes": 2},
        }

        # Encode categorical values
        gender = mapping["gender"].get(gender, 0)
        ever_married = mapping["ever_married"].get(ever_married, 0)
        work_type = mapping["work_type"].get(work_type, 0)
        residence_type = mapping["residence_type"].get(residence_type, 0)
        smoking_status = mapping["smoking_status"].get(smoking_status, 0)

        # Prepare input data
        user_input = pd.DataFrame(
            [
                [
                    gender,
                    age,
                    hypertension,
                    heart_disease,
                    ever_married,
                    work_type,
                    residence_type,
                    avg_glucose_level,
                    bmi,
                    smoking_status,
                ]
            ],
            columns=[
                "gender",
                "age",
                "hypertension",
                "heart_disease",
                "ever_married",
                "work_type",
                "Residence_type",
                "avg_glucose_level",
                "bmi",
                "smoking_status",
            ],
        )

        # Normalize numerical values using the saved scaler
        user_input[["age", "avg_glucose_level", "bmi"]] = scaler.transform(
            user_input[["age", "avg_glucose_level", "bmi"]]
        )

        # Make prediction
        prediction = stroke_model.predict(user_input)[0]
        result = "Risk Detected" if prediction == 1 else "No Risk"

        return render_template(
            "prediciton2.html", stroke_result=result, cardio_result=None
        )

    except Exception as e:
        return render_template(
            "prediciton2.html", stroke_result=f"Error: {str(e)}", cardio_result=None
        )


# Search Caregivers (Only for Family Users)
@app.route("/search_caregivers", methods=["GET", "POST"])
@login_required
def search_caregivers():
    if current_user.role != "Family":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    caregivers = User.query.filter_by(role="Caregiver", status="approved").all()

    if request.method == "POST":
        experience = request.form.get("experience")
        certifications = request.form.get("certifications")
        specialized_skills = request.form.getlist(
            "specialized_skills"
        )  # List of selected skills
        availability = request.form.get("availability")
        location = request.form.get("location")
        gender_preference = request.form.get("gender_preference")
        hourly_rate = request.form.get("hourly_rate")

        query = User.query.filter_by(role="Caregiver", status="approved")

        if experience:
            query = query.filter(User.experience >= int(experience))
        if certifications:
            query = query.filter(User.certifications.ilike(f"%{certifications}%"))
        if specialized_skills:
            for skill in specialized_skills:
                query = query.filter(User.specialized_skills.ilike(f"%{skill}%"))
        if availability:
            query = query.filter(User.availability == availability)
        if location:
            query = query.filter(User.location.ilike(f"%{location}%"))
        if gender_preference:
            query = query.filter(User.gender_preference == gender_preference)
        if hourly_rate:
            query = query.filter(User.hourly_rate <= float(hourly_rate))

        caregivers = query.all()

    return render_template("search.html", caregivers=caregivers)


@app.route("/caregiver/<int:caregiver_id>/review", methods=["POST"])
@login_required
def submit_review(caregiver_id):
    if current_user.role != "Family":
        flash("Only Family users can submit reviews.", "danger")
        return redirect(url_for("home"))

    rating = int(request.form["rating"])
    review_text = request.form.get("review_text", "")

    existing_review = Review.query.filter_by(
        family_user_id=current_user.id, caregiver_id=caregiver_id
    ).first()
    if existing_review:
        flash("You have already reviewed this caregiver.", "warning")
        return redirect(url_for("view_caregiver", caregiver_id=caregiver_id))

    new_review = Review(
        caregiver_id=caregiver_id,
        family_user_id=current_user.id,
        rating=rating,
        review_text=review_text,
    )
    db.session.add(new_review)
    db.session.commit()

    flash("Review submitted successfully!", "success")
    return redirect(url_for("view_caregiver", caregiver_id=caregiver_id))


@app.route("/caregiver/<int:caregiver_id>", methods=["GET"])
@login_required
def view_caregiver(caregiver_id):
    caregiver = User.query.get_or_404(caregiver_id)
    reviews = Review.query.filter_by(caregiver_id=caregiver_id).all()
    avg_rating = (
        np.mean([review.rating for review in reviews]) if reviews else 0
    )  # Calculate average rating
    return render_template(
        "caregiver_profile.html",
        caregiver=caregiver,
        reviews=reviews,
        avg_rating=avg_rating,
    )


@app.route("/update_availability", methods=["GET", "POST"])
@login_required
def update_availability():
    if current_user.role != "Caregiver":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        availability = request.form["availability"]

        # Optional: Validate the format of availability (ensure it is a valid datetime)
        try:
            # Example: Ensure caregiver inputs availability in the correct format (for example, "YYYY-MM-DDTHH:MM")
            datetime.strptime(availability, "%Y-%m-%dT%H:%M")
            current_user.availability = availability
            db.session.commit()
            flash("Availability updated successfully!", "success")
        except ValueError:
            flash(
                "Invalid availability format. Please use 'YYYY-MM-DDTHH:MM' format.",
                "danger",
            )

        return redirect(url_for("home"))

    return render_template("update_availability.html")


from datetime import datetime


@app.route("/schedule_session", methods=["GET", "POST"])
@login_required
def schedule_session():
    if current_user.role != "Family":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    caregivers = User.query.filter_by(role="Caregiver", status="approved").all()

    if request.method == "POST":
        caregiver_id = int(request.form["caregiver_id"])
        start_time = datetime.strptime(request.form["start_time"], "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(request.form["end_time"], "%Y-%m-%dT%H:%M")
        caregiver = User.query.get(caregiver_id)

        if caregiver:
            # Check if caregiver is available
            if caregiver.availability and start_time >= datetime.strptime(
                caregiver.availability, "%Y-%m-%dT%H:%M"
            ):
                # Create a new scheduled session with "scheduled" status
                new_schedule = Schedule(
                    caregiver_id=caregiver.id,
                    family_user_id=current_user.id,
                    start_time=start_time,
                    end_time=end_time,
                )
                db.session.add(new_schedule)
                db.session.commit()

                flash(
                    "Caregiving session scheduled successfully! Awaiting caregiver's response.",
                    "success",
                )
                return redirect(url_for("home"))
            else:
                flash("The caregiver is not available at this time.", "danger")
                return redirect(url_for("schedule_session"))

    return render_template("schedule_session.html", caregivers=caregivers)


@app.route("/view_family_schedule", methods=["GET"])
@login_required
def view_family_schedule():
    if current_user.role != "Family":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    # Get all scheduled sessions for the current family user
    family_schedules = Schedule.query.filter_by(family_user_id=current_user.id).all()

    return render_template("view_family_schedule.html", schedules=family_schedules)


@app.route("/view_caregiver_schedule", methods=["GET", "POST"])
@login_required
def view_caregiver_schedule():
    if current_user.role != "Caregiver":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    # Get all scheduled sessions for the current caregiver
    caregiver_schedules = Schedule.query.filter_by(caregiver_id=current_user.id).all()

    if request.method == "POST":
        # Get action (accept or reject) and schedule ID from the form
        schedule_id = int(request.form["schedule_id"])
        action = request.form["action"]

        # Find the session to update
        session = Schedule.query.get(schedule_id)

        if session:
            if action == "accept":
                session.status = "accepted"
            elif action == "reject":
                session.status = "rejected"

            db.session.commit()
            flash(f"Session has been {action}ed.", "success")

        return redirect(url_for("view_caregiver_schedule"))

    return render_template(
        "view_caregiver_schedule.html", schedules=caregiver_schedules
    )


@app.route("/accept_schedule/<int:schedule_id>")
@login_required
def accept_schedule(schedule_id):
    if current_user.role != "Caregiver":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    schedule = Schedule.query.get(schedule_id)

    if not schedule:
        flash("Schedule not found!", "danger")
        return redirect(url_for("view_caregiver_schedule"))

    if schedule.caregiver_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for("view_caregiver_schedule"))

    # Update the schedule's status to "accepted"
    schedule.status = "accepted"
    db.session.commit()

    flash("You have accepted the caregiving session.", "success")
    return redirect(url_for("view_caregiver_schedule"))


@app.route("/reject_schedule/<int:schedule_id>")
@login_required
def reject_schedule(schedule_id):
    if current_user.role != "Caregiver":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    schedule = Schedule.query.get(schedule_id)

    if not schedule:
        flash("Schedule not found!", "danger")
        return redirect(url_for("view_caregiver_schedule"))

    if schedule.caregiver_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for("view_caregiver_schedule"))

    # Update the schedule's status to "rejected"
    schedule.status = "rejected"
    db.session.commit()

    flash("You have rejected the caregiving session.", "danger")
    return redirect(url_for("view_caregiver_schedule"))


# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
