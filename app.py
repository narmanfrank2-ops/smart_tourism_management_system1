"""
Smart Tourism Management System
--------------------------------
A web-based application to help tourists explore destinations, book tour
packages, make (mock) payments, and track bookings. Includes an Admin
module to manage packages, hotels, transport and view all user bookings.

Tech stack (per project abstract):
  Front-End : HTML, CSS, JavaScript (Jinja2 templates)
  Back-End  : Python (Flask)
  Database  : SQLite
"""
import os
import random
import string
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)

from models import db, User, Destination, Hotel, Transport, Package, Booking, Payment

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "smart-tourism-secret-key-change-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "tourism.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ---------------------------------------------------------------------------
# Helpers / decorators
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


def current_user():
    uid = session.get("user_id")
    if uid:
        return User.query.get(uid)
    return None


@app.context_processor
def inject_globals():
    return {"current_user": current_user(), "current_year": datetime.now().year}


def generate_txn_ref():
    return "TXN" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


# ---------------------------------------------------------------------------
# Public / User Module
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    destinations = Destination.query.limit(6).all()
    packages = Package.query.limit(6).all()
    return render_template("index.html", destinations=destinations, packages=packages)


@app.route("/destinations")
def destinations():
    """Search Tourist Places."""
    query = request.args.get("q", "").strip()
    if query:
        dests = Destination.query.filter(
            (Destination.name.ilike(f"%{query}%")) |
            (Destination.location.ilike(f"%{query}%"))
        ).all()
    else:
        dests = Destination.query.all()
    return render_template("destinations.html", destinations=dests, query=query)


@app.route("/destinations/<int:dest_id>")
def destination_detail(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    packages = Package.query.filter_by(destination_id=dest_id).all()
    return render_template("destination_detail.html", destination=dest, packages=packages)


@app.route("/packages")
def packages():
    all_packages = Package.query.all()
    return render_template("packages.html", packages=all_packages)


@app.route("/packages/<int:package_id>")
def package_detail(package_id):
    pkg = Package.query.get_or_404(package_id)
    return render_template("package_detail.html", package=pkg)


# ---- Registration / Login ---------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("register"))

        user = User(name=name, email=email, phone=phone, role="user")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email, role="user").first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role
            session["name"] = user.name
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---- Booking Module ----------------------------------------------------------
@app.route("/book/<int:package_id>", methods=["GET", "POST"])
@login_required
def book_package(package_id):
    pkg = Package.query.get_or_404(package_id)

    if request.method == "POST":
        travel_date = request.form.get("travel_date")
        num_travelers = int(request.form.get("num_travelers", 1))

        if not travel_date or num_travelers < 1:
            flash("Please provide a valid travel date and number of travelers.", "danger")
            return redirect(url_for("book_package", package_id=package_id))

        total_amount = pkg.price * num_travelers
        booking = Booking(
            user_id=session["user_id"],
            package_id=pkg.id,
            travel_date=travel_date,
            num_travelers=num_travelers,
            total_amount=total_amount,
            status="Pending Payment"
        )
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for("payment", booking_id=booking.id))

    return render_template("book_package.html", package=pkg)


@app.route("/payment/<int:booking_id>", methods=["GET", "POST"])
@login_required
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session["user_id"]:
        flash("You are not authorized to view this booking.", "danger")
        return redirect(url_for("my_bookings"))

    if booking.status != "Pending Payment":
        return redirect(url_for("booking_confirmation", booking_id=booking.id))

    if request.method == "POST":
        method = request.form.get("payment_method", "Card")
        pay = Payment(
            booking_id=booking.id,
            amount=booking.total_amount,
            method=method,
            status="Success",
            transaction_ref=generate_txn_ref()
        )
        booking.status = "Confirmed"
        db.session.add(pay)
        db.session.commit()
        flash("Payment successful! Your booking is confirmed.", "success")
        return redirect(url_for("booking_confirmation", booking_id=booking.id))

    return render_template("payment.html", booking=booking)


@app.route("/booking/confirmation/<int:booking_id>")
@login_required
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session["user_id"] and session.get("role") != "admin":
        flash("You are not authorized to view this booking.", "danger")
        return redirect(url_for("my_bookings"))
    return render_template("booking_confirmation.html", booking=booking)


@app.route("/my-bookings")
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=session["user_id"]).order_by(Booking.created_at.desc()).all()
    return render_template("my_bookings.html", bookings=bookings)


@app.route("/booking/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session["user_id"]:
        flash("You are not authorized to modify this booking.", "danger")
        return redirect(url_for("my_bookings"))
    booking.status = "Cancelled"
    db.session.commit()
    flash("Booking cancelled.", "info")
    return redirect(url_for("my_bookings"))


# ---------------------------------------------------------------------------
# Admin Module
# ---------------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        admin = User.query.filter_by(email=email, role="admin").first()

        if admin and admin.check_password(password):
            session["user_id"] = admin.id
            session["role"] = "admin"
            session["name"] = admin.name
            flash("Welcome to the Admin Dashboard.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials.", "danger")
        return redirect(url_for("admin_login"))

    return render_template("admin/admin_login.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    stats = {
        "total_users": User.query.filter_by(role="user").count(),
        "total_packages": Package.query.count(),
        "total_bookings": Booking.query.count(),
        "total_revenue": db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0)).scalar(),
    }
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_bookings=recent_bookings)


# ---- Manage Tour Packages ----
@app.route("/admin/packages", methods=["GET", "POST"])
@admin_required
def admin_packages():
    if request.method == "POST":
        pkg = Package(
            name=request.form["name"],
            destination_id=request.form["destination_id"],
            hotel_id=request.form.get("hotel_id") or None,
            transport_id=request.form.get("transport_id") or None,
            description=request.form.get("description", ""),
            price=float(request.form["price"]),
            duration_days=int(request.form["duration_days"]),
        )
        db.session.add(pkg)
        db.session.commit()
        flash("Tour package added.", "success")
        return redirect(url_for("admin_packages"))

    all_packages = Package.query.all()
    all_destinations = Destination.query.all()
    all_hotels = Hotel.query.all()
    all_transport = Transport.query.all()
    return render_template(
        "admin/manage_packages.html",
        packages=all_packages, destinations=all_destinations,
        hotels=all_hotels, transport=all_transport
    )


@app.route("/admin/packages/edit/<int:package_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_package(package_id):
    pkg = Package.query.get_or_404(package_id)
    if request.method == "POST":
        pkg.name = request.form["name"]
        pkg.destination_id = request.form["destination_id"]
        pkg.hotel_id = request.form.get("hotel_id") or None
        pkg.transport_id = request.form.get("transport_id") or None
        pkg.description = request.form.get("description", "")
        pkg.price = float(request.form["price"])
        pkg.duration_days = int(request.form["duration_days"])
        db.session.commit()
        flash("Tour package updated.", "success")
        return redirect(url_for("admin_packages"))

    all_destinations = Destination.query.all()
    all_hotels = Hotel.query.all()
    all_transport = Transport.query.all()
    return render_template(
        "admin/edit_package.html", package=pkg,
        destinations=all_destinations, hotels=all_hotels, transport=all_transport
    )


@app.route("/admin/packages/delete/<int:package_id>", methods=["POST"])
@admin_required
def admin_delete_package(package_id):
    pkg = Package.query.get_or_404(package_id)
    db.session.delete(pkg)
    db.session.commit()
    flash("Tour package deleted.", "info")
    return redirect(url_for("admin_packages"))


# ---- Manage Hotels ----
@app.route("/admin/hotels", methods=["GET", "POST"])
@admin_required
def admin_hotels():
    if request.method == "POST":
        hotel = Hotel(
            name=request.form["name"],
            location=request.form["location"],
            price_per_night=float(request.form["price_per_night"]),
            rating=float(request.form.get("rating", 4.0)),
        )
        db.session.add(hotel)
        db.session.commit()
        flash("Hotel added.", "success")
        return redirect(url_for("admin_hotels"))

    all_hotels = Hotel.query.all()
    return render_template("admin/manage_hotels.html", hotels=all_hotels)


@app.route("/admin/hotels/delete/<int:hotel_id>", methods=["POST"])
@admin_required
def admin_delete_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    db.session.delete(hotel)
    db.session.commit()
    flash("Hotel removed.", "info")
    return redirect(url_for("admin_hotels"))


# ---- Manage Transport ----
@app.route("/admin/transport", methods=["GET", "POST"])
@admin_required
def admin_transport():
    if request.method == "POST":
        t = Transport(
            type=request.form["type"],
            name=request.form["name"],
            price=float(request.form["price"]),
        )
        db.session.add(t)
        db.session.commit()
        flash("Transport option added.", "success")
        return redirect(url_for("admin_transport"))

    all_transport = Transport.query.all()
    return render_template("admin/manage_transport.html", transport=all_transport)


@app.route("/admin/transport/delete/<int:transport_id>", methods=["POST"])
@admin_required
def admin_delete_transport(transport_id):
    t = Transport.query.get_or_404(transport_id)
    db.session.delete(t)
    db.session.commit()
    flash("Transport option removed.", "info")
    return redirect(url_for("admin_transport"))


# ---- View All User Bookings ----
@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    status_filter = request.args.get("status", "")
    query = Booking.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_bookings = query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/view_bookings.html", bookings=all_bookings, status_filter=status_filter)


@app.route("/admin/bookings/update-status/<int:booking_id>", methods=["POST"])
@admin_required
def admin_update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get("status")
    if new_status in ["Pending Payment", "Confirmed", "Completed", "Cancelled"]:
        booking.status = new_status
        db.session.commit()
        flash("Booking status updated.", "success")
    return redirect(url_for("admin_bookings"))


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
