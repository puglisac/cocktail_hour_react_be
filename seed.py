# from app import db
from models import User, db
from app import app
from datetime import date
db.drop_all()
db.create_all()

user = User.register("test@email.com", "password", date.today())
db.session.add(user)
db.session.commit()
