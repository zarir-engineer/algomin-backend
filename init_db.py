# init_db.py
from database import Base, engine
from models import Strategy

Base.metadata.create_all(bind=engine)
