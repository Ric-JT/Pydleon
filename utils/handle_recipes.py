import json
from typing import Dict, List
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


def print_hline(n: int = 100):
    """This function prints an Horizontal line with *n* consecutive '_'

    Parameters
    ----------
    n : int, optional
        Number of consecutive '_', by default 100
    """
    print("_" * n)


class RecipeBook:
    def __init__(self, filename: str):
        """This is the initial function of Recipe Book. It initiates the attributes of the class.

        Arguments:
            filename -- Recipe Book json filenmae

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
        """
        try:
            with open(filename, "r") as file:
                recipes: dict = json.load(file)
        except Exception as E:
            raise (E)

        self.recipes: dict = recipes
        self.bag: dict = {}

        self.possible_recipes: dict = {}

        self.grindlist: dict = {}
        self.grindcost: dict = {}
        self.grindleft: dict = {}

    def get_recipe_by_name(self, name: str) -> dict:
        """This function gets a recipe from an item name. If it isn't in the recipe book return an empty dict

        Arguments:
            name -- Recipe item name

        Returns:
            Recipe Dictionary from the recipe book
        """
        recipe_dict = {name: self.recipes.get(name, {})}
        return recipe_dict

    def is_recipe_possible(
        self, smth_lvl: int, recipe_name: str, recipe_count: int, bag: dict
    ) -> bool:
        """This function checks if a recipe is possible based on smth lvl and the items in the bag

        Arguments:
            smth_lvl -- Character smithing level
            recipe_name -- Recipe name
            recipe_count -- Recipe amount
            bag -- Inventory Bag

        Returns:
            True if possible else False
        """
        recipe = self.recipes[recipe_name]
        is_possible = True

        # Check smithing level requirements
        if smth_lvl and smth_lvl < recipe["smth_lvl_req"]:
            is_possible = False
            print(f"Not enough smth_lvl for {recipe_name}")

        else:
            rec_ingredients = recipe["ingredients"]

            # For all ingredients in recipe
            for rec_ing in rec_ingredients:
                # required ingredient counts for the recipe
                required = recipe_count * rec_ingredients[rec_ing]

                # If the ingredient is not a recipe and if there aren't any in the bag
                if rec_ing not in self.recipes and required > bag.get(rec_ing, 0):
                    is_possible = False

                    print(
                        f"Raw material not in bag for recipe: {recipe_name}; raw material: {rec_ing}"
                    )

                # If ingredient is a recipe but there isn't enough in the bag
                elif required > bag.get(rec_ing, 0):
                    # Subbtract from the required the ingredient quantity already in the bag
                    needed = required - bag.get(rec_ing, 0)

                    # Check if the recipe for the amount needed is possible
                    is_possible = self.is_recipe_possible(
                        smth_lvl,
                        rec_ing,
                        needed,
                        bag,
                    )
                # If any ingredient is impossible to obtain from bag
                if not is_possible:
                    break
        return is_possible

    def get_recipes_by_ingredients(
        self, ingredients: dict, smth_lvl: int = None
    ) -> dict:
        """This function gets the recipes based on a set of ingredients

        Arguments:
            ingredients -- Set of ingredients to use in recipe search

        Keyword Arguments:
            smth_lvl -- Character smithing Level (default: {None})

        Returns:
            Possible recipes with the given ingredients
        """
        recipes_dict = {}
        target_count = 1
        for target in self.recipes:
            is_possible = self.is_recipe_possible(
                smth_lvl, target, target_count, ingredients
            )
            if is_possible:
                print("p1:", target, is_possible)
            # If the recipe is still considered possible add it to the recipes dict
            if is_possible:
                recipes_dict.update(self.get_recipe_by_name(target))

        return recipes_dict

    def add_to_bag(self, bag: dict):
        """Add set of items to self.bag. It also updates the self.grindcost and self.possible_recipes

        Arguments:
            bag -- Set of items to add
        """
        # Add bag to Recipe Book Bag
        _update_dict_add(self.bag, bag)

        # Get Grindleft through a subtraction of the Recipe Book Bag to the grindcost
        grindcost = self.grindcost.copy()
        self.grindleft = _update_dict_sub(grindcost, self.bag)

        # Get possible recipes based on Recipe Book Bag
        self.possible_recipes = self.get_recipes_by_ingredients(self.bag)

    def get_item_cost(self, item: str, number: int) -> dict:
        """Get the cost in materials of certain number of one type of item.


        Arguments:
            item -- Item to evaluate
            number -- Item amount

        Returns:
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

        Arguments:
            item_list -- Dictionary with item names as keys and number of that item name as value

        Returns:
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

        Keyword Arguments:
            wishes -- Dictionary with items as key and quantity as value to represent the item grind wishes (default: {{}})
        """

        # Get cost for the new wishes
        wishes = {wish: wishes[wish] for wish in wishes if wishes[wish] > 0}
        cost = self.get_itemlist_cost(wishes)

        # Add wishes to Grindlist
        _update_dict_add(self.grindlist, wishes)

        # Add wishes cost to Grindcost
        _update_dict_add(self.grindcost, cost)

        # Update Grindleft based on Grindcost and Recipe Book Bag
        grindcost = self.grindcost.copy()
        self.grindleft = _update_dict_sub(grindcost, self.bag)

    def _get_stages(
        self, recipe_name: str, recipe_qtty: int, recipe: dict, stage: int = 1
    ) -> dict:
        """This function builds the recipe process in stages in a dict
        Structure:
        -------------
        stage_key:str : {
            recipe name->str:{
                'qtty': recipe_amount -> int
                'ingrediemts: {
                    ingredient_name->str: ingredient_amount->int
                }
            }
        }

        Arguments:
            recipe_name -- recipe name
            recipe_qtty -- recipe amount
            recipe -- recipe dict

        Keyword Arguments:
            stage -- starting stage (default: {1})

        Returns:
            Stages dict
        """
        stage_key = f"{stage}"

        # Fill current Stage
        ing_stages = {
            stage_key: {
                recipe_name: {
                    "qtty": recipe_qtty,
                    "ingredients": {
                        ing: qtty * recipe_qtty
                        for ing, qtty in recipe["ingredients"].items()
                    },
                }
            }
        }

        # Get next stage
        for ing, qtty in ing_stages[stage_key][recipe_name]["ingredients"].items():
            if ing in self.recipes:
                ing_stage = self._get_stages(
                    ing,
                    qtty,
                    self.recipes[ing],
                    stage=stage + 1,
                )
                _update_dict_add(ing_stages, ing_stage)

        return ing_stages

    def merge_dicts(self, dict_dest: dict, dict_src: dict):
        """This function adds a src dict to a dest dict, by adding the lowest level attributes

        Arguments:
            dict_dest -- Destinatio dict
            dict_src -- Source dict

        Returns:
            Merged dict
        """
        for key_src, value_src in dict_src.items():
            if dict_dest.get(key_src):
                if type(dict_dest[key_src]) == dict:
                    dict_dest[key_src] = self.merge_dicts(dict_dest[key_src], value_src)
                else:
                    dict_dest[key_src] += value_src
            else:
                dict_dest[key_src] = value_src
        return dict_dest

    def print_recipes_stages(self, recipes: Dict[str, int] = None, bag=None):
        """This function prints the recipe stages

        Keyword Arguments:
            recipes -- Recipes (default: {None})
            bag -- Bag (default: {None})
        """
        if recipes == None:
            recipes = self.grindlist if self.grindlist else self.recipes
            qttys = {recipe_name: 1 for recipe_name in self.recipes}
        else:
            qttys = recipes.copy()
            recipes = {
                recipe_name: self.get_recipe_by_name(recipe_name)[recipe_name]
                for recipe_name in recipes
            }

        if bag == None:
            bag = self.bag

        recipe_stages: Dict[str, Dict[str, dict]] = {}
        total_item_cost: Dict[str, int] = {}
        if len(recipes):
            for recipe_name, recipe in recipes.items():
                print("_" * 100)
                print("recipe_name:", recipe_name)

                recipe_qtty = qttys[recipe_name]
                recipe_stage = self._get_stages(recipe_name, recipe_qtty, recipe)
                n_stages = len(recipe_stage)
                stage_keys = list(recipe_stage.keys())
                for key in stage_keys:
                    recipe_stage[
                        "stage" + str(n_stages - int(key) + 1)
                    ] = recipe_stage.pop(key)
                recipe_stages[recipe_name] = recipe_stage

                print("recipe_stages:", recipe_stages)

            print(f"There are {len(recipe_stages)} stages")

            for recipe_name, stage in recipe_stages.items():
                print(f"{recipe_name} recipe plan:")
                recipe_cost = self.get_item_cost(recipe_name, qttys[recipe_name])
                _update_dict_add(total_item_cost, recipe_cost)

                for stage_name, stage_items in stage.items():
                    print(f"\t{stage_name}")
                    for item_name, item_details in stage_items.items():
                        item_qtty = item_details["qtty"]
                        print(f"\t\tCraft {item_name} x{item_qtty}")
                        ings = [
                            f"{ing_name} x{ing_qtty}"
                            for ing_name, ing_qtty in item_details[
                                "ingredients"
                            ].items()
                        ]
                        ing_line = " ; ".join(ings)
                        print(f"\t\tIngredients:", ing_line)
                print("Recipe Total Cost: ")
                for item, item_qtty in recipe_cost.items():
                    print(f"\t{item} x{item_qtty}")

    def _print_possible_recipies(self):
        """This function prints possible recipes"""
        print(f"Possible Recipes:")
        for recipe in self.possible_recipes:
            print(f"\t{recipe}")

            ingredients = self.possible_recipes[recipe]["ingredients"]
            [print(f"\t\t * {ing} x{ingredients[ing]}") for ing in ingredients]

    def print_inventory(self):
        """This function prints the current Inventory and current Possible Recipes"""
        print_hline()
        print(f"Inventory:")
        for item in self.bag:
            print(f"\t - {item} x{self.bag[item]}")

        self._print_possible_recipies()
        print_hline()

    def print_grindlist(self):
        """This function prints the grindlist, grindcost and grindleft"""
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
    # Open recipes Json
    recipes_json_filename = "recipes.json"

    # Build Recipe Book
    recipe_book = RecipeBook(filename=recipes_json_filename)

    # Initiate Inventory Bag
    bag = {"Crimson_String": 20, "Cue_Tape": 5, "Spore_Cap": 10, "Copper_Bar": 10000}

    # Initiate Grindlist
    grindlist = {"Gold_Helmet": 1, "Platinum_Helmet": 1, "Boxing_Gloves": 0}

    # Add Inventory Bag to Recipe Book
    recipe_book.add_to_bag(bag)
    # Add Grindlist to Recipe Book
    recipe_book.add_to_grindlist(grindlist)

    # Print Inventory
    recipe_book.print_inventory()

    # Print Grindlist
    recipe_book.print_grindlist()
