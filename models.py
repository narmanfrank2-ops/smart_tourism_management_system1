"""
Smart Tourism Management System
Database Models (SQLite via SQLAlchemy)
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Users table - handles both normal users and admin (role field)."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"


class Destination(db.Model):
    """Tourist destinations."""
    __tablename__ = "destinations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300), default="/static/images/default_destination.jpg")

    packages = db.relationship("Package", backref="destination", lazy=True)


class Hotel(db.Model):
    """Hotels available for a destination."""
    __tablename__ = "hotels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, default=4.0)

    packages = db.relationship("Package", backref="hotel", lazy=True)


class Transport(db.Model):
    """Transportation options."""
    __tablename__ = "transport"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)   # Flight / Train / Bus / Cab
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)

    packages = db.relationship("Package", backref="transport", lazy=True)


class Package(db.Model):
    """Tour packages - combine a destination, hotel and transport option."""
    __tablename__ = "packages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotels.id"))
    transport_id = db.Column(db.Integer, db.ForeignKey("transport.id"))
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False, default=3)
    image_url = db.Column(db.String(300), default="/static/images/default_package.jpg")

    bookings = db.relationship("Booking", backref="package", lazy=True)


class Booking(db.Model):
    """A user's booking of a tour package."""
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"), nullable=False)
    travel_date = db.Column(db.String(20), nullable=False)
    num_travelers = db.Column(db.Integer, nullable=False, default=1)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending Payment")
    # Pending Payment -> Confirmed -> Completed / Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payment = db.relationship("Payment", backref="booking", uselist=False, lazy=True)


class Payment(db.Model):
    """Payment details for a booking (mock/demo payment gateway)."""
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Success")
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_ref = db.Column(db.String(50))
