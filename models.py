from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy_serializer.serializer import SerializerMixin

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

# models go below

class User(db.Model, SerializerMixin):
    """users info"""

    __tablename__ = "users"
    email = db.Column(db.Text, primary_key=True, nullable=False, unique=True) 
    password = db.Column(db.Text, nullable=False,)
    dob = db.Column(db.DateTime, nullable=False)
    saved_cocktails = db.relationship('Cocktail', secondary = "user_cocktails", backref = "user")

    def save_cocktail(self, cocktail):

        self.saved.append(cocktail)
        db.session.commit()

    @classmethod
    def register(cls, email, password, dob):
        """Register new user with a hashed password, and return the user"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(email = email, password = hashed_pwd, dob = dob)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        """Validate that the user exists and password is valid"""

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False


class Cocktail(db.Model, SerializerMixin):
    """cocktails info"""

    __tablename__="cocktails"

    id = db.Column(db.Integer,
                   primary_key=True)
    name = db.Column(db.String(80), nullable = False, unique=True)
    drink_img_url = db.Column(db.String(), nullable = True)


class UserCocktails(db.Model, SerializerMixin):

    """Info about saved cocktails"""

    __tablename__ = "user_cocktails"

    cocktail_id = db.Column(db.Integer, db.ForeignKey('cocktails.id', ondelete = "CASCADE"), primary_key = True)

    user_id = db.Column(db.Text, db.ForeignKey('users.email', ondelete = "CASCADE"), primary_key = True)
