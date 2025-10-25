# UNIVERSE CONNECTED FOR EVERYONE — The Quantum Lab Prototype

This repository contains a self-contained pygame prototype for Level 1 of **UNIVERSE CONNECTED FOR EVERYONE (UC4E)**. The opening chapter follows Dr. Elena Vega and Dr. Arun Patel as they guide the player through four tutorial rooms inside the Quantum Lab, each illustrating a core quantum mechanic.

## Features

- Top-down twin-scientist control with quick swapping between Dr. Vega and Dr. Patel.
- Four handcrafted rooms that mirror the learning beats in the book:
  1. **Superposition Bay** – collapse a dual-door layout by toggling detectors.
  2. **Entanglement Hall** – synchronize remote switches that share a state.
  3. **Uncertainty Workshop** – balance beam focus and momentum spread using paired sliders.
  4. **Tunneling Corridor** – tune an energy dial and attempt probabilistic tunneling.
- Diegetic dialogue that reinforces the science language from UC4E and keeps the doctors foregrounded.
- Interaction prompts and puzzle-specific HUD readouts to make abstract concepts feel tangible.

## Getting Started

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the prototype**

   ```bash
   python main.py
   ```

## Controls

- **WASD / Arrow Keys** – Move the active scientist.
- **Tab** – Swap between Dr. Elena Vega and Dr. Arun Patel.
- **E** – Interact with highlighted lab equipment.
- **Enter** – Advance to the next room once its puzzle is solved.
- **Esc** – Quit the game.

## Project Structure

```
uc4e/
  config.py         # Shared constants and palette colors
  dialogue.py       # Intro beats and codex recap text
  game.py           # Main loop and state transitions
  player.py         # Player movement + rendering
  puzzles.py        # Puzzle mechanics for each quantum room
  rooms.py          # Tile layouts, interactions, and dialogue hooks
  ui.py             # Dialogue box rendering utilities
main.py             # Entry point
requirements.txt    # Runtime dependency pins
THEBOOK.pdf         # Reference manuscript supplied by the author
```

## Next Steps

- Swap placeholder shapes with the illustrated assets defined in the art direction toolkit.
- Connect the codex recap to a proper UI panel and integrate data sourced directly from the book once the lore placeholders are ready.
- Expand interactions to support co-op play and deeper simulation of lab instrumentation.

Enjoy exploring the Quantum Lab! Elena and Arun will keep the science honest while you experiment.
