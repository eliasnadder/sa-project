from players.ai import AI as SlowAI
from players.ai_pruning import AI as FastAI

GAME_MODES = {
    "HUMAN": {
        "ai": None
    },

    "EASY": {
        "ai_class": FastAI,
        "depth": 2
    },

    "MEDIUM": {
        "ai_class": FastAI,
        "depth": 3
    },

    "HARD": {
        "ai_class": SlowAI,
        "depth": 4
    },
}
