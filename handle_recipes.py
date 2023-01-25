import json
import pandas as pd


def _update_dict_add(bag: dict, new_items: dict) -> dict:
    for item_name in new_items:
        if bag.get(item_name):
            bag[item_name] += new_items[item_name]
        else:
            bag[item_name] = new_items[item_name]
    return bag


def _update_dict_sub(bag: dict, new_items: dict) -> dict:
    for item_name in new_items:
        if bag.get(item_name):
            res = bag[item_name] - new_items[item_name]
            bag[item_name] = res if res >= 0 else 0

    return bag


def print_hline(n: int = 100):
    print("_" * n)


class RecipeBook:
    def __init__(self, recipes: dict = {}):
        self.recipes: dict = recipes
        self.bag: dict = {}

        self.possible_recipes: dict = {}

        self.grindlist: dict = {}
        self.grindcost: dict = {}
        self.grindleft: dict = {}

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

    def add_to_bag(self, bag: dict):
        _update_dict_add(self.bag, bag)
        grindcost = self.grindcost.copy()
        self.grindleft = _update_dict_sub(grindcost, self.bag)
        self.possible_recipes = recipe_book.get_recipes_by_ingredients(self.bag)

    def get_item_cost(self, item: str, number: int):
        cost = {}
        if self.recipes.get(item):
            ingredients = self.recipes[item]["ingredients"]

            for ingredient in ingredients:
                item_cost = self.get_item_cost(ingredient, ingredients[ingredient])
                _update_dict_add(cost, item_cost)

            cost_series = pd.Series(cost, dtype=int) * number
            cost = cost_series.to_dict()
        else:
            cost[item] = number

        return cost

    def add_to_grindlist(self, wishes: dict = {}):
        cost = {}

        for wish in wishes:
            wish_cost = self.get_item_cost(wish, wishes[wish])
            _update_dict_add(cost, wish_cost)

        _update_dict_add(self.grindlist, wishes)
        _update_dict_add(self.grindcost, cost)
        grindcost = self.grindcost.copy()
        self.grindleft = _update_dict_sub(grindcost, self.bag)

        return self.grindlist, self.grindcost

    def print_inventory(self):
        print_hline()
        print(f"Inventory:")
        for item in self.bag:
            print(f"\t - {item} x{self.bag[item]}")

        print(f"Possible recipes:")
        for recipe in self.possible_recipes:
            print(f"\t{recipe}")

            ingredients = self.possible_recipes[recipe]["ingredients"]
            [print(f"\t\t * {ing} x{ingredients[ing]}") for ing in ingredients]
        print_hline()

    def print_grindlist(self):
        print_hline()
        print(f"Grind List:")
        for wish in self.grindlist:
            print(f"\t + {wish} x{self.grindlist[wish]}")

        print(f"Grind Cost:")
        for item in self.grindcost:
            print(f"\t * {item} x{self.grindcost[item]}")

        print(f"Grind Left:")
        for item in self.grindleft:
            print(f"\t - {item} x{self.grindleft[item]}")
        print_hline()


if __name__ == "__main__":
    recipes_json_filename = "recipes.json"
    with open(recipes_json_filename, "r") as file:
        recipes = json.load(file)

    recipe_book = RecipeBook(recipes=recipes)

    bag = {"Crimson String": 20, "Cue Tape": 5, "Spore Cap": 10, "Copper Bar": 10000}
    grindlist = {"Wooden Bow": 1, "Goo Galoshes": 2}

    recipe_book.add_to_bag(bag)
    recipe_book.add_to_grindlist(grindlist)

    recipe_book.print_inventory()
    recipe_book.print_grindlist()
