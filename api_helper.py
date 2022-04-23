
import requests
from models import db, connect_db, User, Cocktail, Saved, UserCocktail

cocktails_url = "http://www.thecocktaildb.com/api/json/v1/1"

class CocktailDetails:
    def __init__(self, id, name, alcoholic, glass, img, recipe, instructions):
        self.drink_id = id
        self.instructions = instructions
        self.name = name
        self.alcoholic = alcoholic
        self.glass = glass
        self.img = img
        self.recipe = recipe

    @staticmethod
    def get_random_cocktail(cocktails_url):
        """return a random cocktail"""

        r = requests.get(f"{cocktails_url}/random.php")
        data = r.json()
        drink = data['drinks'][0]
        drink_id = drink['idDrink']
        name = drink['strDrink']
        instructions = drink['strInstructions']
        alcoholic = drink['strAlcoholic']
        glass = drink['strGlass']
        img = drink['strDrinkThumb']
        recipe = CocktailDetails.get_ingredients(drink)

        return CocktailDetails(drink_id, name, alcoholic, glass, img, recipe, instructions)

    @staticmethod
    def get_ingredients(obj):
        """get list of specific cocktail ingredients"""

        ingredients = []
        i = 1
        while obj[f'strIngredient{i}']:
                ingredients.append({"ingredient": obj[f'strIngredient{i}'],
                                        "measurement": obj[f'strMeasure{i}']})
                i = i+1
        return ingredients

    @staticmethod
    def get_cocktails_by_ingredient_name(ingredient):
        """get cocktail by user search: ingredient"""

        r = requests.get(f'{cocktails_url}/filter.php?i={ingredient}')
        data = r.json()
        return data['drinks']

    @staticmethod
    def get_cocktails_by_name(name):
        """get cocktail by drink name"""

        r = requests.get(f'{cocktails_url}/search.php?s={name}')
        data = r.json()
        drinks = data['drinks']
        return drinks

    @staticmethod
    def get_cocktails_by_first_letter(first_letter):
        """get list of cocktails starting with user input letter"""

        r = requests.get(f'{cocktails_url}/search.php?f={first_letter}')
        data = r.json()
        return data['drinks']

    @staticmethod
    def get_drink_by_id(id):

        response =  requests.get(f'{cocktails_url}/lookup.php?i={id}')
        drink = response.json()['drinks'][0]

        drink_id = drink['idDrink']
        name = drink['strDrink']
        instructions = drink['strInstructions']
        alcoholic = drink['strAlcoholic']
        glass = drink['strGlass']
        img = drink['strDrinkThumb']
        recipe = CocktailDetails.get_ingredients(drink)

        return CocktailDetails(drink_id, name, alcoholic, glass, img, recipe, instructions)

    @staticmethod
    def get_all_ingredients():

        r = requests.get(f'{cocktails_url}/list.php?i=list')
        data = r.json()
        ingredients = data['drinks']
        return sorted([ingredient["strIngredient1"] for ingredient in ingredients])






