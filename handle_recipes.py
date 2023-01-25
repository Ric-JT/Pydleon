import json


class RecipeBook:
    def __init__(self, recipes: dict = {}):
        self.recipes = recipes

    def get_recipe_by_name(self, name: str) -> dict:
        recipe_dict = {name: self.recipes.get(name, {})}
        return recipe_dict

    def get_recipes_by_ingredients(
        self, ingredients: dict, smth_lvl: int = None
    ) -> dict:
        recipes_dict = {}
        for target in self.recipes:
            is_possible = True
            recipe = self.recipes.get(target, {})
            if not len(recipe) or (smth_lvl and smth_lvl < recipe["smth_lvl_req"]):
                is_possible = False
            else:
                rec_ingredients = recipe["ingredients"]
                for rec_ingredient in rec_ingredients:
                    if (
                        rec_ingredient not in ingredients
                        or rec_ingredients[rec_ingredient] > ingredients[rec_ingredient]
                    ):
                        is_possible = False
                        break
            if is_possible:
                recipes_dict.update(self.get_recipe_by_name(target))
        return recipes_dict


if __name__ == "__main__":
    recipes_json_filename = "recipes.json"
    with open(recipes_json_filename, "r") as file:
        recipes = json.load(file)

    recipe_book = RecipeBook(recipes=recipes)

    bag = {"Crimson String": 20, "Cue Tape": 5, "Spore Cap": 10, "Copper Bar": 100000}
    possible_recipes = recipe_book.get_recipes_by_ingredients(bag)

    # Prints
    print(f"Inventory:")
    for item in bag:
        print(f"\t - {item} x{bag[item]}")

    print(f"Possible recipes:")
    for recipe in possible_recipes:
        print(f"\t{recipe}")
        ingredients = possible_recipes[recipe]["ingredients"]

        [print(f"\t\t * {ing} x{ingredients[ing]}") for ing in ingredients]
