import pandas as pd
from typing import Dict, Tuple
import json
from utils.config import config

# This program reads the recipes.csv, created in excel from idelon wiki, to build the recipes.json

recipes_filename = config["RECIPES_CSV"]
raw_data_json_filename = config["RAW_DATA_JSON"]
recipes_map = pd.read_csv(recipes_filename, header=0, delimiter=",")


def add_recipes(
    recipes: Dict[str, dict], new_recipes: Dict[str, dict]
) -> Tuple[Dict[str, dict], list, list]:
    """This function adds new_recipes to recipes

    Arguments:
        recipes -- Recipe dict to add the new_recipes
        new_recipes -- New recipes dict to add

    Returns:
        - The extended recipe dict
        - List of added recipes
        - List of ignored recipes
    """
    added_recipes = []
    not_added_recipes = list(new_recipes)
    for recipe_target in new_recipes:
        if not recipes.get(recipe_target):
            recipes[recipe_target] = new_recipes[recipe_target]
            added_recipes += [recipe_target]
            not_added_recipes.remove(recipe_target)
        else:
            print(
                f"ERROR: Tried the recipe you tried to add already exists. Recipe target: {recipe_target}"
            )
    return recipes, added_recipes, not_added_recipes


def build_recipe(
    target: str = "UNKNOWN",
    requirements: Dict[str, int] = {},
) -> Dict[str, dict]:
    """This function builds a recipe, given a recipe name and the recipe requirements

    Keyword Arguments:
        target -- _description_ (default: {"UNKNOWN"})
        requirements -- _description_ (default: {{}})

    Returns:
        Recipe dict
    """
    return {target: requirements}


def build_requirements(
    ingredients: Dict[str, int] = {},
    smithing_level_req: int = -1,
    recipe_source: str = "UNKNOWN",
    anvil_tab: int = -1,
    recipe_id: int = -1,
) -> Dict[str, object]:
    """This function builds a recipe requirements

    Keyword Arguments:
        ingredients -- Ingredient dict with ingredient names as keys and required amount as value (default: {{}})
        smithing_level_req -- Smithing level required to craft the recipe (default: {-1})
        recipe_source -- Recipe source (default: {"UNKNOWN"})
        anvil_tab -- Anvil Tab Group (default: {-1})
        recipe_id -- Recipe id (default: {-1})

    Returns:
        Recipe requirements
    """
    return {
        "ingredients": ingredients,
        "smth_lvl_req": smithing_level_req,
        "recipe_source": recipe_source,
        "anvil_tab": anvil_tab,
        "recipe_id": recipe_id,
    }


def parse_ingredients(row: pd.Series) -> Dict[str, int]:
    """This function parse the rows in a recipe dataframe, created from a csv, to build a recipe ingredients dict.

    Arguments:
        row -- Dataframe row Series with columns: Recipe_no; Name; Smithing_Level_Required; Resource1; Resource2; Resource3; Resource4; Source; Anvil_Tab

    Returns:
        Ingredient Dict with ingredient names as keys and amounts as values
    """
    keys = [key for key in row.keys() if "Resource" in key]
    ingredients = {}
    for key in keys:
        resource = row[key]
        if isinstance(resource, str):
            [name, quantity] = resource.split(" x")
            quantity = int(quantity)

            ingredient = {name: quantity}
            ingredients.update(ingredient)
    return ingredients


if __name__ == "__main__":
    # Start with an empty recipe book
    recipe_book = {}

    # for each recipe
    for r_id, row in recipes_map.iterrows():
        recipe_name = row["Name"]
        recipe_id = row["Recipe_no"]
        smth_lvl_req = row["Smithing_Level_Required"]
        recipe_source = row["Source"]
        anvil_tab = row["Anvil_Tab"]

        # Get ingredients
        ingredients = parse_ingredients(row)

        # Get requirements
        requirements = build_requirements(
            ingredients=ingredients,
            smithing_level_req=smth_lvl_req,
            recipe_source=recipe_source,
            anvil_tab=anvil_tab,
            recipe_id=recipe_id,
        )

        # Build recipe
        recipe = build_recipe(target=recipe_name, requirements=requirements)

        # Add recipe
        recipe_book, added, not_added = add_recipes(
            recipes=recipe_book, new_recipes=recipe
        )

    # Save recipe book as a json
    with open(raw_data_json_filename, "w") as outfile:
        json.dump(recipe_book, outfile)
