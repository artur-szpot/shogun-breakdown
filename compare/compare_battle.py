from typing import Optional

from data.mappers import pickup_name_mapper
from data.prediction_error import PredictionError
from data.snapshot import Snapshot
from data.weapon import Weapon
from enums import LogLevel, WeaponTileEffectEnum
from history.history import History


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
            history.board_size = new_snapshot.room.hero.position.cell * 2 + 1
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


def test_simulation(simulation: Optional[Snapshot], new_snapshot: Snapshot, name: str = None,
                    debug: bool = False) -> bool:
    if simulation is None:
        if debug:
            print(f'Simulation "{name}": impossible')
        return False
    simulation.simulate_enemies()
    try:
        result = new_snapshot.is_good_prediction(simulation, debug)
        if debug:
            print(f'Simulation "{name}": {"correct!" if result else "wrong"}')
        return result
    except PredictionError as error:
        if debug:
            print(f'Simulation "{name}" error: {error}')
        return False


class Scenario:
    simulation: Snapshot
    description: str
    debug_name: str

    def __init__(self, simulation: Snapshot, description: str, debug_name: str):
        self.simulation = simulation
        self.description = description
        self.debug_name = debug_name


def battle_update(history: History, previous_snapshot: Snapshot, new_snapshot: Snapshot,
                  log_level: LogLevel) -> History:
    if previous_snapshot.game_stats.turns == new_snapshot.game_stats.turns:
        # TODO still unclear why this happens
        return history

    # WHAT TIME IS IT
    turns = new_snapshot.game_stats.turns
    time = new_snapshot.game_stats.time
    if log_level == LogLevel.DEBUG:
        print(f"TURN {turns}, TIME {pretty_print_time(time)}")
        pickups = [f'{loc}: {", ".join(pickup_name_mapper[pp] for pp in pps)}' for loc, pps in
                   new_snapshot.room.pickups.items()]
        print(f"PICKUPS: {', '.join(pickups)}")

    # LEFT TO COVER
    # execute special
    # execute queue
    # possibility of free turn around (and all other skills...)

    permutated_attack_queues = previous_snapshot.permutate_possible_attack_queues()
    current_attack_queue = previous_snapshot.room.hero.attack_queue[:]
    possible_attack_queues = [current_attack_queue]
    for perm in permutated_attack_queues:
        if not Weapon.is_list_equal(current_attack_queue, perm):
            possible_attack_queues.append(perm)

    possible_scenarios = [
        Scenario(
            previous_snapshot.simulation_move_right(possible_attack_queues=possible_attack_queues,
                                                    board_size=history.board_size),
            "Hero has moved right", "move right"),
        Scenario(previous_snapshot.simulation_move_left(possible_attack_queues=possible_attack_queues),
                 "Hero has moved left", "move left"),
        Scenario(previous_snapshot.simulation_turn_around(possible_attack_queues=possible_attack_queues),
                 "Hero has turned around", "turn around"),
        Scenario(previous_snapshot.simulation_wait(possible_attack_queues=possible_attack_queues),
                 "Hero has waited a turn", "wait"),
        Scenario(previous_snapshot.simulation_signature_move(possible_attack_queues=possible_attack_queues),
                 "Hero has executed their signature move", "sig. move"),
    ]

    for attack_queue in possible_attack_queues:
        if len(attack_queue):
            possible_scenarios.append(Scenario(
                previous_snapshot.simulation_execute_queue(attack_queue, history.board_size),
                "Hero has executed the queue", "execute"))

    for weapon in previous_snapshot.hero_deck:
        if weapon.tile_effect is not None and weapon.tile_effect == WeaponTileEffectEnum.IMMEDIATE:
            # Immediates are handled elsewhere.
            continue
        is_in_queue = 0
        number_copies = 0
        for potential in previous_snapshot.hero_deck:
            if potential.is_equal(weapon):
                number_copies += 1
        for potential in previous_snapshot.room.hero.attack_queue:
            if potential.is_equal(weapon):
                is_in_queue += 1
        print(f"weapon: {weapon.pretty_print()}")
        print(f"number_copies: {number_copies}")
        print(f"is_in_queue: {is_in_queue}")
        if is_in_queue < number_copies:
            possible_scenarios.append(Scenario(previous_snapshot.simulation_adding_weapon_to_queue(weapon),
                                               f"Hero has added {weapon.pretty_print()} to the queue",
                                               f"add {weapon.debug_print()}"))

    debug = True
    found_the_answer = False
    answer = None
    for scenario in possible_scenarios:
        result = test_simulation(scenario.simulation, new_snapshot, scenario.debug_name, debug)
        if result:
            if found_the_answer:
                if scenario.debug_name != "execute":
                    raise ValueError("More than one scenario found to be correct!")
            answer = scenario.description
            found_the_answer = True

    if answer is None:
        print("Correct scenario has not been found :(")
    else:
        print(answer)

    return history
