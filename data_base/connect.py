from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data_base"
DB_PATH = DB_DIR / "users.db"

url_to_db = f"sqlite:///{DB_PATH}"

engine = create_engine(url_to_db, echo=False)
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()