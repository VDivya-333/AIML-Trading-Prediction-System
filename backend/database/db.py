from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///trading.db"

engine = create_engine(DATABASE_URL)

print("Database Connected")