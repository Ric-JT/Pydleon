import json
from typing import Dict, List
import pandas as pd

from utils.raw_field_parser import RawFieldParser
from utils.handle_cake import CakeHandler
from utils.config import config
from resources.template_data import cake_template
from maps.itemMap import item_map
from maps.maps import (
    obol_name_map,
    char_subclass_map,
)
from maps.cardEquipMap import card_equip_map
from maps.talentMap import talent_map
from maps.mobMap import mob_map
from maps.cardLevelMap import card_level_map


def print_hline(n: int = 100):
    """This function prints a sequence of '_', by default 100 sequence length

    Keyword Arguments:
        n -- Sequence Length (default: {100})
    """
    print("_" * n)


def create_refinery_data(fields: dict) -> Dict[str, dict]:
    """This function creates the refinery data

    Arguments:
        fields -- fields from the raw data json as a dict

    Returns:
        Refinery data dict
    """
    # 0 =
    # 1 = inventory
    # 2 =
    # 3 = redox salt
    # 3[0] = refined (unclaimed)
    # 3[1] = rank
    # 3[2] = ???
    # 3[3] = on/off
    # 3[4] = auto-refine percent
    # 4 = explosive salt
    # 5 = spontaneity salt
    # 6 = dioxide salt
    # 7 = red salt
    # 8 = red salt 2

    # load rawRefinery
    rawRefinery = json.loads(fields["Refinery"])

    refinery = {}
    refinery["salts"] = {}

    # this is how they are named in the template file
    salts = ["redox", "explosive", "spontaneity", "dioxide", "red", "red2"]
    for ix, salt in enumerate(salts):
        # redox starts at index 3, so it has such an offset
        rawSalt = rawRefinery[ix + 3]
        refinery["salts"][salt] = {
            "refined": rawSalt[0],
            "rank": rawSalt[1],
            "state": "on" if rawSalt[3] == 1 else "off",
            "autoPercent": rawSalt[4],
        }
        # TODO add refinery storage

    return refinery


def fill_characters_data(chars: list, parser: RawFieldParser) -> list:
    """This function fills the characters data

    Arguments:
        chars -- Characters array with every character dict partially updated
        parser -- Parser responsible to parse each character dict key.

    Returns:
        Characters array updated with characters data
    """
    for i, _ in enumerate(chars):
        print(chars[i]["name"])
        chars[i]["class"]: str = parser.get_char_class(i)
        chars[i]["money"]: int = parser.get_char_money(i)
        chars[i]["AFKtarget"]: str = parser.get_char_AFKtarget(i)
        chars[i]["currentMap"]: int = parser.get_char_currentMap(i)
        chars[i]["npcDialogue"]: Dict[str, int] = parser.get_char_npcDialog(i)
        chars[i]["timeAway"]: int = parser.get_char_AFKtime(i)
        chars[i]["instaRevives"]: int = parser.get_char_instaRevives(i)
        chars[i]["gender"]: int = parser.get_char_gender(i)
        chars[i]["minigamePlays"]: int = parser.get_char_minigames(i)
        chars[i].update(parser.get_char_statlist(i))  # Stat list, STR, DEF, etc
        chars[i]["POBoxUpgrades"]: List[int] = parser.get_char_POBoxUpgrades(i)
        chars[i]["invBagsUsed"]: List[int] = parser.get_char_invBagsUsed(i)
        chars[i]["inventory"] = parser.get_char_inventory(i)
        chars[i].update(parser.get_char_equipment(i))  # armor + tools
        chars[i]["obols"] = parser.get_char_obols(i)
        chars[i]["statueLevels"] = parser.get_char_statues(i)
        chars[i]["cardsEquip"] = parser.get_char_cards(i)
        chars[i]["cardSetEquip"] = parser.get_char_card_set(i)
        chars[i]["skillLevels"] = parser.get_char_skill_levels(i)
        chars[i]["starSigns"] = parser.get_char_star_signs(i)
        chars[i].update(parser.get_char_tlnt_lvls(i))  # talents + star talents levels
        chars[i]["attackLoadout"] = parser.get_char_atk_loadout(i)
        chars[i]["fishingToolkitEquipped"] = parser.get_char_fishing_toolkit(i)
        chars[i]["bubblesEquipped"] = parser.get_char_bubbles(i)
        chars[i]["anvil"]["production"] = parser.get_char_anvil(i)
    return chars


def fill_account_data(account: dict, characters: list, fields: dict) -> dict:
    """This function fills the account data.

    Arguments:
        account -- Account container attribute
        characters -- Characters array
        fields -- fields from the raw data json as a dict

    Returns:
        Updated Account Data
    """
    account["chestBank"] = fields["MoneyBANK"]

    # chest
    chestOrder = [
        item_map.get(item_name, "UNKNOWN") for item_name in fields["ChestOrder"]
    ]
    chestQuantity = fields["ChestQuantity"]
    account["chest"] = [
        {item_name: int(count) if type(count) == str else count}
        for item_name, count in zip(chestOrder, chestQuantity)
    ]

    # obols
    obolNames = [obol_name_map.get(obol, "UNKNOWN") for obol in fields["ObolEqO1"]]
    obolBonusMap = json.loads(fields["ObolEqMAPz1"])
    plainObolData = [
        {"name": obolNames[id], "bonus": {}} for id, _ in enumerate(obolNames)
    ]
    for key in obolBonusMap:
        plainObolData[int(key)]["bonus"] = obolBonusMap[key]
    account["obols"] = plainObolData

    # TaskZZ0 = Current milestone in uncompleted task
    # TaskZZ1 = Completed Task Count
    # TaskZZ2 = merit shop purchases
    # TaskZZ3 = crafts unlocked
    # TaskZZ4 = total unlock points & unspent merit points
    # TaskZZ5 = current daily tasks
    taskData = cake_template["account"]["tasks"]
    # unlocked
    ZZ1 = json.loads(fields["TaskZZ1"])
    taskData["unlocked"]["world1"] = ZZ1[0]
    taskData["unlocked"]["world2"] = ZZ1[1]
    taskData["unlocked"]["world3"] = ZZ1[2]
    # milestoneProgress
    ZZ0 = json.loads(fields["TaskZZ0"])
    taskData["milestoneProgress"]["world1"] = ZZ0[0]
    taskData["milestoneProgress"]["world2"] = ZZ0[1]
    taskData["milestoneProgress"]["world3"] = ZZ0[2]
    # meritsOwned
    ZZ2 = json.loads(fields["TaskZZ2"])
    taskData["meritsOwned"]["world1"] = ZZ2[0]
    taskData["meritsOwned"]["world2"] = ZZ2[1]
    taskData["meritsOwned"]["world3"] = ZZ2[2]
    # craftsUnlocked
    ZZ3 = json.loads(fields["TaskZZ3"])
    taskData["craftsUnlocked"]["world1"] = ZZ3[0]
    taskData["craftsUnlocked"]["world2"] = ZZ3[1]
    taskData["craftsUnlocked"]["world3"] = ZZ3[2]
    account["tasks"] = taskData

    # stamps
    stampData = cake_template["account"]["stamps"]
    # combat
    stampData["combat"] = {
        int(level): fields["StampLv"][0][level]
        for level in fields["StampLv"][0]
        if level != "length"
    }
    # skills
    stampData["skills"] = {
        int(level): fields["StampLv"][1][level]
        for level in fields["StampLv"][1]
        if level != "length"
    }
    # misc
    stampData["misc"] = {
        int(level): fields["StampLv"][2][level]
        for level in fields["StampLv"][2]
        if level != "length"
    }
    account["stamps"] = stampData

    # forge
    account["forge"]["level"] = [int(level) for level in fields["ForgeLV"]]

    # alchemy
    alchemyData = fields["CauldronInfo"]
    account["alchemy"]["bubbleLevels"]["power"] = {
        int(level): alchemyData[0][level]
        for level in alchemyData[0]
        if level != "length"
    }
    account["alchemy"]["bubbleLevels"]["quick"] = {
        int(level): alchemyData[1][level]
        for level in alchemyData[1]
        if level != "length"
    }
    account["alchemy"]["bubbleLevels"]["highIq"] = {
        int(level): alchemyData[2][level]
        for level in alchemyData[2]
        if level != "length"
    }
    account["alchemy"]["bubbleLevels"]["kazam"] = {
        int(level): alchemyData[3][level]
        for level in alchemyData[3]
        if level != "length"
    }
    account["alchemy"]["vialLevels"] = {
        int(level): alchemyData[4][level]
        for level in alchemyData[4]
        if level != "length"
    }

    # highest class data
    highest_classes = []
    for c in characters:
        row = {
            "class": char_subclass_map.get(c["class"], f"UNKNOWN-{c['class']}"),
            "level": c["level"],
        }
        highest_classes += [row]

    df = pd.DataFrame(highest_classes)
    df["level"] = df["level"].astype(int)
    df.reset_index()
    ids = list(df.groupby(by=["class"], as_index=False, sort=False).idxmax()["level"])
    levels = list(df.groupby(by=["class"], as_index=False, sort=False).max()["level"])

    account["highestClasses"] = {id: level for id, level in zip(ids, levels)}

    # minigame high scores
    minigameHighscores = fields["FamValMinigameHiscores"]
    account["minigameHighscores"]["chopping"] = int(minigameHighscores[0])
    account["minigameHighscores"]["fishing"] = int(minigameHighscores[1])
    account["minigameHighscores"]["catching"] = int(minigameHighscores[2])
    account["minigameHighscores"]["mining"] = int(minigameHighscores[3])

    # highest item counts
    cols_to_count = ["Copper Ore", "Oak Logs", "Grass Leaf"]
    for item in account["chest"]:
        for col in cols_to_count:
            if col in item:
                account["highestItemCounts"][col] = item[col]

    # cards
    rawCardsData = json.loads(fields["Cards0"])
    cleanCardData = {}
    for key in rawCardsData.keys():
        lookup = mob_map.get(key, "UNKNOWN")
        count = int(rawCardsData[key])
        base = card_level_map.get(key, f"UNKNOWN-{key}")
        if count == 0:
            starlevel = "Not Found"
        elif count > base * 5:
            starlevel = "4 Star"
        elif count >= base * 4:
            starlevel = "3 Star"
        elif count >= base * 3:
            starlevel = "2 Star"
        elif count >= base * 2:
            starlevel = "1 Star"
        else:
            starlevel = "Acquired"

        cleanCardData[lookup] = {
            "collected": count,
            "starLevel": starlevel,
        }
    account["cards"] = cleanCardData

    # bribes
    bribes = fields["BribeStatus"]
    account["bribes"] = bribes
    # TODO add map for bribe names?

    # refinery
    account["refinery"] = create_refinery_data(fields)

    # quests complete (possibly temporary for use in spreadsheet)
    quests = {}
    n_chars = len(characters)
    for n in range(n_chars):
        lookup = f"QuestComplete_{n}"
        quests[lookup] = json.loads(fields[lookup])

    account["quests"] = quests

    # looty mc shooty raw display

    account["looty"] = json.loads(fields["Cards1"])

    # purchases
    rawBundles = json.loads(fields["BundlesReceived"])
    rawBundles.update({int(rawBundles[key]) for key in rawBundles})
    account["bundlesPurchased"] = rawBundles

    # anvil crafts unlocked
    # currently 0 = unlocked, -1 = locked. Might change to a better value
    rawAnvil = json.loads(fields["AnvilCraftStatus"])
    account["anvilCraftsUnlocked"]["tab1"] = rawAnvil[0]
    account["anvilCraftsUnlocked"]["tab2"] = rawAnvil[1]
    account["anvilCraftsUnlocked"]["tab3"] = rawAnvil[2]

    # cogs

    rawCogPositions = json.loads(fields["CogO"])
    rawCogData = json.loads(fields["CogM"])
    working_cogs = rawCogData.keys()
    cogs = []

    cogs = [
        {
            rawCogPositions[ix]: (
                rawCogData[f"{ix}"]
                if f"{ix}" in working_cogs
                else {"a": None, "b": None}
            )
        }
        for ix, cogName in enumerate(rawCogPositions)
    ]

    account["cogs"] = cogs

    return account


def fillGuildData(guildInfo: dict) -> dict:
    """This function fills the Guild Data

    Arguments:
        guildInfo -- Guild information

    Returns:
        Updated guildInfo
    """

    res = {}
    res["id"] = guildInfo["i"]
    res["name"] = guildInfo["n"]
    res["bonuses"] = guildInfo["stats"]

    return res


def print_line(ids: List[str], values: list, prefix: str = "", separators: list = None):
    """This function prints a line with the respective ids and values, with possible costumization with prefix and separators

    Arguments:
        ids -- List of ids
        values -- Values that correspond to he ids

    Keyword Arguments:
        prefix -- prefix that may be needed (default: {""})
        separators -- separator between ids (default: {None})
    """
    separators = [":"] * len(values) if not separators else separators
    lines = []
    line = []
    for id, value, separator in zip(ids, values, separators):
        if type(value) == dict:
            line += [prefix + f"{id}{separator}"]
            new_prefix = prefix + "\t"
            dict_lines = []
            dict_line = []
            counter = 0
            for key in value:
                if type(value[key]) == dict:
                    dict_line += [f"{key}{separator} {value[key]}"]
                    dict_lines += [new_prefix + " \t ".join(dict_line)]
                    dict_line = []
                elif (
                    type(value[key]) == list
                    and len(value[key])
                    and type(value[key][0]) == dict
                ):
                    new_new_prefix = new_prefix + "\t"
                    for prod_item_info in value[key]:
                        if type(prod_item_info) == dict:
                            for key2 in prod_item_info:
                                dict_line += [
                                    f"{key2}{separator} {prod_item_info[key2]}"
                                ]
                        else:
                            dict_line += [f"{key}{separator} {prod_item_info}"]
                        dict_lines += [new_new_prefix + " \t ".join(dict_line)]
                        dict_line = []

                else:
                    dict_line += [f"{key}{separator} {value[key]}"]
                    counter += 1
                    if counter % 5 == 0:
                        dict_lines += [new_prefix + " \t ".join(dict_line)]
                        dict_line = []
            if len(dict_line):
                dict_lines += [new_prefix + " \t ".join(dict_line)]

            line += ["\n".join(dict_lines)]
        elif type(value) == list and len(value):
            if type(value[0]) == dict:
                line += [prefix + f"{id}{separator}"]
                dict_lines = []
                dict_line = []
                counter = 0
                new_prefix = prefix + "\t"
                for dict_el in value:
                    dict_keys = dict_el.keys()
                    for key in dict_keys:
                        counter += 1
                        if type(dict_el[key]) == dict:
                            dict_line += [
                                new_prefix + f"{key}{separator} {dict_el[key]}"
                            ]
                            if counter % 2 == 0:
                                dict_lines += [new_prefix + " \t ".join(dict_line)]
                                dict_line = []
                        else:
                            dict_line += [f"{key}{separator} {dict_el[key]}"]
                            if counter % 2 == 0:
                                dict_lines += [new_prefix + " \t ".join(dict_line)]
                                dict_line = []
                dict_lines += [new_prefix + " \t ".join(dict_line)]

                line += ["\n".join(dict_lines)]
            else:
                line += [prefix + f"{id}{separator} {value}"]

        else:
            line += [prefix + f"{id}{separator} {value}"]

    lines += line
    message = " ".join(lines)
    print(message)


def print_characters(chars: list):
    """This Function prints all the characters info

    Arguments:
        chars -- Characters information
    """
    for ch in chars:
        columns = ["name", "class", "level"]
        line = ["", "", "lv."]
        values = [ch[column] for column in columns]
        seps = ["", "", ""]
        print_line(line, values, separators=seps)

        columns = ["strength", "agility", "wisdom"]
        line = [column.capitalize() for column in columns]
        values = [ch[column] for column in columns]
        print_line(line, values)

        columns = [
            "money",
            "AFKtarget",
            "currentMap",
            "npcDialogue",
            "timeAway",
            "instaRevives",
            "gender",
            "minigamePlays",
        ]
        for column in columns:
            print_line([column.capitalize()], [ch[column]])

        columns = [
            "POBoxUpgrades",
            "invBagsUsed",
            "inventory",
            "equipment",
            "tools",
            "food",
            "obols",
            "statueLevels",
            "cardsEquip",
            "cardSetEquip",
            "skillLevels",
            "starSigns",
            "talentLevels",
            "starTalentLevels",
            "fishingToolkitEquipped",
            "bubblesEquipped",
            "anvil",
            "attackLoadout",
        ]

        for column in columns:
            print_line([column.capitalize()], [ch[column]])

        print_hline()


def print_account(account: dict):
    """This function prints the Account Data

    Arguments:
        account -- Account data
    """
    columns = ["chestBank"]
    values = [account[column] for column in columns]
    line = ["Bank Money"]
    print_line(line, values)

    columns = [
        "chest",
        "obols",
        "tasks",
        "stamps",
        "forge",
        "alchemy",
        "highestClasses",
        "minigameHighscores",
        "highestItemCounts",
        "cards",
        "bribes",
        "refinery",
        "quests",
        "looty",
        "bundlesPurchased",
        "anvilCraftsUnlocked",
        "cogs",
        "Guild",
    ]

    for column in columns:
        print_line([column.capitalize()], [account[column]])


def save_json(json_data: dict, filename: str = "new_json.json", indent: int = 4):
    """This saves a dict in a json with a given indent

    Arguments:
        json_data -- Json data as a dict

    Keyword Arguments:
        filename -- json filename (default: {"new_json.json"})
        indent -- indent number (default: {4})
    """
    with open(filename, "w") as fp:
        json.dump(json_data, fp, indent=indent)


def prepare_dough(flour: dict) -> dict:
    """This prepares the "raw dough" by building a dict with custom charNameData and guildInfo and with the raw data from the raw json

    Arguments:
        flour -- Raw data from raw json

    Returns:
        Raw Dough - dict resulting of the combination of the three ingredients- charNameData, guildInfo, saveData(flour)
    """
    charNameData = [
        "Mr_Piggao",
        "Miss_Piggy",
        "Piggy_Jr",
        "Sr_Puerco",
        "Grand_Pigdalf",
        "Pigolas",
        "Pigliota",
        "Ditto_Piggo",
    ]

    guildInfo = {
        "i": 31,
        "n": "Jaegerists",
        "stats": [2, 6, 5, 15, 6, 0, 5, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    }
    dough = {
        "charNameData": charNameData,
        "guildInfo": guildInfo,
        "saveData": flour,
    }

    return dough


def bake_dough(dough: dict) -> dict:
    """This function initializes processes and fills the structure of the final cake

    Arguments:
        dough -- Dict with Char Name Data, Guild Info and the raw data from the json

    Returns:
        Fill dough
    """

    res = {}
    numChars = len(dough["charNameData"])
    fields = dough["saveData"]
    parser = RawFieldParser(fields)
    guildInfo = dough["guildInfo"]
    characters = []
    for i in range(numChars):
        newCharacter = cake_template["characters"].copy()
        newCharacter["name"] = dough["charNameData"][i]
        characters += [newCharacter]

    res["characters"] = fill_characters_data(
        characters,
        parser,
    )

    res["account"] = fill_account_data(
        cake_template["account"], res["characters"], fields
    )

    res["account"]["Guild"] = fillGuildData(guildInfo)
    return res


if __name__ == "__main__":
    filename = config["RAW_DATA_JSON"]
    cake_filename = config["CAKE_FILENAME"]

    with open(filename, "r") as fp:
        saveData = json.load(fp)

    dough = prepare_dough(saveData)

    cake = bake_dough(dough)

    save_json(cake, filename=cake_filename)

    # -------------------------------------------------------
    # Try Cake
    cake_handler = CakeHandler(cake_filename)

    inventory = cake_handler.get_char_inventory(0)
    print_hline()
    print_hline()

    # print_characters(cake["characters"])
    print_account(cake["account"])
