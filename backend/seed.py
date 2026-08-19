from datetime import date, timedelta, datetime
from database import db
from models import User, Trek, Booking, Notification

def seed_database_if_empty():
    """
    Programmatic Database Initialization:
    Ensures pre-existing superuser Admin exists without any registration requirement,
    along with representative sample staff, treks, bookings, and notifications.
    """
    # Check if admin already exists
    admin_exists = User.query.filter_by(role='admin').first()
    if admin_exists:
        return

    print("[DATABASE SEED] Initializing database and creating pre-existing Admin...")

    # 1. Create Pre-existing Superuser Admin (Only one allowed)
    admin = User(
        username="admin",
        email="admin@trekma.com",
        name="Chief Trek Director (Superuser Admin)",
        contact_no="+91 98765 43210",
        role="admin",
        is_active=True,
        is_blacklisted=False
    )
    admin.set_password("Admin@123")
    db.session.add(admin)

    # 2. Create Initial Staff Members
    staff1 = User(
        username="staff_alex",
        email="alex@trekma.com",
        name="Alex Rivera",
        contact_no="+91 91234 56780",
        role="staff",
        specialization="High Altitude Alpine Specialist & WFR Certified",
        experience_years=7,
        is_active=True,
        is_blacklisted=False
    )
    staff1.set_password("Staff@123")

    staff2 = User(
        username="staff_priya",
        email="priya@trekma.com",
        name="Priya Sharma",
        contact_no="+91 91234 56781",
        role="staff",
        specialization="Western Ghats Rainforest & Wilderness Survival",
        experience_years=5,
        is_active=True,
        is_blacklisted=False
    )
    staff2.set_password("Staff@123")

    staff3 = User(
        username="staff_rohit",
        email="rohit@trekma.com",
        name="Rohit Verma",
        contact_no="+91 91234 56782",
        role="staff",
        specialization="Himalayan Passes & Navigation",
        experience_years=8,
        is_active=True,
        is_blacklisted=False
    )
    staff3.set_password("Staff@123")

    db.session.add_all([staff1, staff2, staff3])
    db.session.commit()  # commit to generate IDs for staff

    # 3. Create Sample Trekkers (Users)
    user1 = User(
        username="trekker_john",
        email="john@example.com",
        name="John Doe",
        contact_no="+91 99887 76655",
        role="user",
        is_active=True,
        is_blacklisted=False
    )
    user1.set_password("User@123")

    user2 = User(
        username="trekker_sara",
        email="sara@example.com",
        name="Sara Jenkins",
        contact_no="+91 98877 66554",
        role="user",
        is_active=True,
        is_blacklisted=False
    )
    user2.set_password("User@123")

    user3 = User(
        username="trekker_amit",
        email="amit@example.com",
        name="Amit Patel",
        contact_no="+91 97766 55443",
        role="user",
        is_active=True,
        is_blacklisted=False
    )
    user3.set_password("User@123")

    db.session.add_all([user1, user2, user3])
    db.session.commit()

    # 4. Create Diverse Trekking Routes
    today = date.today()

    trek1 = Trek(
        name="Kedarkantha Winter Snow Summit",
        location="Uttarakhand, Himalayas",
        difficulty="Moderate",
        duration_days=5,
        total_slots=18,
        available_slots=15,
        assigned_staff_id=staff1.id,
        status="Open",
        start_date=today + timedelta(days=2),
        end_date=today + timedelta(days=7),
        description="Famous for 360-degree views of Himalayan snow peaks. Perfect blend of dense pine forests and summit climb.",
        price=8500.0,
        image_url="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80"
    )

    trek2 = Trek(
        name="Valley of Flowers Alpine Bloom",
        location="Chamoli, Uttarakhand",
        difficulty="Easy",
        duration_days=4,
        total_slots=25,
        available_slots=23,
        assigned_staff_id=staff2.id,
        status="Open",
        start_date=today + timedelta(days=5),
        end_date=today + timedelta(days=9),
        description="UNESCO World Heritage site nestled in the Garhwal Himalayas. Features hundreds of rare endemic wildflowers.",
        price=6200.0,
        image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"
    )

    trek3 = Trek(
        name="Hampta Pass & Chandratal Lake",
        location="Manali to Spiti, Himachal Pradesh",
        difficulty="Hard",
        duration_days=6,
        total_slots=15,
        available_slots=13,
        assigned_staff_id=staff3.id,
        status="Open",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=16),
        description="Dramatic landscape crossover from lush green Kullu valley to the rugged desert mountains of Spiti.",
        price=11500.0,
        image_url="https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=80"
    )

    trek4 = Trek(
        name="Dudhsagar Waterfalls Trek",
        location="Goa-Karnataka Border",
        difficulty="Easy",
        duration_days=2,
        total_slots=30,
        available_slots=28,
        assigned_staff_id=staff2.id,
        status="Open",
        start_date=today + timedelta(days=14),
        end_date=today + timedelta(days=16),
        description="Trek alongside majestic four-tiered milky waterfalls surrounded by lush Western Ghats deciduous forest.",
        price=3200.0,
        image_url="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80"
    )

    trek5 = Trek(
        name="Harishchandragad Fort & Konkan Kada",
        location="Ahmednagar, Maharashtra",
        difficulty="Moderate",
        duration_days=2,
        total_slots=20,
        available_slots=20,
        assigned_staff_id=staff1.id,
        status="Open",
        start_date=today + timedelta(days=20),
        end_date=today + timedelta(days=22),
        description="Historical hill fort with an astonishing semicircular cliff called Konkan Kada, offering spectacular cloud views.",
        price=2800.0,
        image_url="https://images.unsplash.com/photo-1426604966848-d7adac402bff?auto=format&fit=crop&w=800&q=80"
    )

    trek6 = Trek(
        name="Roopkund Mystery Alpine Expedition",
        location="Garhwal Himalayas, Uttarakhand",
        difficulty="Hard",
        duration_days=7,
        total_slots=12,
        available_slots=0,
        assigned_staff_id=staff3.id,
        status="Closed",
        start_date=today - timedelta(days=15),
        end_date=today - timedelta(days=8),
        description="High altitude glacial lake expedition surrounded by rock-strewn glaciers and snow-clad mountains.",
        price=13800.0,
        image_url="https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=800&q=80"
    )

    db.session.add_all([trek1, trek2, trek3, trek4, trek5, trek6])
    db.session.commit()

    # 5. Create Initial Bookings
    b1 = Booking(
        user_id=user1.id,
        trek_id=trek1.id,
        seats=2,
        status="Booked",
        payment_status="Paid",
        total_amount=17000.0,
        special_notes="Need vegetarian meals during camp"
    )
    b2 = Booking(
        user_id=user2.id,
        trek_id=trek1.id,
        seats=1,
        status="Booked",
        payment_status="Paid",
        total_amount=8500.0,
        special_notes="First time snow trekking"
    )
    b3 = Booking(
        user_id=user3.id,
        trek_id=trek2.id,
        seats=2,
        status="Booked",
        payment_status="Paid",
        total_amount=12400.0,
        special_notes=""
    )
    b4 = Booking(
        user_id=user1.id,
        trek_id=trek3.id,
        seats=2,
        status="Booked",
        payment_status="Paid",
        total_amount=23000.0,
        special_notes="Need trekking poles"
    )
    b5 = Booking(
        user_id=user2.id,
        trek_id=trek4.id,
        seats=2,
        status="Booked",
        payment_status="Paid",
        total_amount=6400.0,
        special_notes=""
    )
    b6 = Booking(
        user_id=user1.id,
        trek_id=trek6.id,
        seats=1,
        status="Completed",
        payment_status="Paid",
        total_amount=13800.0,
        special_notes="Past completed expedition"
    )

    db.session.add_all([b1, b2, b3, b4, b5, b6])

    # 6. Create Welcome and Reminder Notifications
    n1 = Notification(
        user_id=user1.id,
        title="Welcome to TMA!",
        message="Welcome to Trekking Management Application! Explore breathtaking Himalayan & Western Ghats routes.",
        type="system"
    )
    n2 = Notification(
        user_id=user1.id,
        title="Upcoming Trek Reminder: Kedarkantha Winter Summit",
        message="Your trek starts in 2 days! Please ensure you have packed warm layers and waterproof boots.",
        type="reminder"
    )
    n3 = Notification(
        user_id=admin.id,
        title="System Initialized",
        message="TMA V2 platform initialized successfully with SQLite database and programmatic seeding.",
        type="system"
    )

    db.session.add_all([n1, n2, n3])
    db.session.commit()
    print("[DATABASE SEED] Seed completed successfully!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database_if_empty()
