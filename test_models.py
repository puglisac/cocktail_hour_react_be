
from unittest import TestCase
from models import db, User, Cocktail, Saved, UserCocktail, UserCocktailIngredient
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://@localhost:5433/test_cocktail"

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):
    """Tests user model"""

    def setUp(self):
        """create test client, add sample data."""
        
        Saved.query.delete()
        UserCocktail.query.delete()
        UserCocktailIngredient.query.delete()
        Cocktail.query.delete()
        User.query.delete()
        
        self.client = app.test_client
        self.u =User.register(
            username = "testname",
            password = "password",
            email = "testemail@test.com", 
            dob = "01/01/2000"
        )

        db.session.commit()


    def test_user_model(self):
        """does user model work"""

        self.assertEqual(len(self.u.saved_cocktails), 0)
        self.assertEqual(len(self.u.user_cocktails), 0)
    
    def test_authentication(self):
        self.assertEqual(User.authenticate(self.u.username, "wrong"), False)
        
        self.assertEqual(User.authenticate(self.u.username, "password"), self.u)


class UserCocktailTestCase(TestCase):

    def setUp(self):
        """create test client, add sample data."""
        
        Saved.query.delete()
        UserCocktail.query.delete()
        UserCocktailIngredient.query.delete()
        Cocktail.query.delete()
        User.query.delete()
        
        self.client = app.test_client
        self.u =User.register(
            username = "testname",
            password = "password",
            email = "testemail@test.com", 
            dob = "01/01/2000"
        )

        db.session.commit()

    def test_user_cocktail(self):

        self.c = UserCocktail(
            name = "testname",
            instructions = "test_instructions",
            alcoholic = "test_alocholic",
            glass = "test_glass",
            user_id = self.u.id,
            drink_img_url = "none",
            recipe = []
        )
        

        db.session.add(self.c)
        self.u.user_cocktails.append(self.c)
        db.session.commit()

        self.assertEqual(len(self.u.user_cocktails), 1)


class UserCocktailIngredientTestCase(TestCase):

    def setUp(self):
        """create test client, add sample data."""
        
        Saved.query.delete()
        UserCocktail.query.delete()
        UserCocktailIngredient.query.delete()
        Cocktail.query.delete()
        User.query.delete()
        
        self.client = app.test_client
        self.u =User.register(
            username = "testname",
            password = "password",
            email = "testemail@test.com", 
            dob = "01/01/2000"
        )

        db.session.commit()


        self.c = UserCocktail(
            name = "testname",
            instructions = "test_instructions",
            alcoholic = "test_alocholic",
            glass = "test_glass",
            user_id = self.u.id,
            drink_img_url = "none",
            recipe = []
        )
        
        db.session.add(self.c)
        db.session.commit()
        self.u.user_cocktails.append(self.c)

    def test_user_cocktail_ingredient(self):

        self.i = UserCocktailIngredient(
            cocktail_id = self.u.user_cocktails[0].id,
            name = "test_name",
            amount = 1,
            measurement = "test_measurement"
        )

        db.session.add(self.i)
        db.session.commit()

        self.assertEqual(len(self.u.user_cocktails[0].recipe), 1)
