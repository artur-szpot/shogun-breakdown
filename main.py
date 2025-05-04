import os
from time import sleep

from compare.compare import compare_snapshots
from history.history import History
from data.snapshot.snapshot import Snapshot
from logger import logger, MessageType


def get_time(file):
    return os.stat(file).st_mtime

def main_loop(too_early=False):
    # save_dir = "C:\\Users\\szpot\\AppData\\LocalLow\\Roboatino\\ShogunShowdown"
    save_dir = "C:\\Users\\WZ\\AppData\\LocalLow\\Roboatino\\ShogunShowdown"
    save_file = "RunSaveData.dat"
    filename = save_dir + "\\" + save_file

    try:
        last_recorded_edited_time = get_time(filename)
    except FileNotFoundError:
        logger.debug_info("Run not yet started")
        sleep(1)
        return main_loop(True)

    if too_early:
        logger.debug_success("Run has started")

    previous_snapshot = Snapshot.from_file(filename)
    history = History(previous_snapshot)
    compare_snapshots(history, None, previous_snapshot)

    while True:
        try:
            current_last_edited_time = get_time(filename)
            if current_last_edited_time != last_recorded_edited_time:
                last_recorded_edited_time = current_last_edited_time
                new_snapshot = Snapshot.from_file(filename)
                compare_snapshots(history, previous_snapshot, new_snapshot)
                previous_snapshot = new_snapshot
        except FileNotFoundError:
            logger.line()
            logger.nice_print([MessageType.INFO], "Run finished")
            break


if __name__ == '__main__':
    logger.nice_print([MessageType.INFO], 'Welcome to Shugun Breakdown v0.2')
    main_loop()
