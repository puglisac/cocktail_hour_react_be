from unittest import TestCase
from models import db, User, Cocktail, Saved, UserCocktail, UserCocktailIngredient
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://@localhost:5433/test_cocktail"

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class TestViewRoutesTestCase(TestCase):

    def setUp(self):
        """create test client, add sample data."""
        
        Saved.query.delete()
        UserCocktail.query.delete()
        UserCocktailIngredient.query.delete()
        Cocktail.query.delete()
        User.query.delete()
        
        self.client = app.test_client
        self.u =User(
        
            username = "testname",
            password = "password",
            email = "testemail@test.com", 
            dob = "01/01/2000"
            )


        self.c = Cocktail(
            name = "test_cocktail",
            drink_img_url = "none"
        )


    def test_slash_page(self):
        with app.test_client() as client:

            resp = client.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome to Cocktail Hour",   html)

    

    def test_login(self):
        with app.test_client() as client:

            resp = client.post('/login', data =    {'username': 'testname', 'password':   'testuser'}, follow_redirects = True)
            html = resp.get_data(as_text = True)
            self.assertEqual(resp.status_code, 200)
            
    def test_invalid_password(self):
        with app.test_client() as client:

            resp = client.post(
                '/login', data={'username':'testname',     'password':'nottestuser'},    follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid username or password",   html)    

    def test_signup(self):
        with app.test_client() as client:

            resp = client.post('/signup', data =   {'username': 'testname', 'email': 'testemail@test.com', 'password':   'newpassword', 'dob': '01/02/1999'},  follow_redirects = True)
            html = resp.get_data(as_text = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testname", html)
    
    def test_delete_user(self):
        with app.test_client() as client:

            resp = client.post(f"/user/1/delete",  follow_redirects = True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('testname', html)
    
    def test_logout(self):
        with app.test_client() as client:

            resp = client.post('/logout/1',    follow_redirects = True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('testname', html)


    def test_user_home(self):
        with app.test_client() as client:

            resp = client.post('/user/1', follow_redirects = True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)


    def test_random(self):
        with app.test_client() as client:

            resp = client.post('/random', follow_redirects = True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)

    def test_search_name(self):
        with app.test_client() as client:

            resp = client.post('/search/mule', follow_redirects = True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('gin', html)     

    def test_search_ingredient(self):
        with app.test_client() as client:

            resp = client.post('/search/tonic', follow_redirects = True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tonic', html)  

    
    def test_search_letter(self):
        with app.test_client() as client:

            resp = client.post('/search/a', follow_redirects = True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('A', html)      




