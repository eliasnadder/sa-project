# Senet Game

A comprehensive Python implementation of the ancient Egyptian board game Senet, featuring advanced AI opponents, genetic algorithm training, and both terminal and GUI interfaces.

## 📜 About Senet

Senet is one of the oldest known board games, dating back to ancient Egypt around 3100 BCE. The game involves moving pieces across a 30-square board, navigating special houses with unique rules, and being the first player to successfully bear off all pieces.

## ✨ Features

- **Multiple Play Modes**
  - Human vs Human
  - Human vs AI (Expectiminimax with Alpha-Beta pruning)
  - Human vs AI (Q-Learning reinforcement learning)
- **Dual Interfaces**
  - Terminal-based gameplay with colored ASCII graphics
  - Pygame GUI with visual board representation
- **Advanced AI Implementations**
  - Expectiminimax algorithm with Star1 pruning for chance nodes
  - Alpha-Beta pruning for efficient tree search
  - Transposition table for state caching
  - Move ordering and iterative deepening
  - Q-Learning reinforcement learning agent
- **AI Training System**
  - Genetic algorithm for weight optimization
  - Configurable population size and generations
  - Checkpoint system for resuming training
  - Performance visualization and statistics
  - CSV export of training data

## 🎮 Game Rules

- **Board**: 30 squares arranged in a 3x10 boustrophedon (S-shape) pattern
- **Pieces**: Each player starts with 7 pieces on alternating squares (1-14)
- **Movement**: Throw 4 casting sticks to determine moves (1-5 squares)
- **Special Houses**:
  - **House of Rebirth (15)**: Where pieces return when sent back
  - **House of Happiness (26)**: Must be landed on exactly when passing
  - **House of Water (27)**: Pieces landing here return to Rebirth
  - **Exit Houses (28-30)**: Require specific rolls to exit

## 📁 Project Structure

```text
├── engines/
│   ├── board.py                    # Board display and ANSI colors
│   ├── game.py                     # Main game loop (terminal)
│   ├── game_ql.py                  # Game loop for Q-Learning
│   ├── game_state_pyrsistent.py    # Immutable game state using pyrsistent
│   ├── rules.py                    # Game rules and move validation
│   ├── rules_silent.py             # Silent rules for AI training
│   └── sticks.py                   # Dice throwing mechanics
│
├── players/
│   ├── player.py                   # Player class definitions
│   ├── ai.py                       # Basic Expectiminimax AI
│   ├── ai_pruning.py              # Optimized AI with Star1 pruning
│   └── player_rl.py               # Q-Learning AI agent
│
├── evaluations/
│   ├── evaluation_ai.py           # Dynamic evaluation function
│   ├── evaluation_ai_star1.py     # Evaluation for pruning AI
│   └── static_evaluation.py       # Phase-based evaluation
│
├── models/
│   └── trainer.py                 # Genetic algorithm trainer
│
├── main.py                        # Terminal game entry point
├── gui.py                         # Pygame GUI application
├── best_ai_weights.json          # Trained AI weights
└── requirements.txt              # Python dependencies
```

## 🚀 Installation

### Requirements

- Python 3.8+

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd senet-game

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- `pygame` - GUI interface
- `pyrsistent` - Immutable data structures
- `matplotlib` - Training visualization
- `numpy` - Numerical operations

## 🎯 How to Run

### Terminal Game

```bash
python main.py
```

**Options:**

1. Human vs Human
2. Human vs AI (Expectiminimax with trained weights)
3. Human vs AI (Q-Learning)

### GUI Game

```bash
python gui.py
```

**Features:**

- Visual board representation
- Mouse-based piece selection
- AI depth configuration
- Real-time game state display

### AI Training

```bash
cd models
python trainer.py
```

**Training Options:**

- **Resume (r)**: Continue from latest checkpoint
- **Load (l)**: Use best weights as starting point for new training
- **New (n)**: Start fresh training from scratch

**Configuration** (in `trainer.py`):

```python
POP_SIZE = 15           # Population size
GENS = 20               # Number of generations
MATCHES_PER_EVAL = 10   # Evaluation matches per individual
ELITE_SIZE = 6          # Elite individuals to preserve
MUTATION_RATE = 0.3     # Probability of mutation
```

## 🤖 AI Algorithms

### Expectiminimax with Star1 Pruning

The primary AI uses a sophisticated tree search algorithm:

- **Expectiminimax**: Handles probabilistic dice rolls using expected values
- **Star1 Pruning**: Prunes chance nodes by calculating bounds on expected values
- **Alpha-Beta Pruning**: Standard minimax optimization for deterministic nodes
- **Transposition Table**: Caches evaluated states to avoid recomputation
- **Move Ordering**: Evaluates promising moves first for better pruning
- **Iterative Deepening**: Gradually increases search depth

### Q-Learning Agent

Reinforcement learning approach:

- Learns from game experience
- Maintains Q-table of state-action values
- Combines Q-values with heuristic evaluation
- Adaptive weight adjustment based on game outcomes
- Exploration-exploitation balance

## 📊 AI Weight Parameters

The evaluation function uses 12 configurable weights:

| Parameter          | Default | Description                                 |
| ------------------ | ------- | ------------------------------------------- |
| `piece_off`        | 1200    | Value of bearing off pieces                 |
| `win_bonus`        | 20000   | Bonus for winning the game                  |
| `progress_base`    | 85      | Base value for piece advancement            |
| `zone_multiplier`  | 1.8     | Multiplier for endgame zone (squares 21-30) |
| `happiness_bonus`  | 150     | Bonus for House of Happiness                |
| `water_penalty`    | -300    | Penalty for House of Water                  |
| `special_house`    | 100     | Value of special exit houses                |
| `protection`       | 60      | Value of protected pieces (adjacent allies) |
| `block`            | 80      | Value of blocking formations                |
| `attack`           | 60      | Value of attacking opponent pieces          |
| `flexibility`      | 8       | Value per available move                    |
| `isolated_penalty` | 15      | Penalty for isolated pieces                 |

## 📈 Training System

### Genetic Algorithm

The trainer uses evolutionary optimization:

1. **Initialization**: Create diverse population of weight configurations
2. **Evaluation**: Each configuration plays multiple matches against baseline AI
3. **Selection**: Top performers become "elite" and survive to next generation
4. **Crossover**: Combine elite configurations to create offspring
5. **Mutation**: Random variations introduce diversity
6. **Iteration**: Repeat for specified number of generations

### Training Outputs

- `best_ai_weights.json` - Best weights found
- `training_stats.json` - Performance statistics
- `checkpoints/` - Periodic training checkpoints
- `backups/` - Timestamped weight backups
- `training_progress_*.png` - Visualization graphs

### Visualization

Training produces detailed graphs showing:

- Best and average scores over generations
- Population diversity metrics
- Generation-to-generation improvement
- Weight parameter evolution
- Comparison with previous training runs

## 🎮 Controls

### Terminal Interface

- Press Enter to throw sticks
- Enter move index (0, 1, 2...) to select move

### GUI Interface

- Click "Throw Sticks" button
- Click on a piece to select it
- Click on highlighted destination or "EXIT" zone
- Click "Menu" to return to main menu

## 📝 Special Houses

| Square | Name                  | Effect                                 |
| ------ | --------------------- | -------------------------------------- |
| 15     | House of Rebirth      | Where pieces return when sent back     |
| 26     | House of Happiness    | Must land exactly when passing through |
| 27     | House of Water        | Pieces are sent back to Rebirth        |
| 28     | House of Three Truths | Requires roll of 3 to exit             |
| 29     | House of Re-Atum      | Requires roll of 2 to exit             |
| 30     | House of Horus        | Any roll can exit                      |

## 🔧 Configuration

### AI Depth

Default search depth is 3 moves ahead. Adjustable in:

- `main.py`: `AI(player_symbol=opponent, depth=3, ...)`
- GUI: Input box during AI setup

Higher depth = stronger play but slower performance

### Custom Weights

Load custom weights:

```python
import json
with open("your_weights.json", "r") as f:
    custom_weights = json.load(f)
ai = AI(player_symbol='O', depth=3, weights=custom_weights)
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional evaluation heuristics
- Neural network-based evaluation
- Opening book database
- Endgame tablebase
- Network multiplayer
- Move history and game replay

## 📚 References

- Kendall, Timothy. "Mehen, Mysteries, and Resurrection from the Coiled Serpent." Journal of the American Research Center in Egypt (2007)
- Piccione, Peter A. "The Egyptian Game of Senet and the Migration of the Soul." Before the Pyramids (2011)

---

**Made with ❤️ for the preservation of ancient games**
