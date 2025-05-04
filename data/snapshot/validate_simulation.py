from typing import List, Optional

from data.other_enums import GamePhase
from data.snapshot.prediction_error import PredictionError
from data.snapshot.predictions import Predictions
from data.snapshot.simulation import Simulation
from data.snapshot.snapshot import Snapshot
from data.weapon.weapon import Weapon


def reduce_potential_attack_queues(actual_snapshot: Snapshot, attack_queue: List[Weapon], predictions: Predictions) -> \
        Optional[List[Weapon]]:
    if actual_snapshot.game_phase == GamePhase.BATTLE_REWARDS:
        return []
    if not len(predictions.potential_hero_attack_queues):
        return attack_queue
    for phaq in predictions.potential_hero_attack_queues:
        if Weapon.is_list_equal(actual_snapshot.room.hero.attack_queue, phaq):
            return phaq
    return None


def reduce_potential_decks(actual_snapshot: Snapshot, hero_deck: List[Weapon], predictions: Predictions) -> Optional[
    List[Weapon]]:
    if actual_snapshot.game_phase == GamePhase.BATTLE_REWARDS:
        return [weapon.clone() for weapon in actual_snapshot.hero_deck]
    if not len(predictions.potential_hero_decks):
        return hero_deck
    for phd in predictions.potential_hero_decks:
        if Weapon.is_list_equal(actual_snapshot.hero_deck, phd):
            return phd
    return None


def is_good_prediction(actual_snapshot: Snapshot, simulation: Simulation, debug: bool = True) -> bool:
    # Reduce potentials down to a single comparison.
    reduced_attack_queue = reduce_potential_attack_queues(
        actual_snapshot,
        simulation.room.hero.attack_queue,
        simulation.predictions
    )
    if reduced_attack_queue is None:
        if debug:
            raise PredictionError("None of the predicted attack queues check out")
        return False
    simulation.room.hero.attack_queue = reduced_attack_queue
    reduced_hero_deck = reduce_potential_decks(
        actual_snapshot,
        simulation.hero_deck,
        simulation.predictions
    )
    if reduced_hero_deck is None:
        if debug:
            pot_decks = ' OR '.join(Weapon.debug_print_list(phd) for phd in simulation.predictions.potential_hero_decks)
            raise PredictionError(f"None of the predicted hero decks check out {pot_decks}")
        return False
    simulation.hero_deck = reduced_hero_deck

    # Check potions.
    total_any_potions = sum(1 if x == -2 else 0 for x in simulation.hero_potion_ids)
    if len(actual_snapshot.hero_potion_ids) < len(simulation.hero_potion_ids) - total_any_potions \
            or len(actual_snapshot.hero_potion_ids) > len(simulation.hero_potion_ids):
        if debug:
            raise PredictionError(f"wrong number of potions is {len(actual_snapshot.hero_potion_ids)} "
                                  f"expected at least {len(simulation.hero_potion_ids) - total_any_potions} "
                                  f"and at most {len(simulation.hero_potion_ids)}")
        return False
    for potion_id in simulation.hero_potion_ids:
        if potion_id not in [-1, -2] and potion_id not in actual_snapshot.hero_potion_ids:
            if debug:
                raise PredictionError(f"predicted potion missing")
            return False

    # Check simple values.
    if not Weapon.is_list_equal(actual_snapshot.hero_deck, simulation.hero_deck):
        if debug:
            if len(actual_snapshot.hero_deck) != len(simulation.hero_deck):
                what = f"wrong len {len(actual_snapshot.hero_deck)} vs {len(simulation.hero_deck)}"
            for i in range(len(actual_snapshot.hero_deck)):
                if not actual_snapshot.hero_deck[i].is_equal(simulation.hero_deck[i]):
                    what = f"wrong weapon #{i}"
            raise PredictionError(f"wrong hero deck state: {what}")
        return False
    if actual_snapshot.game_phase != simulation.game_phase:
        if debug:
            raise PredictionError(f"wrong game phase")
        return False

    if not actual_snapshot.game_stats.is_good_prediction(simulation.game_stats, simulation.predictions.new_potions,
                                                         debug):
        actual_snapshot.game_stats.diff(simulation.game_stats, simulation.predictions.new_potions)
        raise PredictionError(f"game stats wrong debug={debug}")
    if not actual_snapshot.room.is_good_prediction(simulation.room, simulation.predictions.summons, debug=True):
        # actual_snapshot.room.diff(simulation.room, simulation.predictions.summons)
        raise PredictionError("room wrong")

    # Perform complex validations.
    game_stats = actual_snapshot.game_stats.is_good_prediction(
        simulation.game_stats,
        simulation.predictions.new_potions,
        debug
    )
    if not game_stats:
        raise PredictionError("game stats wrong")

    room = actual_snapshot.room.is_good_prediction(simulation.room, simulation.predictions.summons, debug=True)
    if not room:
        raise PredictionError("room wrong")

    return True
