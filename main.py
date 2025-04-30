import os
from time import sleep

from compare.compare import compare_snapshots
from enums import LogLevel
from history.history import History
from data.snapshot import Snapshot


def main_loop(too_early=False):
    get_time = lambda f: os.stat(f).st_mtime
    log_level = LogLevel.DEBUG

    save_dir = "C:\\Users\\szpot\\AppData\\LocalLow\\Roboatino\\ShogunShowdown"
    # save_dir = "C:\\Users\\WZ\\AppData\\LocalLow\\Roboatino\\ShogunShowdown"
    save_file = "RunSaveData.dat"
    filename = save_dir + "\\" + save_file

    try:
        last_recorded_edited_time = get_time(filename)
    except FileNotFoundError:
        print("Run not yet started")
        sleep(1)
        return main_loop(True)

    if too_early:
        print("Run has started")

    with open(filename) as source_file:
        previous_snapshot = Snapshot.from_file(source_file.read())
        history = History(previous_snapshot)
        compare_snapshots(history, None, previous_snapshot, log_level)

    while True:
        try:
            current_last_edited_time = get_time(filename)
            if current_last_edited_time != last_recorded_edited_time:
                with open(filename, mode='r') as source_file:
                    last_recorded_edited_time = current_last_edited_time
                    source = source_file.read()
                    new_snapshot = Snapshot.from_file(source)
                    compare_snapshots(history, previous_snapshot, new_snapshot, log_level)

                    # WIP
                    # raw_data = json.loads(base64.b64decode(source))

                    previous_snapshot = new_snapshot
        except FileNotFoundError:
            print("Run finished")
            break


if __name__ == '__main__':
    main_loop()
