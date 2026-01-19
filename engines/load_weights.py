import json
import os

from engines.board import print_message

@staticmethod
def load_weights():
    # Init weights
    ai_weights = None
    weights_file = "best_ai_weights.json"

    if os.path.exists(weights_file):
        try:
            with open(weights_file, "r") as f:
                ai_weights = json.load(f)
            print_message(
                "The training weights have been successfully loaded ​is now at its maximum power.", "info")
        except Exception as e:
            print_message(
                f"File upload error; default weights will be used.: {e}", "warning")
    else:
        print_message(
            "The weights file does not exist, using default weights.", "warning")
    return ai_weights