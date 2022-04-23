from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Cocktail, Saved, UserCocktail, UserCocktailIngredient
from forms import LoginForm, AddUserForm, SearchByNameForm, SearchByIngredientForm, CreateDrinkForm, EditUserForm, CreateDrinkForm, IngredientForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from api_helper import CocktailDetails, cocktails_url
import string
import os


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://@localhost:5433/cocktails')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shh')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
login_manager = LoginManager()

connect_db(app)

login = LoginManager(app)
login.login_view="welcome"



@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#################### home route
@app.route("/")
def welcome():
    """Display welcome/login/signup links"""
    if not current_user.is_active:
        return render_template("welcome.html")
        
    else:
        return redirect("/home")

################### authentication routes

@app.route("/login", methods = ["GET", "POST"])
def login():
    """Handle User Login"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(request.form['username'], request.form['password'])
        if user:
            """log in user & redirect to user home page"""
            login_user(user)
            return redirect(f"/home")
        else:
            """error handling for invalid credentials"""
            flash("Invalid username or password", "danger")
            return redirect(url_for('login'))
    print("************", current_user)
            
    return render_template('login.html', form=form)


@app.route("/logout/<int:user_id>", methods = ["GET", "POST"])
@login_required
def logout(user_id):
    """logs out user"""
    if current_user.id != user_id:
        flash("You do not have permission to see this page", "danger")
        return redirect(f"/user/{current_user.id}")
    else: 
        logout_user()
        return redirect(url_for("welcome"))


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """handles user signup."""
    form = AddUserForm()

    if form.validate_on_submit():
        """create a new user"""
        user = User.register(
            username = form.username.data,
            email = form.email.data,
            password = form.password.data, 
            dob = form.dob.data)
        print("*******", form.email.data)
        db.session.add(user)

        try:
            db.session.commit()
            login_user(user)
            return redirect(f"/home")

        except IntegrityError:
            """handles create user errors if username already taken"""
            flash(f"Username {form.username.data} has already been taken. Please try again.", 'danger')
            return redirect(url_for('signup'))
    else:
        """display user sign-up form"""
        return render_template('add_user.html', form=form)



################### user routes

@app.route("/home")
@login_required
def home():
    """Display homepage"""
    user=current_user
    return render_template('home.html', current_user=current_user)


@app.route("/user/<int:user_id>", methods = ["POST", "GET"])
@login_required
def user_home(user_id):
    """display use homepage"""
    if current_user.id != user_id:
        flash("You do not have permission to see this page", "danger")
        return redirect(f"/user/{current_user.id}")
    
    else: 
        return render_template('user_home.html', user=current_user)

@app.route("/user/<int:user_id>/edit", methods = ['GET', 'POST'])
@login_required
def edit_user(user_id):
    """edit a user"""

    current_user = User.query.get_or_404(user_id)

    if current_user.id != user_id:
        flash("You do not have permission to access this page", "danger")
        return redirect(f"/user/{current_user.id}")

    form = EditUserForm(obj = current_user)
    
   
    if current_user.authenticate(current_user.username, form.password.data):
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.dob = form.dob.data

            db.session.commit()

            return redirect(f"/user/{current_user.id}")
    else:
         return render_template('edit_user.html', form = form)

@app.route("/user/<int:user_id>/delete", methods = ["POST"])
@login_required
def delete_user(user_id):
    """delete a user"""
    if current_user.id != user_id:
        flash("You do not have permission to access this page", "danger")
        return redirect(f"/user/{current_user.id}")


    else:

        db.session.delete(current_user)
        db.session.commit()
        logout_user()


    return redirect("/")

################  user created cocktail routes


@app.route("/user/<int:user_id>/create_cocktail/", methods = ['GET', 'POST'])
@login_required
def create_cocktail(user_id):
    """create a cocktail"""
    form = CreateDrinkForm()

    if form.validate_on_submit():
        user_cocktail = UserCocktail(
            name = form.name.data,
            instructions = form.instructions.data,
            alcoholic = form.alcoholic.data,
            glass = form.glass.data,
            drink_img_url = form.drink_img_url.data,
            user_id = user_id
        )
        
        db.session.add(user_cocktail)
        db.session.commit()
   
        return redirect(f"/user/{user_id}/{user_cocktail.id}/add_ingredients")
    else:
        return render_template("create_drink.html", form=form)



@app.route("/user/<int:user_id>/<int:cocktail_id>/add_ingredients/", methods = ['GET', 'POST'])
@login_required
def add_ingredients_to_user_cocktail(user_id, cocktail_id):
    form = IngredientForm()
    cocktail = UserCocktail.query.get_or_404(cocktail_id)

    if form.validate_on_submit():
        ingredient_for_cocktail = UserCocktailIngredient(
            cocktail_id = cocktail_id,
            name = form.name.data, 
            amount = form.amount.data, 
            measurement = form.measurement.data
        )

        db.session.add(ingredient_for_cocktail)
        db.session.commit()

        return redirect(f"/user/{user_id}/{cocktail_id}/add_ingredients")
    
    else:
        return render_template("add_ingredients.html", form = form, cocktail = cocktail, user_id = user_id)



@app.route("/user/<int:user_id>/<int:cocktail_id>/edit_cocktail", methods = ['GET', 'POST'])
@login_required
def edit_ingredients_for_user_cocktail(user_id, cocktail_id):   

    cocktail = UserCocktail.query.get_or_404(cocktail_id)
    form = CreateDrinkForm(obj = cocktail)

    if form.validate_on_submit():
        cocktail.name = form.name.data
        cocktail.instructions = form.instructions.data
        cocktail.alcoholic = form.alcoholic.data
        cocktail.glass = form.glass.data
        cocktail.drink_img_url = form.drink_img_url.data
        user_id = user_id

        db.session.commit()
    
        return redirect (f"/user/{current_user.id}")
    
    else:
        return render_template("edit_user_cocktail.html", form = form, cocktail = cocktail, user = current_user)


    
@app.route("/user/<int:user_id>/<int:cocktail_id>/delete", methods = ['GET', 'POST'])
@login_required
def delete_user_cocktail(user_id, cocktail_id):

    cocktail = UserCocktail.query.get_or_404(cocktail_id)
    db.session.delete(cocktail)
    db.session.commit()
        
    return redirect(f"/user/{user_id}")


@app.route("/user/<int:user_id>/<int:cocktail_id>/<int:ingredient_id>/edit_ingredients", methods = ['GET', 'POST'])
@login_required
def edit_user_ingredients(user_id, cocktail_id, ingredient_id):

    ingredient = UserCocktailIngredient.query.get_or_404(ingredient_id)
    form = IngredientForm(obj = ingredient)

    if form.validate_on_submit():
        
        ingredient.name = form.name.data, 
        ingredient.amount = form.amount.data, 
        ingredient.measurement = form.measurement.data
        
        db.session.commit()

        return redirect(f"/user/{user_id}/{cocktail_id}/edit_cocktail")

    else:

        return render_template('edit_ingredients.html', form = form, user_id = user_id, cocktail_id = cocktail_id, ingredient_id = ingredient_id)



@app.route("/user/<int:user_id>/<int:cocktail_id>/<int:ingredient_id>/delete_ingredient", methods = ['GET', 'POST'])
@login_required
def delete_user_ingredients(user_id, cocktail_id, ingredient_id):

    user = current_user
    ingredient = UserCocktailIngredient.query.get_or_404(ingredient_id)

    db.session.delete(ingredient)
    db.session.commit()

    return redirect(f"/user/{user_id}/{cocktail_id}/edit_cocktail")


@app.route("/user/<int:user_id>/user_cocktail/<int:cocktail_id>", methods = ['GET'])
@login_required
def display_user_cocktail_details(cocktail_id, user_id):

        user = current_user
        cocktail = UserCocktail.query.get_or_404(cocktail_id)

        return render_template('display_user_cocktail.html', cocktail=cocktail, user = user)

################### cocktail routes


@app.route("/random", methods = ['GET', 'POST'])
@login_required
def get_random():
    """get a random cocktail"""
    cocktail = CocktailDetails.get_random_cocktail(cocktails_url)
    return render_template("display_cocktail.html", cocktail=cocktail)

@app.route("/drinks/<letter>", methods = ["GET"])
@login_required
def by_letter(letter):
    """displays drinks starting with letter"""
    return render_template('drinks_list.html')

@app.route("/display/name/<name>/", methods = ["GET"])
@login_required
def display_name(name):
    """retrieve drink by name"""
    cocktails = CocktailDetails.get_cocktails_by_name(name)
    return render_template("drinks_list.html", drinks=cocktails)

@app.route("/display/ingredient/<ingredient>/", methods = ["GET"])
@login_required
def display_ing(ingredient):
    """retrieve drink by ingredient name"""
    cocktail = CocktailDetails.get_cocktails_by_ingredient_name(ingredient)
    return render_template("drinks_list.html", drinks=cocktail)


@app.route("/search/<first_letter>", methods = ["GET", "POST"])
@login_required
def search_by_letter(first_letter):
    """gets drinks by first letter"""
    cocktail = CocktailDetails.get_cocktails_by_first_letter(first_letter)
    return render_template(
             "drinks_list.html", drinks = cocktail)


@app.route("/search", methods=['GET'])
@login_required
def search():
    """handles user searches"""
    name_form = SearchByNameForm()
    ingredient_form = SearchByIngredientForm()
    ingredient_choices = CocktailDetails.get_all_ingredients()
    range = list(string.ascii_uppercase)

    return render_template('search.html', name_form = name_form, ingredient_form = ingredient_form, range = range)


@app.route("/search/name", methods = ['POST'])
@login_required
def post_search():
    """handles name search route"""
    name_form = SearchByNameForm()

    if name_form.validate_on_submit():
        name = name_form.name.data
        return redirect(f"/display/name/{name}")


@app.route("/search/ingredient", methods = ['POST'])
@login_required
def ingredient_search():
    """handles ingredient search route"""

    ingredient_form = SearchByIngredientForm()

    if ingredient_form.validate_on_submit():
        ingredient = ingredient_form.ingredient.data
        return redirect(f"/display/ingredient/{ingredient}")


@app.route("/drink/<drink_id>", methods = ["GET"])
@login_required
def drink_details(drink_id):
    """displays drink info"""
    cocktail = CocktailDetails.get_drink_by_id(drink_id)

    saved_ids = [str(cocktail.id) for cocktail in current_user.saved_cocktails]
    

    return render_template("display_cocktail.html", cocktail=cocktail, saved_ids = saved_ids)
    

@app.route("/drink/<drink_id>/save", methods=["POST"])
@login_required
def save_drink(drink_id):
    """saves a drink to the user"""

    cocktail_from_api = CocktailDetails.get_drink_by_id(drink_id)
    my_cocktail = Cocktail(id = cocktail_from_api.drink_id, name=cocktail_from_api.name, drink_img_url=cocktail_from_api.img)
    db.session.add(my_cocktail)
    try:
        current_user.saved_cocktails.append(my_cocktail)
        db.session.commit()
      
    except IntegrityError:
        db.session.rollback()
        cocktail = Cocktail.query.get_or_404(drink_id)
        current_user.saved_cocktails.append(cocktail)
        db.session.commit()
        
    flash("Saved!")
    return redirect (f"/user/{current_user.id}")


@app.route("/drink/<drink_id>/delete", methods = ["POST"])
@login_required
def delete_saved_drink(drink_id):
    """deletes a saved drink from user"""

    drink = Cocktail.query.get_or_404(drink_id)
    current_user.saved_cocktails.remove(drink)
    db.session.commit()

    if not drink.user:
        db.session.delete(drink)
        db.session.commit()

    return redirect(f"/user/{current_user.id}")

