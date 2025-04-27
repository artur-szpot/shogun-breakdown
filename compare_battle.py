from typing import Optional

from enums import LogLevel
from history import History
from snapshot import Snapshot
from weapon import Weapon


def pretty_print_time_part(part: int) -> str:
    return str(part).rjust(2, '0')


def pretty_print_time(time: int) -> str:
    hours = time // 3600
    minutes = (time - hours * 3600) // 60
    seconds = time - hours * 3600 - minutes * 60
    result = f"{pretty_print_time_part(minutes)}:{pretty_print_time_part(seconds)}"
    if not hours:
        return result
    return f"{pretty_print_time_part(hours)}:{result}"


def run_started(history: History, new_snapshot: Snapshot, log_level: LogLevel) -> History:
    if log_level == LogLevel.DEBUG:
        print("== RUN STARTED ==")
        print()
    return battle_started(history, new_snapshot, new_snapshot, log_level)


def battle_started(history: History, previous_snapshot: Optional[Snapshot], new_snapshot: Snapshot,
                   log_level: LogLevel) -> History:
    if log_level == LogLevel.DEBUG:
        print()
        if previous_snapshot is None:
            print("== IN A BATTLE ==")
        else:
            print("== BATTLE STARTED ==")
        print(f"== {new_snapshot.get_room()} ==")
        print()
    return history


def battle_finished(history: History, previous_snapshot: Snapshot, log_level: LogLevel) -> History:
    if log_level == LogLevel.DEBUG:
        print()
        print("== BATTLE WON ==")
        print(f"== {previous_snapshot.get_room()} ==")
        print(f"Turns taken: {'unknown'}")
        print(f"Time taken: {'unknown'}")
        print(f"Hits taken: {'unknown'}")
        print(f"Potions used: {'unknown'}")
        print(f"Combos: {'unknown'}")
        print()
    elif log_level == LogLevel.SPLITS:
        print(f"== {previous_snapshot.get_room()} ==")
        print(f"Turns taken: {'unknown'}")
        print(f"Time taken: {'unknown'}")
        print(f"Hits taken: {'unknown'}")
        print(f"Potions used: {'unknown'}")
        print(f"Combos: {'unknown'}")
        print()
    return history


def battle_update(history, previous_snapshot: Snapshot, new_snapshot: Snapshot, log_level: LogLevel) -> History:
    if previous_snapshot.game_stats.turns == new_snapshot.game_stats.turns:
        # Not sure yet what happens to write in the file twice - maybe update before and after enemy turn.
        return history

    # WHAT TIME IS IT
    turns = new_snapshot.game_stats.turns
    time = new_snapshot.game_stats.time
    if log_level == LogLevel.DEBUG:
        print(f"TURN {turns}, TIME {pretty_print_time(time)}")

    # WHAT HAVE I DONE
    hero_queue_changed = False
    hero_queue_emptied = False
    hero_attack_executed = False
    hero_moved = True
    hero_flipped = False
    hero_used_special = False

    # 1: interacted with attack queue
    previous_queue = previous_snapshot.hero.attack_queue
    current_queue = new_snapshot.hero.attack_queue
    if not Weapon.is_list_equal(previous_queue, current_queue):
        hero_queue_changed = True
        if Weapon.is_list_reordered(previous_queue, current_queue):
            if log_level == LogLevel.DEBUG:
                print(f"Reordered attack queue to {Weapon.pretty_print_list(current_queue)}")
        elif len(previous_queue) and not len(current_queue):
            hero_queue_emptied = True
            if log_level == LogLevel.DEBUG:
                print("Probably executed the queue")  # TODO
            # need additional check to make sure it was executed
            # but not deck, need to analyze combat room
        else:
            removed = []
            added = []

            for weapon in previous_queue:
                found = False
                for new_weapon in current_queue:
                    if weapon.is_equal(new_weapon):
                        found = True
                if not found:
                    removed.append(weapon)

            for index, new_weapon in enumerate(current_queue):
                found = False
                for weapon in previous_queue:
                    if weapon.is_equal(new_weapon):
                        found = True
                if not found:
                    added.append((new_weapon, index))

            for weapon in removed:
                removed_and_added = False
                for index, entry in enumerate(added):
                    added_weapon, new_index = entry
                    if weapon.is_equal(added_weapon):
                        removed_and_added = True
                        # this will never show up TODO cleanup
                        if log_level == LogLevel.DEBUG:
                            print(
                                f"ERROR: Removed {weapon.pretty_print()} from queue and added it back in position {new_index}")
                        added[index] = (added_weapon, -2)
                if not removed_and_added:
                    if log_level == LogLevel.DEBUG:
                        print(f"Removed {weapon.pretty_print()} from queue")
            for entry in added:
                weapon, index = entry
                if index != -2:
                    if log_level == LogLevel.DEBUG:
                        # Always print position because immediate can cause several to be added.
                        print(f"Added {weapon.pretty_print()} to the queue in position {index + 1}")

    # 2. executed queue

    # 3. moved
    hero_position_change = new_snapshot.hero.cell - previous_snapshot.hero.cell
    if hero_position_change == 1:
        if log_level == LogLevel.DEBUG:
            print("Moved right")
    elif hero_position_change == -1:
        if log_level == LogLevel.DEBUG:
            print("Moved left")
    elif hero_position_change > 0:
        if log_level == LogLevel.DEBUG:
            print(f"Moved {hero_position_change} spaces to the right")
    elif hero_position_change < 0:
        if log_level == LogLevel.DEBUG:
            print(f"Moved {-hero_position_change} spaces to the left")
    else:
        hero_moved = False

    # 4. turned around
    if new_snapshot.hero.facing != previous_snapshot.hero.facing:
        if log_level == LogLevel.DEBUG:
            print(f"Turned {'right' if new_snapshot.hero.facing == 1 else 'left'}")
        hero_flipped = True

    # 5. drank a potion
    # COMPLICATED!

    # 6. used special
    if new_snapshot.hero.special_move_cooldown == 0:
        if log_level == LogLevel.DEBUG:
            print("Used special move")
        hero_used_special = True

    # 7. waited
    if not hero_queue_changed \
            and not hero_attack_executed \
            and not hero_moved \
            and not hero_flipped \
            and not hero_used_special:
        if log_level == LogLevel.DEBUG:
            print("Waited a turn")

    # WHAT HAVE THEY DONE
    # enemies spawned, prepared actions, executed actions
    # hits taken

    return history
