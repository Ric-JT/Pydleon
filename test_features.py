from utils.handle_cake import CakeHandler
from utils.handle_recipes import RecipeBook
from utils.config import config


cake_filename = config["CAKE_FILENAME"]
recipe_filename = config["RECIPES_BOOK_FILENAME"]

recipe_book = RecipeBook(recipe_filename)
cake_handler = CakeHandler(cake_filename)

bags = [cake_handler.get_char_inventory(n) for n in range(len(cake_handler)) if n == 0]
bags += [cake_handler.get_chest_inventory()]

for bag in bags:
    recipe_book.add_to_bag(bag)

possible_recipes = recipe_book.possible_recipes


# Print Inventory
# recipe_book.print_inventory()
recipe_book._print_possible_recipies()

recipe_book.add_to_grindlist(
    {
        "Crows_Nest": 1,
    }
)
res = recipe_book.print_recipes_stages(recipes=recipe_book.grindlist)

# Print Grindlist
recipe_book.print_grindlist()
