import base64
import json
import os
from json import JSONDecodeError
from time import sleep

from compare.compare import compare_snapshots
from data.snapshot.snapshot import Snapshot
from logger import logger, MessageType
from options import set_options, read_options
from test_data import test_remade_data


def get_time(file):
    return os.stat(file).st_mtime


def main_loop(too_early=False):
    options = read_options()
    save_file = "RunSaveData.dat"
    filename = options['save_dir'] + "\\" + save_file
    logger.bright_logs = options['bright_logs']

    try:
        last_recorded_edited_time = get_time(filename)
    except FileNotFoundError:
        logger.debug_info("Run not yet started")
        sleep(1)
        return main_loop(True)

    if too_early:
        logger.debug_success("Run has started")

    previous_snapshot = Snapshot.from_file(filename, True)
    # TODO another dev checkup to see if cheat production works well
    try:
        with open(filename, mode='r') as source_file:
            source = source_file.read()
        raw_data = json.loads(base64.b64decode(source))
        remade_snapshot = previous_snapshot.to_dict()
        test_remade_data(raw_data, remade_snapshot)
    except JSONDecodeError:
        pass  # don't much care

    compare_snapshots(None, previous_snapshot)

    while True:
        try:
            current_last_edited_time = get_time(filename)
            if current_last_edited_time != last_recorded_edited_time:
                last_recorded_edited_time = current_last_edited_time
                new_snapshot = Snapshot.from_file(filename)
                history = compare_snapshots(previous_snapshot, new_snapshot)
                previous_snapshot = new_snapshot
                previous_snapshot.history = history
        except FileNotFoundError:
            logger.line()
            logger.nice_print([MessageType.INFO], "Run finished")
            break


if __name__ == '__main__':
    logger.nice_print([MessageType.INFO], 'Welcome to Shugun Breakdown v0.2')
    set_options()

    # TODO remove; temporarily doubled; allows mid-run start
    logger.splits_info(" ".join([
        "ROOM".ljust(30),
        "TURNS".ljust(5),
        "TIME".rjust(8),
    ]))

    main_loop()
