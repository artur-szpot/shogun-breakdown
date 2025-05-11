from typing import Optional, List, Dict

from data.mappers import pickup_name_mapper
from data.other_enums import GamePhase
from data.room.room_enums import PickupEnum
from data.skill.skill_enums import SkillEnum
from data.snapshot.permutate_queues import permutate_possible_attack_queues
from data.snapshot.prediction_error import PredictionError
from data.snapshot.predictions import Predictions
from data.snapshot.simulation import Simulation
from data.snapshot.snapshot import Snapshot
from data.snapshot.validate_simulation import is_good_prediction
from data.weapon.weapon import Weapon
from history.history import History
from logger import logger


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


def run_started(new_snapshot: Snapshot) -> History:
    logger.splits_info(" ".join([
        "ROOM".ljust(30),
        "TURNS".ljust(5),
        "TIME".rjust(8),
    ]))

    logger.detail_info("== RUN STARTED ==")
    logger.detail_info("")
    return battle_started(new_snapshot, new_snapshot)


def battle_started(previous_snapshot: Optional[Snapshot], new_snapshot: Snapshot) -> History:
    logger.detail_info("")

    if previous_snapshot is None:
        logger.detail_info("== IN A BATTLE ==")
        history = new_snapshot.history
    else:
        logger.detail_info("== BATTLE STARTED ==")
        history = previous_snapshot.history
    logger.detail_info(f"== {new_snapshot.get_room()} ==")
    logger.detail_info("")
    return history


def battle_finished(previous_snapshot: Snapshot) -> History:
    history = previous_snapshot.history

    logger.splits_text(" ".join([
        previous_snapshot.get_room(True).ljust(30),
        str(previous_snapshot.game_stats.turns).rjust(5),
        pretty_print_time(previous_snapshot.game_stats.time).rjust(8),
    ]))

    logger.detail_success("")
    logger.detail_success("== BATTLE WON ==")
    logger.detail_success(f"Turns taken: {'unknown'}")
    logger.detail_success(f"Time taken: {'unknown'}")
    logger.detail_success(f"Hits taken: {'unknown'}")
    logger.detail_success(f"Potions used: {'unknown'}")
    logger.detail_success(f"Combos: {'unknown'}")
    logger.detail_success("")
    return history


class SimulationResults:
    all_answers: List[str]
    non_execute_answers: int
    victory: bool
    new_history: Optional[History]
    guesses: List[Dict[int, PickupEnum]]

    def __init__(self,
                 all_answers: List[str] = None,
                 non_execute_answers: int = 0,
                 victory: bool = False,
                 new_history: Optional[History] = None,
                 guesses: List[Dict[int, PickupEnum]] = None,
                 ):
        self.all_answers = all_answers or []
        self.non_execute_answers = non_execute_answers
        self.victory = victory
        self.new_history = new_history
        self.guesses = guesses or []

    def add(self, others: List):
        for other in others:
            if other is None:
                return
            if len(other.all_answers):
                self.all_answers.extend(other.all_answers)
            if len(other.guesses):
                self.guesses.extend(other.guesses)
            self.non_execute_answers += other.non_execute_answers
            if other.victory:
                self.victory = True
            if self.new_history is None and other.new_history is not None:
                self.new_history = other.new_history


def test_simulation(simulation: Optional[Simulation], new_snapshot: Snapshot,
                    previous_hero_cell: int, name: str, description: str,
                    potions_description: Optional[str]) -> List[SimulationResults]:
    if simulation is None:
        logger.queue_debug_error(f'Simulation "{name}": impossible')
        logger.queue_debug_error(f"{potions_description}")
        logger.queue_debug_error("")
        return []

    # TODO cleanup if enemy order really always is LTR
    if potions_description is not None:
        full_description = potions_description + '; ' + description
    else:
        full_description = description
    enemy_attack_order = simulation.simulate_enemies(
        previous_hero_cell=previous_hero_cell,
    )
    results = []
    for order_name, simulated_order in enemy_attack_order.items():
        simulated_order_name = "" if len(enemy_attack_order) == 1 else f" (order_name)"
        # If everybody has died (this can mean cleared wave -- new spawns don't attack)
        if simulation.predictions.enemies_cleared:
            # Has the battle has finished?
            if new_snapshot.game_phase != GamePhase.BATTLE:
                results.append(SimulationResults(
                    all_answers=[full_description],
                    victory=True,
                    new_history=simulation.history,
                    guesses=[simulation.predictions.potion_simulation.guesses],
                ))
                continue
        try:
            result = is_good_prediction(new_snapshot, simulated_order)
            if result:
                logger.queue_debug_success(f'Simulation "{name}"{simulated_order_name}: correct!')
            else:
                logger.queue_debug_warn(f'Simulation "{name}"{simulated_order_name}: wrong')
            logger.queue_debug_success("")
            results.append(SimulationResults(
                all_answers=[full_description] if result else None,
                non_execute_answers=0 if name.startswith("execute") or not result else 1,
                new_history=simulated_order.history if result else None,
                guesses=[simulation.predictions.potion_simulation.guesses] if result else None,
            ))
            continue
        except PredictionError as error:
            logger.queue_debug_error(f'Simulation "{name}{simulated_order_name}" error: {error}')
            logger.queue_debug_error("")

    return results


def battle_update(previous_snapshot: Snapshot, new_snapshot: Snapshot) -> History:
    if previous_snapshot.game_stats.turns == new_snapshot.game_stats.turns:
        # TODO still unclear why this happens
        return previous_snapshot.history

    # WHAT TIME IS IT
    turns = new_snapshot.game_stats.turns
    time = new_snapshot.game_stats.time
    logger.detail_text("")
    logger.detail_text(f"TURN {turns}, TIME {pretty_print_time(time)}")
    logger.debug_text(new_snapshot.game_stats.debug_print())
    for potion_id in previous_snapshot.history.potions.current_guess_matrix:
        print(
            f"{potion_id} ({'/'.join(pickup_name_mapper[t] for t in previous_snapshot.history.potions.current_guess_matrix[potion_id])})")

    # logger.debug_text(f"POTIONS: {previous_snapshot.hero_potion_ids}")
    # for pos, pot in previous_snapshot.history.potions.potions.items():
    #     logger.debug_text(f"{pos}: {pot.pretty_print()}")
    # logger.debug_text(f"PICKUPS:")
    # for loc, pps in new_snapshot.room.pickups.items():
    #     for pp, total in pps.items():
    #         logger.debug_text(f"{loc}. {pickup_name_mapper[pp]} ({total})")
    # logger.debug_text(f"PREV ENEMIES:")
    # for index, enemy in enumerate(previous_snapshot.room.enemies):
    #     logger.debug_text(f"{index}. {enemy.pretty_print()}")
    # logger.debug_text(f"ENEMIES:")
    # for index, enemy in enumerate(new_snapshot.room.enemies):
    #     logger.debug_text(f"{index}. {enemy.pretty_print()}")
    # logger.debug_text(f"BOARD SIZE: {new_snapshot.room.board_size}")
    # logger.detail_text("")

    # Account for switching the queue order.
    permutated_attack_queues = permutate_possible_attack_queues(
        attack_queue=previous_snapshot.room.hero.attack_queue,
        hero_deck=previous_snapshot.hero_deck
    )
    current_attack_queue = previous_snapshot.room.hero.attack_queue[:]
    possible_attack_queues = [current_attack_queue]
    for perm in permutated_attack_queues:
        if not Weapon.is_list_equal(current_attack_queue, perm):
            possible_attack_queues.append(perm)
    predictions = Predictions(potential_hero_attack_queues=possible_attack_queues)

    # Learn as much as possible about potions. 
    potion_simulations = previous_snapshot.history.potions.potion_update(
        previous_snapshot=previous_snapshot.potion_snapshot(),
        new_snapshot=new_snapshot.potion_snapshot(),
        selling_allowed=previous_snapshot.skills.has_skill(SkillEnum.ROGUE_RETAIL)
    )

    # Begin simulations.
    results = SimulationResults()
    for potion_simulation in potion_simulations:
        # Simulate potions.
        initial_simulation = Simulation.of(previous_snapshot)
        initial_simulation.apply_potion_simulation(potion_simulation)
        initial_simulation.hero_potion_ids = new_snapshot.hero_potion_ids[:]
        initial_predictions = predictions.clone()
        initial_predictions.potion_simulation = potion_simulation

        # Simulate possible hero actions.
        new_results = simulate_hero_actions(initial_simulation, new_snapshot, predictions)
        results.add([new_results])

    if not results.victory and results.non_execute_answers > 1:
        logger.execute_queue()
        logger.debug_error("More than one scenario found to be correct!")
        for answer in results.all_answers:
            logger.detail_text(answer)
    elif not len(results.all_answers):
        logger.execute_queue()
        logger.debug_error("Correct scenario has not been found :(")
    else:
        logger.clear_queue()
        if results.victory:
            if len(results.all_answers) > 1:
                logger.debug_success(f"Battle won! Possible paths to victory: {len(results.all_answers)}")
            else:
                logger.debug_success(f"Battle won! Last move: {results.all_answers[0]}")
        else:
            logger.detail_text(results.all_answers[0])

    logger.debug_info(f"Potion simulations: {len(potion_simulations)}")
    if results.new_history is not None:
        results.new_history.potions.confirmed_guesses(results.guesses)
    return results.new_history or previous_snapshot.history


def simulate_hero_actions(initial_simulation: Simulation, new_snapshot: Snapshot,
                          predictions: Predictions) -> SimulationResults:
    results = SimulationResults()
    turn_around_is_free = new_snapshot.skills.has_skill(SkillEnum.TWO_FACED_DANGER)
    previous_hero_cell = initial_simulation.room.hero.position.cell
    potions_description = predictions.potion_simulation.potion_description

    name = "move right"
    description = "Hero has moved right"
    logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
    simulation = Simulation.simulation_move_right(initial_simulation, predictions)
    results.add(test_simulation(
        simulation=simulation,
        new_snapshot=new_snapshot,
        previous_hero_cell=previous_hero_cell,
        name=name,
        description=description,
        potions_description=potions_description,
    ))

    if turn_around_is_free:
        name = "turn and move right"
        description = "Hero has turned moved right"
        logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
        simulation = Simulation.simulation_move_right(initial_simulation, predictions)
        if simulation is not None:
            simulation.room.hero.position.flip()
            simulation.game_stats.turn_arounds += 1
        results.add(test_simulation(
            simulation=simulation,
            new_snapshot=new_snapshot,
            previous_hero_cell=previous_hero_cell,
            name=name,
            description=description,
            potions_description=potions_description,
        ))

    name = "move left"
    description = "Hero has moved left"
    logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
    simulation = Simulation.simulation_move_left(initial_simulation, predictions)
    results.add(test_simulation(
        simulation=simulation,
        new_snapshot=new_snapshot,
        previous_hero_cell=previous_hero_cell,
        name=name,
        description=description,
        potions_description=potions_description,
    ))

    if turn_around_is_free:
        name = "turn and move left"
        description = "Hero has turned moved left"
        logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
        simulation = Simulation.simulation_move_left(initial_simulation, predictions)
        if simulation is not None:
            simulation.room.hero.position.flip()
            simulation.game_stats.turn_arounds += 1
        results.add(test_simulation(
            simulation=simulation,
            new_snapshot=new_snapshot,
            previous_hero_cell=previous_hero_cell,
            name=name,
            description=description,
            potions_description=potions_description,
        ))

    if turn_around_is_free:
        name = "turn around twice"
        description = "Hero has turned around twice (or more)"
        logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
        simulation = Simulation.simulation_idle(initial_simulation, predictions)
        simulation.room.hero.state.curse = True
        simulation.predictions.allow_more_turn_arounds = True
        results.add(test_simulation(
            simulation=simulation,
            new_snapshot=new_snapshot,
            previous_hero_cell=previous_hero_cell,
            name=name,
            description=description,
            potions_description=potions_description,
        ))

        name = "turn around thrice"
        description = "Hero has turned around thrice (or more)"
        logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
        simulation = Simulation.simulation_idle(initial_simulation, predictions)
        simulation.room.hero.state.curse = True
        simulation.room.hero.position.flip()
        simulation.predictions.allow_more_turn_arounds = True
        results.add(test_simulation(
            simulation=simulation,
            new_snapshot=new_snapshot,
            previous_hero_cell=previous_hero_cell,
            name=name,
            description=description,
            potions_description=potions_description,
        ))
    else:
        name = "turn around"
        description = "Hero has turned around"
        logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
        simulation = Simulation.simulation_turn_around(initial_simulation, predictions)
        results.add(test_simulation(
            simulation=simulation,
            new_snapshot=new_snapshot,
            previous_hero_cell=previous_hero_cell,
            name=name,
            description=description,
            potions_description=potions_description,
        ))

    name = "wait"
    description = "Hero has waited a turn"
    logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
    simulation = Simulation.simulation_wait(initial_simulation, predictions)
    results.add(test_simulation(
        simulation=simulation,
        new_snapshot=new_snapshot,
        previous_hero_cell=previous_hero_cell,
        name=name,
        description=description,
        potions_description=potions_description,
    ))

    if turn_around_is_free:
        name = "turn and wait"
        description = "Hero has turned and waited a turn"
        logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
        simulation = Simulation.simulation_wait(initial_simulation, predictions)
        simulation.room.hero.position.flip()
        simulation.game_stats.turn_arounds += 1
        results.add(test_simulation(
            simulation=simulation,
            new_snapshot=new_snapshot,
            previous_hero_cell=previous_hero_cell,
            name=name,
            description=description,
            potions_description=potions_description,
        ))

    name = "sig. move"
    description = "Hero has executed their signature move"
    logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
    simulation = Simulation.simulation_signature_move(initial_simulation, predictions)
    results.add(test_simulation(
        simulation=simulation,
        new_snapshot=new_snapshot,
        previous_hero_cell=previous_hero_cell,
        name=name,
        description=description,
        potions_description=potions_description,
    ))

    if turn_around_is_free:
        name = "turn + sig. move"
        description = "Hero has turned and executed their signature move"
        logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
        simulation = Simulation.simulation_turn_and_signature_move(initial_simulation, predictions)
        results.add(test_simulation(
            simulation=simulation,
            new_snapshot=new_snapshot,
            previous_hero_cell=previous_hero_cell,
            name=name,
            description=description,
            potions_description=potions_description,
        ))

    for weapon in initial_simulation.hero_deck:
        # Immediates are handled elsewhere.
        if weapon.is_immediate():
            continue
        is_in_queue = 0
        number_copies = 0
        for potential in initial_simulation.hero_deck:
            if weapon.cooldown_charge == weapon.cooldown and potential.is_equal(weapon):
                number_copies += 1
        for potential in initial_simulation.room.hero.attack_queue:
            if potential.is_equal(weapon):
                is_in_queue += 1
        if is_in_queue < number_copies:
            name = f"add {weapon.debug_print()}"
            description = f"Hero has added {weapon.pretty_print()} to the queue"
            logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
            simulation = Simulation.simulation_adding_weapon_to_queue(initial_simulation, weapon.clone())
            results.add(test_simulation(
                simulation=simulation,
                new_snapshot=new_snapshot,
                previous_hero_cell=previous_hero_cell,
                name=name,
                description=description,
                potions_description=potions_description,
            ))

            if turn_around_is_free:
                name = f"turn + add {weapon.debug_print()}"
                description = f"Hero has turned and added {weapon.pretty_print()} to the queue"
                logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
                simulation = Simulation.simulation_adding_weapon_to_queue(initial_simulation, weapon.clone())
                simulation.room.hero.position.flip()
                simulation.game_stats.turn_arounds += 1
                results.add(test_simulation(
                    simulation=simulation,
                    new_snapshot=new_snapshot,
                    previous_hero_cell=previous_hero_cell,
                    name=name,
                    description=description,
                    potions_description=potions_description,
                ))

    for attack_queue in [predictions.potential_hero_attack_queues[0]]:
        # possible_attack_queues: TODO uncomment, for now one only
        if len(attack_queue):
            name = f"execute {Weapon.short_print_list(attack_queue)}"
            description = f"Hero has executed the queue: {Weapon.short_print_list(attack_queue)}"
            logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
            simulation = Simulation.simulation_execute_queue(
                snapshot=initial_simulation,
                attack_queue=attack_queue,
                previous_hero_cell=previous_hero_cell,
            )
            results.add(test_simulation(
                simulation=simulation,
                new_snapshot=new_snapshot,
                previous_hero_cell=previous_hero_cell,
                name=name,
                description=description,
                potions_description=potions_description,
            ))

            if turn_around_is_free:
                name = f"turn + execute {Weapon.short_print_list(attack_queue)}"
                description = f"Hero has turned and executed the queue: {Weapon.short_print_list(attack_queue)}"
                logger.queue_debug_info(f'Start simulation {potions_description}:"{name}"')
                simulation = Simulation.simulation_turn_and_execute_queue(
                    snapshot=initial_simulation,
                    attack_queue=attack_queue,
                    previous_hero_cell=previous_hero_cell,
                )
                results.add(test_simulation(
                    simulation=simulation,
                    new_snapshot=new_snapshot,
                    previous_hero_cell=previous_hero_cell,
                    name=name,
                    description=description,
                    potions_description=potions_description,
                ))

    return results


def battle_ended(previous_snapshot: Snapshot, new_snapshot: Snapshot) -> History:
    # TODO!
    return battle_update(previous_snapshot, new_snapshot)
