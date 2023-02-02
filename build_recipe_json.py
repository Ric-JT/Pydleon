import pandas as pd
from typing import Dict, Tuple
import json

items_ids_filename = "resources/items_ids.csv"
recipes_filename = "resources/recipes.csv"

item_id_map = pd.read_csv(items_ids_filename, header=0, delimiter=",")
recipes_map = pd.read_csv(recipes_filename, header=0, delimiter=",")


def add_recipes(recipes: Dict[str, dict], new_recipes: Dict[str, dict]) -> Tuple[Dict[str, dict], list, list]:
    added_recipes = []
    not_added_recipes = list(new_recipes.keys())
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
    return {target: requirements}


def build_requirements(
    ingredients: Dict[str, int] = {},
    smithing_level_req: int = -1,
    recipe_source: str = "UNKNOWN",
    anvil_tab: int = -1,
    recipe_id: int = -1,
) -> Dict[str, object]:
    return {
        "ingredients": ingredients,
        "smth_lvl_req": smithing_level_req,
        "recipe_source": recipe_source,
        "anvil_tab": anvil_tab,
        "recipe_id": recipe_id,
    }


def parse_ingredients(row):
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
    recipes = {}

    for r_id, row in recipes_map.iterrows():
        recipe_name = row["Name"]
        recipe_id = row["Recipe_no"]
        smth_lvl_req = row["Smithing_Level_Required"]
        recipe_source = row["Source"]
        anvil_tab = row["Anvil_Tab"]

        ingredients = parse_ingredients(row)

        requirements = build_requirements(
            ingredients=ingredients,
            smithing_level_req=smth_lvl_req,
            recipe_source=recipe_source,
            anvil_tab=anvil_tab,
            recipe_id=recipe_id,
        )

        recipe = build_recipe(target=recipe_name, requirements=requirements)

        recipes, added, not_added = add_recipes(recipes=recipes, new_recipes=recipe)

    with open("sample.json", "w") as outfile:
        json.dump(recipes, outfile)
