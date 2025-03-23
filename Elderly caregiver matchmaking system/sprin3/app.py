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
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
import joblib
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from models import db, User, Review, Schedule, Payment
from datetime import timedelta
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
cardio_model = joblib.load("models/cardio_model.pkl")
stroke_model = joblib.load("models/stroke_model.pkl")
scaler = joblib.load("models/scaler.pkl")
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
@login_required
def home():
    if current_user.role == "Admin":

        return redirect(url_for("admin_dashboard"))
    elif current_user.role == "Family":
        return render_template("home/famhome.html", family=current_user)
    elif current_user.role == "Caregiver":

        upcoming_schedules = Schedule.query.filter(
            Schedule.caregiver_id == current_user.id,
            Schedule.status == "accepted",
            Schedule.start_time > datetime.now(),
        ).all()

        if upcoming_schedules:
            flash("You have upcoming caregiving sessions!", "info")

        return render_template("home/cghome.html", caregiver=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(
            request.form["password"], method="pbkdf2:sha256"
        )
        role = request.form["role"]
        phone = request.form.get("phone")
        location = request.form.get("location")
        gender = request.form.get("gender")
        age = request.form.get("age")

        if role == "Caregiver":
            experience = request.form.get("experience")
            certifications = request.form.get("certifications")
            specialized_skills_list = request.form.getlist("specialized_skills[]")
            specialized_skills = (
                ",".join(specialized_skills_list) if specialized_skills_list else None
            )
            availability = request.form.get("availability")
            gender_preference = request.form.get("gender_preference")
            hourly_rate = request.form.get("hourly_rate")

            experience_file = request.files.get("experience_file")
            filename = None
            if experience_file:
                filename = f"uploads/{experience_file.filename}"
                experience_file.save(os.path.join("static", filename))

            new_user = User(
                username=username,
                password=password,
                role=role,
                phone=phone,
                location=location,
                gender=gender,
                age=int(age) if age else None,
                experience=experience,
                certifications=certifications,
                specialized_skills=specialized_skills,
                experience_file=filename,
                availability=availability,
                gender_preference=gender_preference,
                hourly_rate=float(hourly_rate) if hourly_rate else None,
                status="pending",
            )
        else:
            new_user = User(
                username=username,
                password=password,
                role=role,
                phone=phone,
                location=location,
                gender=gender,
                age=int(age) if age else None,
                status="approved",
            )

        db.session.add(new_user)
        db.session.commit()
        flash(
            "Registration submitted. Caregiver accounts require admin approval.",
            "success",
        )
        return redirect(url_for("login"))

    return render_template("home/register.html")


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
        specialized_skills = request.form.getlist("specialized_skills")
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

    return render_template("home/searchcg.html", caregivers=caregivers)


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
    caregivers = User.query.filter_by(role="Caregiver").all()
    reviews = Review.query.filter_by(caregiver_id=caregiver_id).all()
    avg_rating = np.mean([review.rating for review in reviews]) if reviews else 0
    print("Caregivers Data:", caregivers)
    return render_template(
        "home/caregiver_profile.html",
        caregivers=caregivers,
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

        try:

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

    return render_template("home/update_availability.html")


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

            if caregiver.availability and start_time >= datetime.strptime(
                caregiver.availability, "%Y-%m-%dT%H:%M"
            ):

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

    return render_template("home/schedule_session.html", caregivers=caregivers)


@app.route("/view_family_schedule", methods=["GET"])
@login_required
def view_family_schedule():
    if current_user.role != "Family":
        flash("Unauthorized access!", "danger")

        return redirect(url_for("home"))

    family_schedules = Schedule.query.filter(
        Schedule.family_user_id == current_user.id,
        Schedule.status.in_(["scheduled", "accepted", "paid"]),
    ).all()

    print("Retrieved schedules for family:", len(family_schedules))
    for s in family_schedules:
        print(f"ID: {s.id}, Status: {s.status}, Caregiver ID: {s.caregiver_id}")

    return render_template(
        "/home/famindex.html",
        schedules=family_schedules,
    )


@app.route("/view_caregiver_schedule", methods=["GET"])
@login_required
def view_caregiver_schedule():
    if current_user.role != "Caregiver":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    caregiver_schedules = (
        db.session.query(Schedule)
        .outerjoin(Payment, Schedule.id == Payment.schedule_id)
        .filter(
            Schedule.caregiver_id == current_user.id,
            Schedule.status.in_(["scheduled", "accepted"]),
            db.or_(Payment.id == None, Payment.status != "paid"),
        )
        .all()
    )

    return render_template("home/indexcg.html", schedules=caregiver_schedules)


@app.route("/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():
    if request.method == "POST":
        current_user.username = request.form["username"]
        current_user.email = request.form["email"]

        certification_file = request.files.get("certification")
        if certification_file and certification_file.filename:
            cert_filename = secure_filename(certification_file.filename)
            cert_path = os.path.join(app.config["UPLOAD_FOLDER"], cert_filename)
            certification_file.save(cert_path)
            current_user.certifications = f"uploads/{cert_filename}"

        experience_file = request.files.get("experience")
        if experience_file and experience_file.filename:
            exp_filename = secure_filename(experience_file.filename)
            exp_path = os.path.join(app.config["UPLOAD_FOLDER"], exp_filename)
            experience_file.save(exp_path)
            current_user.experience_file = f"uploads/{exp_filename}"
        profile_picture = request.files.get("profile_picture")
        if profile_picture and profile_picture.filename:
            pic_filename = secure_filename(profile_picture.filename)
            pic_path = os.path.join(app.config["UPLOAD_FOLDER"], pic_filename)
            profile_picture.save(pic_path)
            current_user.profile_picture = f"uploads/{pic_filename}"

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("update_profile"))

    return render_template("home/update_profile.html", user=current_user)


@app.route("/accept_schedule/<int:schedule_id>", methods=["POST"])
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

    schedule.status = "accepted"
    db.session.commit()

    flash("You have accepted the caregiving session.", "success")
    return redirect(url_for("view_caregiver_schedule"))


@app.route("/reject_schedule/<int:schedule_id>", methods=["POST"])
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

    schedule.status = "rejected"
    db.session.commit()

    flash("You have rejected the caregiving session.", "danger")
    return redirect(url_for("view_caregiver_schedule"))


@app.route("/request_payout/<int:schedule_id>", methods=["POST"])
@login_required
def request_payout(
    schedule_id,
):
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

    amount = float(request.form["amount"])
    if amount <= 0:
        flash("Invalid amount!", "danger")
        return redirect(url_for("view_caregiver_schedule"))

    new_payout = Payment(
        schedule_id=schedule.id,
        caregiver_id=current_user.id,
        amount=amount,
        status="pending",
    )
    db.session.add(new_payout)
    db.session.commit()

    flash("Payout request submitted!", "success")
    return redirect(url_for("view_earnings"))


@app.route("/approve_payout/<int:payment_id>", methods=["POST"])
@login_required
def approve_payout(payment_id):
    if current_user.role != "Family":
        flash("Unauthorized action!", "danger")
        return redirect(url_for("home"))

    payment = Payment.query.get(payment_id)
    if not payment or payment.status != "pending":
        flash("Invalid payout request!", "danger")
        return redirect(url_for("view_pending_payouts"))

    payment.status = "approved"
    payment.family_id = current_user.id
    db.session.commit()

    flash("Payout approved! Proceed with payment.", "success")
    return redirect(url_for("view_pending_payouts"))


@app.route("/view_earnings")
@login_required
def view_earnings():
    total_earnings = get_total_earnings(current_user.id)

    if current_user.role != "Caregiver":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    earnings = Payment.query.filter_by(
        caregiver_id=current_user.id, status="approved"
    ).all()
    total_earnings = get_total_earnings(current_user.id)
    print("Total Earnings:", total_earnings)

    return render_template(
        "home/view_earnings.html", earnings=earnings, total_earnings=total_earnings
    )


@app.route("/view_pending_payouts")
@login_required
def view_pending_payouts():
    if current_user.role != "Family":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("home"))

    pending_payouts = Payment.query.filter_by(status="pending").all()

    return render_template("home/pending_payouts.html", payouts=pending_payouts)


def get_total_earnings(caregiver_id):
    total = (
        db.session.query(db.func.sum(Payment.amount))
        .filter(
            Payment.caregiver_id == caregiver_id,
            Payment.status == "approved",
        )
        .scalar()
    )
    return total if total else 0.0


@app.route("/predict_cardio", methods=["POST", "GET"])
@login_required
def predict_cardio():
    if current_user.role != "Family":
        flash("Only Family users can access predictions.", "danger")
        return redirect(url_for("home"))

    try:

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

        prediction = cardio_model.predict(user_input)[0]
        result = "Risk Detected" if prediction == 1 else "No Risk"

        return render_template(
            "home/index1.html", cardio_result=result, stroke_result=None
        )

    except Exception as e:
        return render_template(
            "home/index1.html", cardio_result=f"Error: {str(e)}", stroke_result=None
        )


@app.route("/predict_stroke", methods=["POST", "GET"])
@login_required
def predict_stroke():
    if current_user.role != "Family":
        flash("Only Family users can access predictions.", "danger")
        return redirect(url_for("home"))

    try:

        stroke_model = joblib.load("models/stroke_model2.pkl")
        scaler = joblib.load("models/scaler2.pkl")

        gender = request.form["gender"]
        age = int(request.form["age"])
        ever_married = request.form["ever_married"]
        work_type = request.form["work_type"]
        residence_type = request.form["residence_type"]
        avg_glucose_level = float(request.form["avg_glucose_level"])
        bmi = float(request.form["bmi"])
        smoking_status = request.form["smoking_status"]

        print("\n🔹 Original Input Data:")
        print(
            f"Gender: {gender}, Age: {age}, Married: {ever_married}, Work: {work_type}, Residence: {residence_type}, Glucose: {avg_glucose_level}, BMI: {bmi}, Smoking: {smoking_status}\n"
        )

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
            "Residence_type": {"Urban": 1, "Rural": 0},
            "smoking_status": {
                "never smoked": 0,
                "formerly smoked": 1,
                "smokes": 2,
                "unknown": 3,
            },
        }

        gender = mapping["gender"].get(gender, 0)
        ever_married = mapping["ever_married"].get(ever_married, 0)
        work_type = mapping["work_type"].get(work_type, 0)
        residence_type = mapping["Residence_type"].get(residence_type, 0)
        smoking_status = mapping["smoking_status"].get(smoking_status, 0)

        print("Encoded Input Values:")
        print(
            f"Gender: {gender}, Age: {age}, Married: {ever_married}, Work: {work_type}, Residence: {residence_type}, Glucose: {avg_glucose_level}, BMI: {bmi}, Smoking: {smoking_status}\n"
        )

        user_input = pd.DataFrame(
            [
                [
                    gender,
                    age,
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
                "ever_married",
                "work_type",
                "Residence_type",
                "avg_glucose_level",
                "bmi",
                "smoking_status",
            ],
        )

        user_input[["age", "avg_glucose_level", "bmi"]] = scaler.transform(
            user_input[["age", "avg_glucose_level", "bmi"]]
        )

        print(" Normalized Input Values:")
        print(user_input.to_string(index=False))

        prob = stroke_model.predict_proba(user_input)[0][1]
        threshold = 0.2
        prediction = "Risk Detected" if prob > threshold else "No Risk"

        print(f"\n Prediction Probability: {prob:.4f} (Threshold: {threshold})")
        print(f" Final Prediction: {prediction}\n")

        return render_template(
            "home/index2.html", stroke_result=prediction, cardio_result=None
        )

    except Exception as e:
        print(f" Error: {str(e)}")
        return render_template(
            "home/index2.html", stroke_result=f"Error: {str(e)}", cardio_result=None
        )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
