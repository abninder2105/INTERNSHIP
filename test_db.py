from sqlalchemy import text
from app import create_app, db

app = create_app()

with app.app_context():
    try:
        # Use a connection context to execute the raw SQL
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to MySQL successfully!")
    except Exception as e:
        print("❌ MySQL connection failed:", e)
