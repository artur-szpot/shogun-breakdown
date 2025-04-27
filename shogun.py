# import json
# import jsondiff
# import base64
# import os
# import time
#
#
# def process_skills(value):
#     skills = value.get("skills", [])
#     levels = value.get("skillsLevel", [])
#     retval = {}
#     for i in range(len(skills)):
#         retval[skills[i]] = levels[i]
#     return retval
#
#
# def print_weapon(value):
#     # print(value)
#     weapon_name = value["attackEnum"]
#     name = {
#         2: "Spear",
#     }.get(weapon_name, f"Unkown weapon {weapon_name}")
#     weapon_prefix = value["attackEffect"]
#     prefix = ""
#     prefix = {
#         666: "dunno"
#     }.get(weapon_prefix, prefix)
#     weapon_prefix = value["tileEffect"]
#     prefix = {
#         666: "dunno"
#     }.get(weapon_prefix, prefix)
#     cooldown = value["cooldown"]
#     cooldown_charge = value["cooldownCharge"]
#     strength = value["value"]
#     baseStrength = value["baseValue"]
#     level = value["level"]
#     max_level = value["maxLevel"]
#     return prefix + (" " if prefix else "") + name + f" ({strength}, {cooldown})"
#
#
# def print_attack_queue(value):
#     return [print_weapon(x) for x in value]
#

def process(json_decoded, prev_data, stats):
    if json_decoded["runStats"]["turns"] == stats["turns"]:
        return prev_data, stats

    # print(f"inBattle: {stats['inBattle']}")
    change = jsondiff.diff(prev_data, json_decoded)
    # print(json.dumps(change, indent=2))
    # print(json.dumps(json_decoded, indent=2))
    waited_turn = False
    
    for key, value in change.items():
        if key == "runStats":
            for statkey, statvalue in value.items():
                if statkey == "coins":
                    coin_change = statvalue - stats["coins"]
                    if coin_change > 0:
                        print(f"coins earned: {coin_change}")
                    else:
                        print(f"coins spent: {-coin_change}")
                    stats["coins"] = statvalue
                elif statkey == "time":
                    continue # pass for now
                elif statkey == "combos":
                    continue # pass for now
                elif statkey == "numberOfCombatRoomsCleared":
                    continue # pass for now (???)
                elif statkey == "nScrollsPickupDrops":
                    continue # pass for now (???)
                elif statkey == "nPotionsPickupDrops":
                    continue # pass for now (???)
                elif statkey == "nHealPickupDrops":
                    print(f"what is nHealPickupDrops?")
                    continue # pass for now (???)
                elif statkey == "nTurnArounds":
                    continue # pass for now (???)
                elif statkey == "friendlyKills":
                    continue # pass for now (???)
                elif statkey == "hits":
                    print(f"ERROR: Received hit #{statvalue}")
                elif statkey == "turns":
                    print(f"TURN {statvalue}")
                    stats["turns"] = statvalue
                    waited_turn = True
                else:
                    print(f"Not sure what to do with key runStats.{statkey}")
        elif key == "potions":
            print("Recived or used potion") # todo
        elif key == "skills":
            curr_skills = process_skills(change)
            prev_skills = process_skills(stats)
            for skill in prev_skills:
                if skill not in curr_skills:
                    print(f"lost skill: {skill}")
                elif prev_skills[skill] != curr_skills[skill]:
                    print(f"new skill level: {skill} is now level {curr_skills[skill]}")
            for skill in curr_skills:
                if skill not in prev_skills:
                    print(f"new skill: {skill}")
            stats["skills"] = value
            stats["levels"] = change["skillsLevel"]
        elif key == "skillsLevel":
            continue # handled above
        elif key == "shopRoom":
            continue # skip for now, not very interesting
        elif key == "mapSelectionInProgress":
            print("Moving on the map" if value else "Entered a new level")
        elif key == "progressionSaveData":
            stats["inBattle"] = value == 0
            continue # moving between parts of a room
        elif key == "pickups":
            continue # potions picked up from the ground...
        elif key == "pickupsCellIndex":
            continue # ...and where they landed
        elif key == "rewardRoom":
            print(f"entered reward room") # print more details?
            stats["inBattle"] = False
        elif key == "mapSaveData":
            print(f"New location: {value['currentMapLocationID']}")
        elif key == "combatRoom":
            continue # print("fight update")
        elif key == "deck":
            if stats["inBattle"]:
                continue
            curr_deck = print_attack_queue(stats["deck"])
            new_deck = print_attack_queue(value)
            if len(curr_deck) > len(new_deck):
                for weapon in curr_deck:
                    if weapon not in new_deck:
                        print(f"Removed {weapon} from the deck")
            elif len(curr_deck) < len(new_deck):
                for weapon in new_deck:
                    if weapon not in curr_deck:
                        print(f"Added {weapon} to the deck")
        elif key == "hero":
            continue # handled in the other loop
        else:
            print(f"not sure what to do with key '{key}'")
            print(value)
            
        
    for herokey, herovalue in json_decoded.get("hero", {}).items():
        if herokey in ["name", "heroEnum"]:
            continue # these do not change mid-run
        elif herokey == "agentStats":
            for statkey, statvalue in herovalue.items():
                if statkey == "ice":
                    if stats["hero"]["ice"] != statvalue:
                        if not stats["hero"]["ice"]:
                            print(f"Got iced for {statvalue} turns")
                        else:
                            print(f"Ice cooldown down to {statvalue} turns")
                        stats["hero"]["ice"] = statvalue
                elif statkey == "poison":
                    if stats["hero"]["poison"] != statvalue:
                        if not stats["hero"]["poison"]:
                            print(f"Got poisoned for {statvalue} turns")
                        else:
                            print(f"Poison cooldown down to {statvalue} turns")
                        stats["hero"]["poison"] = statvalue
                elif statkey == "shield":
                    if stats["hero"]["shield"] != statvalue:
                        if not stats["hero"]["shield"]:
                            print(f"Got shielded")
                        else:
                            print(f"Lost shield")
                        stats["hero"]["shield"] = statvalue
                elif statkey == "curse":
                    if stats["hero"]["curse"] != statvalue:
                        if not stats["hero"]["curse"]:
                            print(f"Got cursed")
                        else:
                            print(f"Lost curse")
                        stats["hero"]["curse"] = statvalue
                elif statkey == "hp":
                    if stats["hero"]["hp"] != statvalue:
                        hp_change = statvalue - stats["hero"]["hp"]
                        if hp_change > 0:
                            print(f"Healed for {hp_change} HP")
                        else:
                            print(f"Lost {-hp_change} HP")
                        stats["hero"]["hp"] = statvalue
                elif statkey == "maxHP":
                    if stats["hero"]["maxHP"] != statvalue:
                        hp_change = statvalue - stats["hero"]["maxHP"]
                        if hp_change > 0:
                            print(f"Got {hp_change} max HP")
                        else:
                            print(f"Lost {-hp_change} max HP")
                        stats["hero"]["maxHP"] = statvalue
                else:
                    print(f"Not sure what to do with hero agent stat {statkey}")
        elif herokey == "specialMoveCooldownCharge":
            if herovalue == 0:
                print("Used special move")
                waited_turn = False
        elif herokey == "FacingDir":
            if herovalue != stats["hero"]["facing"]:
                print("changed facing")
                stats["hero"]["facing"] = herovalue
                waited_turn = False
        elif herokey == "deck":
            print(f"aaaaaaaaa deck: {herovalue}")
            continue
        elif herokey == "attackQueue":
            if not len(herovalue) and len(stats["attackQueue"]):
                print("Executed attack queue")
                stats["attackQueue"] = []
                waited_turn = False
                continue
            prev_queue = print_attack_queue(stats["attackQueue"])
            curr_queue = print_attack_queue(json_decoded["hero"]["attackQueue"])
            queues_equal = len(prev_queue) == len(curr_queue)
            if queues_equal:
                for i in range(len(prev_queue)):
                    if prev_queue[i] != curr_queue[i]:
                        queues_equal = False
            if queues_equal:
                continue
            elif not len(prev_queue):
                print(f"Added {curr_queue[0]} to queue")
                waited_turn = False
            else:
                waited_turn = False
                change_detected = False
                for weapon in prev_queue:
                    if weapon not in curr_queue:
                        change_detected = True
                        print(f"Removed {weapon} from queue")
                for i in range(len(curr_queue)):
                    weapon = curr_queue[i]
                    if weapon not in prev_queue:
                        change_detected = True
                        print(f"Added {weapon} to queue in position {i+1}")
                if not change_detected:
                    print(f"ERROR: Changed queue order to: {curr_queue}")
            stats["attackQueue"] = json_decoded["hero"]["attackQueue"]
        elif herokey == "iCell":
            if herovalue != stats["hero"]["cell"]:
                print(f"Moved to cell {herovalue}")
                stats["hero"]["cell"] = herovalue
                waited_turn = False
        else:
            print(f"not sure what to do with key hero.'{herokey}'")
            print(herovalue)
            
    if waited_turn:
        print("Waited for a turn")
        
    return json_decoded, stats


# def main_loop():
#     get_time = lambda f: os.stat(f).st_mtime
#
#     saveDir = "C:\\Users\\WZ\\AppData\\LocalLow\\Roboatino\\ShogunShowdown"
#     saveFile = "RunSaveData.dat"
#
#     try:
#         fn = saveDir + "\\" + saveFile
#         prev_time = get_time(fn)
#     except FileNotFoundError:
#         print("Run not started")
#         time.sleep(1)
#         main_loop()
#
#     with open(fn) as sourceFile:
#         prev_data = json.loads(base64.b64decode(sourceFile.read()))
#         stats = {
#             "coins": prev_data["runStats"]["coins"],
#             "turnArounds": prev_data["runStats"]["nTurnArounds"],
#             "turns": prev_data["runStats"]["turns"],
#             "actions": [],
#             "skills": prev_data["skills"],
#             "levels": prev_data["skillsLevel"],
#             "deck": prev_data["deck"],
#             "attackQueue": prev_data.get("hero", {}).get("attackQueue", []),
#             "inBattle": True,
#             "hero": {
#                 "cell": prev_data.get("hero", {}).get("iCell", 0),
#                 "facing": prev_data.get("hero", {}).get("FacingDir", 0),
#                 "maxHP": prev_data.get("hero", {}).get("agentStats", {}).get("maxHP", 0),
#                 "hp": prev_data.get("hero", {}).get("agentStats", {}).get("hp", 0),
#                 "shield": prev_data.get("hero", {}).get("agentStats", {}).get("shield", False),
#                 "curse": prev_data.get("hero", {}).get("agentStats", {}).get("curse", False),
#                 "ice": prev_data.get("hero", {}).get("agentStats", {}).get("ice", 0),
#                 "poison": prev_data.get("hero", {}).get("agentStats", {}).get("poison", 0),
#             }
#         }
#
#     while True:
#         try:
#             t = get_time(fn)
#             if t != prev_time:
#                 with open(fn, mode='r') as sourceFile:
#                     prev_time = t
#                     json_decoded = json.loads(base64.b64decode(sourceFile.read()))
#                     prev_data, stats = process(json_decoded, prev_data, stats)
#         except FileNotFoundError:
#             print("Run finished")
#             break
#
#
# if __name__ == '__main__':
#     main_loop()
