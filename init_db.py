"""
Initializes the SQLite database and seeds it with sample data:
  - 1 admin account
  - 1 demo user account
  - Sample destinations, hotels, transport options and tour packages

Run this once before starting the app for the first time:
    python init_db.py
"""
from app import app
from models import db, User, Destination, Hotel, Transport, Package


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ---- Admin account ----
        admin = User(name="System Admin", email="admin@smarttourism.com", role="admin")
        admin.set_password("Admin@123")
        db.session.add(admin)

        # ---- Demo user account ----
        demo_user = User(name="Praveen Kumar", email="user@smarttourism.com",
                          phone="9876543210", role="user")
        demo_user.set_password("User@123")
        db.session.add(demo_user)

        # ---- Destinations ----
        destinations_data = [
            ("Goa Beaches", "Goa, India",
             "Golden beaches, vibrant nightlife, Portuguese heritage and water sports."),
            ("Munnar Hills", "Kerala, India",
             "Rolling tea plantations, misty mountains and cool weather retreats."),
            ("Jaipur Heritage", "Rajasthan, India",
             "The Pink City, home to majestic forts, palaces and royal history."),
            ("Kashmir Valley", "Jammu & Kashmir, India",
             "Snow-capped mountains, serene lakes and the 'Paradise on Earth'."),
            ("Andaman Islands", "Andaman & Nicobar, India",
             "Crystal clear waters, coral reefs and pristine tropical beaches."),
            ("Manali Adventure", "Himachal Pradesh, India",
             "Snow trekking, river rafting and scenic Himalayan views."),
        ]
        destinations = []
        for name, location, desc in destinations_data:
            d = Destination(name=name, location=location, description=desc)
            db.session.add(d)
            destinations.append(d)
        db.session.flush()  # get IDs

        # ---- Hotels ----
        hotels_data = [
            ("Sea Pearl Resort", "Goa, India", 4500, 4.3),
            ("Tea Valley Retreat", "Munnar, Kerala", 3200, 4.5),
            ("Royal Heritage Palace", "Jaipur, Rajasthan", 5200, 4.7),
            ("Dal Lake View Hotel", "Srinagar, Kashmir", 4000, 4.4),
            ("Coral Bay Resort", "Havelock, Andaman", 6000, 4.6),
            ("Snow Peak Cottages", "Manali, Himachal Pradesh", 3500, 4.2),
        ]
        hotels = []
        for name, location, price, rating in hotels_data:
            h = Hotel(name=name, location=location, price_per_night=price, rating=rating)
            db.session.add(h)
            hotels.append(h)
        db.session.flush()

        # ---- Transport ----
        transport_data = [
            ("Flight", "Economy Class Flight", 5500),
            ("Train", "AC 2-Tier Train", 1800),
            ("Bus", "Volvo AC Sleeper Bus", 1200),
            ("Cab", "Private Cab (Round Trip)", 3000),
        ]
        transport_options = []
        for t_type, name, price in transport_data:
            t = Transport(type=t_type, name=name, price=price)
            db.session.add(t)
            transport_options.append(t)
        db.session.flush()

        # ---- Tour Packages ----
        packages_data = [
            ("Goa Beach Getaway", 0, 0, 0, 12999, 4,
             "3 nights / 4 days beach holiday with resort stay, breakfast and water sports."),
            ("Munnar Hill Escape", 1, 1, 2, 9999, 3,
             "Explore tea gardens, waterfalls and Eravikulam National Park."),
            ("Royal Rajasthan Tour", 2, 2, 0, 18999, 5,
             "Visit Amber Fort, City Palace and Hawa Mahal with heritage stay."),
            ("Kashmir Paradise Tour", 3, 3, 0, 24999, 6,
             "Houseboat stay on Dal Lake, Gulmarg gondola ride and Pahalgam valley."),
            ("Andaman Island Bliss", 4, 4, 0, 21999, 5,
             "Scuba diving, Radhanagar Beach and Cellular Jail heritage tour."),
            ("Manali Snow Adventure", 5, 5, 2, 14999, 4,
             "Solang Valley snow activities, Rohtang Pass and river rafting."),
        ]
        for name, dest_idx, hotel_idx, transport_idx, price, days, desc in packages_data:
            p = Package(
                name=name,
                destination_id=destinations[dest_idx].id,
                hotel_id=hotels[hotel_idx].id,
                transport_id=transport_options[transport_idx].id,
                description=desc,
                price=price,
                duration_days=days,
            )
            db.session.add(p)

        db.session.commit()
        print("Database initialized and seeded successfully!")
        print("-" * 50)
        print("Admin Login  -> email: admin@smarttourism.com | password: Admin@123")
        print("Demo User    -> email: user@smarttourism.com  | password: User@123")
        print("-" * 50)


if __name__ == "__main__":
    seed()
