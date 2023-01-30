import json
import pandas as pd


def _update_dict_add(bag: dict, new_items: dict) -> dict:
    """This is an auxiliary function that allows to update an existing dict with the new items relying on the addition operator.
    If one key in *new_items* exists in both dictionaries, then the resulting value for that key would be the sum of both values.

    Parameters
    ----------
    bag : dict
        Dictionary to update with the *new_items*
    new_items : dict
        Dictionary with keys and values to update *bag*

    Returns
    -------
    dict
        Resulting dictionary
    """
    for item_name in new_items:
        if bag.get(item_name):
            bag[item_name] += new_items[item_name]
        else:
            bag[item_name] = new_items[item_name]
    return bag


def _update_dict_sub(bag: dict, new_items: dict) -> dict:
    """This is an auxiliary function that allows to update an existing dict with the new items relying on the subtraction operator.
    If one key in *new_items* exists in both dictionaries, then the resulting value for that key would be the difference of both values.

    Parameters
    ----------
    bag : dict
        Dictionary to update with the *new_items*
    new_items : dict
        Dictionary with keys and values to update *bag*

    Returns
    -------
    dict
        Resulting dictionary
    """
    for item_name in new_items:
        if bag.get(item_name):
            res = bag[item_name] - new_items[item_name]
            bag[item_name] = res if res >= 0 else 0

    return bag


def _print_hline(n: int = 100):
    """This function prints an Horizontal line with *n* consecutive '_'

    Parameters
    ----------
    n : int, optional
        Number of consecutive '_', by default 100
    """
    print("_" * n)


class RecipeBook:
    def __init__(self, recipes: dict = {}):
        """This is the initial function of Recipe Book. It initiates the attributes of the class.

        Attributes:
        ----------
        self.recipes: dict
            Recipe book dictionary with the recipe output item name as keys and the requirements as values.
            The requirements are also dict with the following keys
                - 'ingredients' : dict
                    Dictionary with items as keys and their required quantity as the value
                - 'smth_lvl_req': int
                    Smithing level required to craft the recipe
                - 'recipe_source': str
                    How the recipe is achieved
                - 'anvil_tab': int
                    To which anvil tab the recipe belongs to
                - 'recipe_id': id
                    Recipe Id in the respective anvil tab
        self.bag: dict
            Dictionary with with items as keys and their required quantity as the value, representing the Inventory bag

        Parameters
        ----------
        recipes : dict, optional
            Recipe book as a dictionary, by default {}
        """
        self.recipes: dict = recipes
        self.bag: dict = {}

        self.possible_recipes: dict = {}

        self.grindlist: dict = {}
        self.grindcost: dict = {}
        self.grindleft: dict = {}

    def get_recipe_by_name(self, name: str) -> dict:
        """This function gets a recipe from an output item name. If it isn't in the recipe book return an empty dict

        Parameters
        ----------
        name : str
            Recipe output item name

        Returns
        -------
        dict
            Recipe Dictionary from the recipe book
        """
        recipe_dict = {name: self.recipes.get(name, {})}
        return recipe_dict

    def get_recipes_by_ingredients(
        self, ingredients: dict, smth_lvl: int = None
    ) -> dict:
        """This function gets the recipes based on a set of ingredients

        Parameters
        ----------
        ingredients : dict
            Set of ingredients to use in recipe search
        smth_lvl : int, optional
            Player smithing Level, by default None

        Returns
        -------
        dict
            Possible recipes with the given ingredients
        """
        recipes_dict = {}
        for target in self.recipes:
            # Start recipe evaluation believing it's possible
            is_possible = True

            # Get recipe from Recipe Book, if doesn't exist return empty recipe
            recipe = self.recipes.get(target, {})

            # If there isn't a recipe or is invalid for the current smithing level
            # assume impossible recipe
            if not len(recipe) or (smth_lvl and smth_lvl < recipe["smth_lvl_req"]):
                is_possible = False
            # If there is a recipe and valid for the current smithing level
            else:
                rec_ingredients = recipe["ingredients"]
                # If any ingredient isn't available or isn't enough to craft the recipe
                # assume impossible recipe
                for rec_ingredient in rec_ingredients:
                    if (
                        rec_ingredient not in ingredients
                        or rec_ingredients[rec_ingredient] > ingredients[rec_ingredient]
                    ):
                        is_possible = False
                        break
            # If the recipe is still considered possible add it to the recipes dict
            if is_possible:
                recipes_dict.update(self.get_recipe_by_name(target))

        return recipes_dict

    def add_to_bag(self, bag: dict):
        """Add set of items to self.bag. It also updates the self.grindcost and self.possible_recipes

        Parameters
        ----------
        bag : dict
            Set of items to add
        """
        # Add bag to Recipe Book Bag
        _update_dict_add(self.bag, bag)

        # Get Grindleft through a subtraction of the Recipe Book Bag to the grindcost
        grindcost = self.grindcost.copy()
        self.grindleft = _update_dict_sub(grindcost, self.bag)

        # Get possible recipes based on Recipe Book Bag
        self.possible_recipes = recipe_book.get_recipes_by_ingredients(self.bag)

    def get_item_cost(self, item: str, number: int) -> dict:
        """Get the cost in materials of certain number of one type of item.

        Parameters
        ----------
        item : str
            Item to evaluate
        number : int
            Number of Items

        Returns
        -------
        dict
            Dictionary with items as key and quantity as value to represent the item cost
        """

        cost = {}
        # If Recipe Book has a recipe for the item
        if self.recipes.get(item):
            ingredients = self.recipes[item]["ingredients"]

            # Break the ingredient down until there is no more ingredients with recipes
            for ingredient in ingredients:
                item_cost = self.get_item_cost(ingredient, ingredients[ingredient])
                _update_dict_add(cost, item_cost)

            # Multiply the item cost by the number of items
            cost_series = pd.Series(cost, dtype=int) * number

            # Convert cost back to Dictionary
            cost = cost_series.to_dict()
        # Else set the item itself as the cost
        else:
            cost[item] = number

        return cost

    def get_itemlist_cost(self, item_list: dict) -> dict:
        """This function calculates the cost for a set of items

        Parameters
        ----------
        item_list : dict
            Dictionary with item names as keys and number of that item name as value

        Returns
        -------
        dict
            Dictionary ith item names as keys and number of that item name as value to represent the cost.
        """
        cost = {}

        # Get cost for the List of Items
        for item in item_list:
            item_cost = self.get_item_cost(item, item_list[item])
            _update_dict_add(cost, item_cost)
        return cost

    def add_to_grindlist(self, wishes: dict = {}):
        """This function adds grind wishes to the grind list. Also updates self.gindcost and self.grindleft

        Parameters
        ----------
        wishes : dict, optional
            Dictionary with items as key and quantity as value to represent the item grind wishes, by default {}
        """
        # Get cost for the new wishes
        wishes = {wish: wishes[wish] for wish in wishes if wishes[wish] > 0}
        cost = self.get_cost_itemlist(wishes)

        # Add wishes to Grindlist
        _update_dict_add(self.grindlist, wishes)

        # Add wishes cost to Grindcost
        _update_dict_add(self.grindcost, cost)

        # Update Grindleft based on Grindcost and Recipe Book Bag
        grindcost = self.grindcost.copy()
        self.grindleft = _update_dict_sub(grindcost, self.bag)

    def print_inventory(self):
        """This function prints the current Inventory and current Possible Recipes"""
        _print_hline()
        print(f"Inventory:")
        for item in self.bag:
            print(f"\t - {item} x{self.bag[item]}")

        print(f"Possible Recipes:")
        for recipe in self.possible_recipes:
            print(f"\t{recipe}")

            ingredients = self.possible_recipes[recipe]["ingredients"]
            [print(f"\t\t * {ing} x{ingredients[ing]}") for ing in ingredients]
        _print_hline()

    def print_grindlist(self):
        """This function prints the grindlist, grindcost and grindleft"""
        _print_hline()
        print(f"Grind List:")
        for wish in self.grindlist:
            print(f"\t + {wish} x{self.grindlist[wish]}")

        print(f"Grind Cost:")
        for item in self.grindcost:
            print(f"\t * {item} x{self.grindcost[item]}")

        print(f"Grind Left:")
        for item in self.grindleft:
            print(f"\t - {item} x{self.grindleft[item]}")
        _print_hline()


if __name__ == "__main__":
    # Open recipes Json
    recipes_json_filename = "recipes.json"
    with open(recipes_json_filename, "r") as file:
        recipes = json.load(file)

    # Build Recipe Book
    recipe_book = RecipeBook(recipes=recipes)

    # Initiate Inventory Bag
    bag = {"Crimson String": 20, "Cue Tape": 5, "Spore Cap": 10, "Copper Bar": 10000}

    # Initiate Grindlist
    grindlist = {"Wooden Bow": 20, "Goo Galoshes": 0, "Boxing Gloves": 1}

    # Add Inventory Bag to Recipe Book
    recipe_book.add_to_bag(bag)
    # Add Grindlist to Recipe Book
    recipe_book.add_to_grindlist(grindlist)

    # Print Inventory
    recipe_book.print_inventory()

    # Print Grindlist
    recipe_book.print_grindlist()
