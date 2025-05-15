import json
import os


def read_options():
    if not os.path.isfile("options.json"):
        return None
    with open("options.json", mode='r') as file:
        return json.loads(file.read())


def set_options():
    # TODO add input here
    options = {
        "save_dir": "C:\\Users\\szpot\\AppData\\LocalLow\\Roboatino\\ShogunShowdown",
        "bright_logs": False,
    }
    with open("options.json", mode='w') as file:
        file.write(json.dumps(options))
