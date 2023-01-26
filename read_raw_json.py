import json
from typing import Dict, List
import pandas as pd

from utils.parsing.raw_field_parser import RawFieldParser
from template_data import cake_template
from maps.classTalentMap import class_index_map, class_talent_map, class_talent_page_map
from maps.itemMap import item_map
from maps.maps import (
    obol_name_map,
    card_set_map,
    skill_index_map,
    star_sign_map,
    fishing_bait_map,
    fishing_line_map,
    large_bubble_map,
    char_subclass_map,
)
from maps.cardEquipMap import card_equip_map
from maps.talentMap import talent_map
from maps.mobMap import mob_map
from maps.cardLevelMap import card_level_map


def print_hline(n: int = 100):
    print("_" * n)


def create_refinery_data(fields):
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


def fill_characters_data(
    chars: list, numChars: int, fields, parser: RawFieldParser
) -> list:
    for i in range(numChars):
        chars[i]["class"]: str = parser.get_char_class(i)
        chars[i]["money"]: int = parser.get_char_money(i)
        chars[i]["AFKtarget"]: str = parser.get_char_AFKtarget(i)
        chars[i]["currentMap"]: int = parser.get_char_currentMap(i)
        chars[i]["npcDialogue"]: Dict[str, int] = parser.get_char_npcDialog(i)
        chars[i]["timeAway"]: int = parser.get_char_AFKtime(i)
        chars[i]["instaRevives"]: int = parser.get_char_instaRevives(i)
        chars[i]["gender"]: int = parser.get_char_gender(i)
        chars[i]["minigamePlays"]: int = parser.get_char_minigames(i)
        chars[i].update(parser.get_char_statlist(i))
        chars[i]["POBoxUpgrades"]: List[int] = parser.get_char_POBoxUpgrades(i)
        chars[i]["invBagsUsed"]: List[int] = parser.get_char_invBagsUsed(i)
        chars[i]["inventory"] = parser.get_char_inventory(i)

        equipableNames = fields[f"EquipOrder_{i}"]
        equipableCounts = fields[f"EquipQTY_{i}"]

        rawEquipmentNames = [
            item_map.get(equipableNames[0][equip_name], "UNKNOWN")
            for equip_name in equipableNames[0]
            if equip_name != "length"
        ]
        rawEquipmentCounts = [
            equipableCounts[0][equip_name]
            for equip_name in equipableCounts[0]
            if equip_name != "length"
        ]
        plainEquipmentData = [
            {equip_name: count}
            for equip_name, count in zip(rawEquipmentNames, rawEquipmentCounts)
        ]
        # add upgrade stone data
        # IMm_# = players inventory (todo later as it isn't usefull for calculations)
        # EMm0_# = equips
        # EMm1_# = tools
        equipmentStoneData = json.loads(fields[f"EMm0_{i}"])

        blankData = {
            "Defence": 0,
            "WIS": 0,
            "STR": 0,
            "LUK": 0,
            "Weapon_Power": 0,
            "AGI": 0,
            "Reach": 0,
            "Upgrade_Slots_Left": 0,
            "Power": 0,
            "Speed": 0,
            "UQ1val": 0,
        }

        # add blank data to everything in the list first
        for j in range(len(plainEquipmentData)):
            plainEquipmentData[j]["stoneData"] = blankData

        # go through stone data and add any that need to be added
        keys = equipmentStoneData.keys()
        for key in keys:
            # (hacky fix) some weapon power is stored as "Weapon_Power" instead of "Power"
            # if that happens, just add "Power" with the same value
            if "Weapon_Power" in equipmentStoneData[key].keys():
                equipmentStoneData[key]["Power"] = equipmentStoneData[key][
                    "Weapon_Power"
                ]

            plainEquipmentData[int(key)]["stoneData"] = equipmentStoneData[key]

        chars[i]["equipment"] = plainEquipmentData

        rawToolNames = [
            item_map.get(equipableNames[1][tool_name], "UNKNOWN")
            for tool_name in equipableNames[1]
            if tool_name != "length"
        ]
        rawToolCounts = [
            equipableCounts[1][tool_name]
            for tool_name in equipableCounts[1]
            if tool_name != "length"
        ]

        plainToolData = [
            {tool_name: count} for tool_name, count in zip(rawToolNames, rawToolCounts)
        ]
        toolStoneData = json.loads(fields[f"EMm1_{i}"])

        # add blank data to everything in the list first
        for j in range(len(plainToolData)):
            plainToolData[j]["stoneData"] = blankData

        # go through stone data and add any that need to be added
        keys = toolStoneData.keys()
        for key in keys:
            # (hacky fix) some weapon power is stored as "Weapon_Power" instead of "Power"
            # if that happens, just add "Power" with the same value
            if "Weapon_Power" in toolStoneData[key].keys():
                toolStoneData[key]["Power"] = toolStoneData[key]["Weapon_Power"]

            plainToolData[int(key)]["stoneData"] = toolStoneData[key]

        chars[i]["tools"] = plainToolData

        rawFoodNames = [
            item_map.get(equipableNames[2][food_name], "UNKNOWN")
            for food_name in equipableNames[2]
            if food_name != "length"
        ]
        rawFoodCounts = [
            equipableCounts[2][food_name]
            for food_name in equipableCounts[2]
            if food_name != "length"
        ]
        chars[i]["food"] = [
            {food_name: count} for food_name, count in zip(rawFoodNames, rawFoodCounts)
        ]

        # obols
        obolNames = [
            obol_name_map.get(obol_name, "UNKNOWN")
            for obol_name in fields[f"ObolEqO0_{i}"]
        ]
        obolMap = json.loads(fields[f"ObolEqMAP_{i}"])

        plainObolData = [
            {"name": obolNames[id], "bonus": {}} for id, _ in enumerate(obolNames)
        ]
        for key in obolMap:
            plainObolData[int(key)]["bonus"] = obolMap[key]

        chars[i]["obols"] = plainObolData

        statueArray = json.loads(fields[f"StatueLevels_{i}"])
        statueItems = []
        for statue in statueArray:
            statueItems += [{"level": int(statue[0]), "progress": statue[1]}]

        chars[i]["statueLevels"] = statueItems

        cardsArray = [
            card_equip_map.get(card_id, "UNKNOWN")
            for card_id in fields[f"CardEquip_{i}"]
        ]

        chars[i]["cardsEquip"] = cardsArray

        rawCardSet = json.loads(fields[f"CSetEq_{i}"])
        cardSetName = rawCardSet
        chars[i]["cardSetEquip"] = [
            card_set_map.get(name, "UNKNOWN") for name in cardSetName
        ]

        rawSkillLevels = fields[f"Lv0_{i}"]
        unmappedSkillLevels = [int(skill) for skill in rawSkillLevels]
        mappedSkillLevels = {}
        for skill_index, skill_level in enumerate(unmappedSkillLevels):

            if skill_level != -1:
                mappedSkillLevels[
                    skill_index_map.get(skill_index, f"UNKNOWN-{skill_index}")
                ] = skill_level

        chars[i]["skillLevels"] = mappedSkillLevels

        rawStarSignData = fields[f"PVtStarSign_{i}"]
        starSignSplit = rawStarSignData.split(",")
        for sign_index, sign in enumerate(starSignSplit):
            starSignSplit[sign_index] = sign.replace("_", "-1")
            if sign == "":
                starSignSplit[sign_index] = "-1"

        starSign1 = star_sign_map.get(int(starSignSplit[0]), "None")
        starSign2 = star_sign_map.get(int(starSignSplit[1]), "None")
        starSignFinal = [starSign1, starSign2]
        chars[i]["starSigns"] = starSignFinal

        unmappedTalents = json.loads(fields[f"SL_{i}"])

        mappedTalents = {
            talent_map.get(int(key), "UNKNOWN"): unmappedTalents[key]
            for key in unmappedTalents.keys()
        }

        # regular talents
        talentPages = class_talent_map.get(chars[i]["class"], "UNKNOWN")

        orderedClassTalents = []

        for key in talentPages:
            orderedClassTalents += class_talent_page_map.get(
                "Savvy Basics" if key == "Savy Basics" else key, ["UNKNOWN"]
            )

        indexedTalents = {
            class_tenant: mappedTalents.get(class_tenant, "-1")
            for class_tenant in orderedClassTalents
        }

        chars[i]["talentLevels"] = indexedTalents

        starTalentList = class_talent_page_map["Star Talents"]
        starTalentIndexed = {}
        counter = 0
        for starTalent in starTalentList:
            if starTalent == "FILLER":
                starLevel = 0
                starTalent += f"_{counter}"
                counter += 1

            else:
                starLevel = mappedTalents.get(starTalent, -1)

            starTalentIndexed.update({starTalent: starLevel})

        chars[i]["starTalentLevels"] = starTalentIndexed

        # talent attack loadout
        unmappedLoadoutRaw = json.loads(fields[f"AttackLoadout_{i}"])
        # merge them all into one array
        unmappedLoadout = []

        for key in unmappedLoadoutRaw:
            unmappedLoadout += key

        # change talent IDs to their in-game names
        mappedLoadout = []
        for talentId in unmappedLoadout:
            if talentId != "Null":
                mappedLoadout += [talent_map.get(talentId, "Unknown")]

        # change talent names to their readable form
        for ix, word in enumerate(mappedLoadout):
            mappedLoadout[ix] = " ".join(
                [w.capitalize() for w in word.lower().split("_")]
            )

        chars[i]["attackLoadout"] = mappedLoadout
        chars[i]["fishingToolkitEquipped"]["bait"] = fishing_bait_map.get(
            int(fields[f"PVFishingToolkit_{i}"][0]), "UNKNOWN"
        )
        chars[i]["fishingToolkitEquipped"]["line"] = fishing_line_map.get(
            int(fields[f"PVFishingToolkit_{i}"][1]), "UNKNOWN"
        )

        charEquippedBubbles = json.loads(fields["CauldronBubbles"])[i]
        chars[i]["bubblesEquipped"] = [
            large_bubble_map.get(char_bubble, f"UNKNOWN-{char_bubble}")
            for char_bubble in charEquippedBubbles
        ]

        rawAnvil = fields[f"AnvilPA_{i}"]

        # [0-13] of rawAnvil are each anvil product
        # of each product...
        # 0 = amount to be produced (claimed)
        # 1 = amount of xp gained when claimed
        # 2 = current progress? (idk need more proof but also kinda useless)
        # 3 = ???
        anvilProducts = []
        for rawProductStats in rawAnvil:
            anvilProducts += [
                {
                    "produced": int(rawProductStats["0"]),
                    "xp": int(rawProductStats["1"]),
                    "progress": float(rawProductStats["2"]),
                    "3": int(rawProductStats["3"]),
                }
            ]

        chars[i]["anvil"]["production"] = anvilProducts
    return chars


def fill_account_data(account: dict, characters: list, fields: dict) -> dict:
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
        base = card_level_map.get(key)
        if count == 0:
            starlevel = "Not Found"
        elif count >= base * 9:
            starlevel = "3 Star"
        elif count >= base * 4:
            starlevel = "2 Star"
        elif count >= base:
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


def fillGuildData(fields: dict, guildInfo: dict):
    res = {}
    res["id"] = guildInfo["i"]
    res["name"] = guildInfo["n"]
    res["bonuses"] = guildInfo["stats"]

    return res


def parse_dough(dough: dict):
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
        numChars,
        fields,
        parser,
    )

    res["account"] = fill_account_data(
        cake_template["account"], res["characters"], fields
    )

    res["account"]["Guild"] = fillGuildData(fields, guildInfo)
    return res


def print_line(ids: list, values: list, prefix: str = "", separators: list = None):
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

    for line in lines:
        print(line)


def print_characters(chars: list):
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


def save_json(json_data: dict, filename: str = "new_json.json", indent:int=4):
    with open(filename, "w") as fp:
        json.dump(json_data, fp, indent = indent)


if __name__ == "__main__":
    filename = "raw_data.json"
    with open(filename, "r") as fp:
        saveData = json.load(fp)

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
    raw_dough = {
        "charNameData": charNameData,
        "guildInfo": guildInfo,
        "saveData": saveData,
    }

    cake = parse_dough(raw_dough)
    print_characters([cake["characters"][2]])
    print_account(cake["account"])

    save_json(cake)
