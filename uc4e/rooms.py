"""Room definitions and layout management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Sequence

import pygame

from . import config, puzzles
from .ui import DialogueLine


@dataclass
class Interaction:
    name: str
    position: pygame.Vector2
    callback: Callable[["Room"], None]
    prompt: str

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.position.x - 28), int(self.position.y - 28), 56, 56)


@dataclass
class Room:
    name: str
    tilemap: List[List[int]]
    puzzle: puzzles.Puzzle
    interactions: List[Interaction] = field(default_factory=list)
    intro_dialogue: Sequence[DialogueLine] = field(default_factory=list)
    solved_dialogue: Sequence[DialogueLine] = field(default_factory=list)
    exit_position: pygame.Vector2 | None = None
    _intro_triggered: bool = False
    _completion_announced: bool = False

    def world_rects(self) -> List[pygame.Rect]:
        rects: List[pygame.Rect] = []
        for y, row in enumerate(self.tilemap):
            for x, cell in enumerate(row):
                if cell == 1:  # wall
                    rects.append(
                        pygame.Rect(
                            x * config.TILE_SIZE,
                            y * config.TILE_SIZE,
                            config.TILE_SIZE,
                            config.TILE_SIZE,
                        )
                    )
        if isinstance(self.puzzle, puzzles.SuperpositionPuzzle):
            for door in self.puzzle.doors:
                if not door.open_state:
                    rects.append(door.rect)
        elif isinstance(self.puzzle, puzzles.EntanglementPuzzle):
            for door in self.puzzle.doors:
                if not door.open_state:
                    rects.append(door.rect)
        elif isinstance(self.puzzle, puzzles.TunnelingPuzzle):
            if not self.puzzle.gate.open_state:
                rects.append(self.puzzle.gate.rect)
        return rects

    def draw(self, surface: pygame.Surface) -> None:
        for y, row in enumerate(self.tilemap):
            for x, cell in enumerate(row):
                rect = pygame.Rect(
                    x * config.TILE_SIZE,
                    y * config.TILE_SIZE,
                    config.TILE_SIZE,
                    config.TILE_SIZE,
                )
                if cell == 1:
                    pygame.draw.rect(surface, config.COLOR_WALL, rect)
                else:
                    base_color = config.COLOR_FLOOR if (x + y) % 2 == 0 else config.COLOR_FLOOR_ACCENT
                    pygame.draw.rect(surface, base_color, rect)
                    pygame.draw.rect(surface, config.COLOR_BACKGROUND, rect, width=1)
        self.puzzle.draw(surface)
        for interaction in self.interactions:
            pygame.draw.circle(surface, config.COLOR_HOLOGRAM, interaction.position, 16, width=2)

    def try_trigger_intro(self, dialogue_box) -> None:
        if not self._intro_triggered and self.intro_dialogue:
            dialogue_box.add_lines(self.intro_dialogue)
            self._intro_triggered = True

    def try_trigger_completion(self, dialogue_box) -> None:
        if self.puzzle.solved and not self._completion_announced and self.solved_dialogue:
            dialogue_box.add_lines(self.solved_dialogue)
            self._completion_announced = True


def create_superposition_room() -> Room:
    tilemap = _simple_room_layout()
    detector = puzzles.ToggleTerminal(
        position=pygame.Vector2(640, 320),
        on_color=config.COLOR_ACCENT_GREEN,
        off_color=config.COLOR_ACCENT_VIOLET,
    )
    door_left = puzzles.Door(pygame.Rect(320 - 32, 128, 32, 128), config.COLOR_ACCENT_AMBER, ghost=True)
    door_right = puzzles.Door(pygame.Rect(960, 128, 32, 128), config.COLOR_ACCENT_AMBER, ghost=True)
    puzzle = puzzles.SuperpositionPuzzle(detector, [door_left, door_right])

    def toggle_detector(room: Room) -> None:
        detector.toggle()

    interactions = [
        Interaction("Detector", pygame.Vector2(640, 320), toggle_detector, "Toggle detectors"),
    ]

    intro_dialogue = [
        DialogueLine("Dr. Elena Vega", "Before we look, the system is a weighted \"maybe\" across states. These twin doors model that ambiguity."),
        DialogueLine("Dr. Arun Patel", "Once the detector fires, one pathway becomes real and the other is only a ghost in our readout."),
    ]
    solved_dialogue = [
        DialogueLine("Dr. Elena Vega", "See how the detector collapsed us into one definite exit? Measurement is a kind of choice."),
    ]
    return Room(
        name="Superposition Bay",
        tilemap=tilemap,
        puzzle=puzzle,
        interactions=interactions,
        intro_dialogue=intro_dialogue,
        solved_dialogue=solved_dialogue,
        exit_position=pygame.Vector2(640, 80),
    )


def create_entanglement_room() -> Room:
    tilemap = _simple_room_layout()
    switch_a = puzzles.ToggleTerminal(
        pygame.Vector2(320, 320),
        config.COLOR_ACCENT_GREEN,
        config.COLOR_ACCENT_RED,
    )
    switch_b = puzzles.ToggleTerminal(
        pygame.Vector2(960, 320),
        config.COLOR_ACCENT_GREEN,
        config.COLOR_ACCENT_RED,
    )
    doors = [
        puzzles.Door(pygame.Rect(576, 192, 32, 160), config.COLOR_ACCENT_VIOLET),
        puzzles.Door(pygame.Rect(672, 192, 32, 160), config.COLOR_ACCENT_VIOLET),
    ]
    puzzle = puzzles.EntanglementPuzzle([switch_a, switch_b], doors)

    def toggle_switch_a(_: Room) -> None:
        switch_a.toggle()

    def toggle_switch_b(_: Room) -> None:
        switch_b.toggle()

    interactions = [
        Interaction("Switch A", switch_a.position, toggle_switch_a, "Toggle paired switch"),
        Interaction("Switch B", switch_b.position, toggle_switch_b, "Toggle paired switch"),
    ]

    intro_dialogue = [
        DialogueLine("Dr. Arun Patel", "Measurement here correlates there—no signals, just correlation born together."),
        DialogueLine("Dr. Elena Vega", "Flip one and the far door follows, even across the hall."),
    ]
    solved_dialogue = [
        DialogueLine("Dr. Arun Patel", "With the pair aligned, both gates cooperate. Entanglement rewards good timing."),
    ]

    return Room(
        name="Entanglement Hall",
        tilemap=tilemap,
        puzzle=puzzle,
        interactions=interactions,
        intro_dialogue=intro_dialogue,
        solved_dialogue=solved_dialogue,
        exit_position=pygame.Vector2(640, 80),
    )


def create_uncertainty_room() -> Room:
    tilemap = _simple_room_layout()
    slider_position = puzzles.Slider(pygame.Vector2(512, 320), config.COLOR_ACCENT_AMBER)
    slider_momentum = puzzles.Slider(pygame.Vector2(768, 320), config.COLOR_ACCENT_VIOLET)
    puzzle = puzzles.UncertaintyPuzzle(slider_position, slider_momentum)

    def adjust_focus(room: Room) -> None:
        puzzle.adjust(-0.05, +0.05)

    def adjust_spread(room: Room) -> None:
        puzzle.adjust(+0.05, -0.05)

    interactions = [
        Interaction("Lens Stage", slider_position.position + pygame.Vector2(-64, -48), adjust_focus, "Narrow position"),
        Interaction("Momentum Coil", slider_momentum.position + pygame.Vector2(64, -48), adjust_spread, "Widen momentum"),
    ]

    intro_dialogue = [
        DialogueLine("Dr. Elena Vega", "Locking position blurs momentum, like squeezing one side of a balloon."),
        DialogueLine("Dr. Arun Patel", "To clear the slit, balance sharp focus with a generous spread."),
    ]
    solved_dialogue = [
        DialogueLine("Dr. Elena Vega", "Perfect calibration. The beam threads the aperture and still lands on the sensor."),
    ]

    return Room(
        name="Uncertainty Workshop",
        tilemap=tilemap,
        puzzle=puzzle,
        interactions=interactions,
        intro_dialogue=intro_dialogue,
        solved_dialogue=solved_dialogue,
        exit_position=pygame.Vector2(640, 80),
    )


def create_tunneling_room() -> Room:
    tilemap = _simple_room_layout()
    slider = puzzles.Slider(pygame.Vector2(640, 360), config.COLOR_ACCENT_GREEN)
    gate = puzzles.Door(pygame.Rect(624, 160, 32, 160), config.COLOR_ACCENT_RED)
    puzzle = puzzles.TunnelingPuzzle(slider, gate)

    def tune_up(_: Room) -> None:
        puzzle.tune_energy(+0.05)

    def tune_down(_: Room) -> None:
        puzzle.tune_energy(-0.05)

    def attempt(_: Room) -> None:
        puzzle.attempt_tunnel()

    interactions = [
        Interaction("Energy Dial +", slider.position + pygame.Vector2(120, 0), tune_up, "Increase energy"),
        Interaction("Energy Dial -", slider.position + pygame.Vector2(-120, 0), tune_down, "Decrease energy"),
        Interaction("Gate Console", pygame.Vector2(640, 220), attempt, "Attempt tunneling"),
    ]

    intro_dialogue = [
        DialogueLine("Dr. Arun Patel", "Non-zero chance to appear through the barrier; high when the wave matches the barrier’s profile."),
        DialogueLine("Dr. Elena Vega", "Dial us into resonance and the gate will welcome us through."),
    ]
    solved_dialogue = [
        DialogueLine("Dr. Arun Patel", "We matched the waveform—tunneling granted!"),
    ]

    return Room(
        name="Tunneling Corridor",
        tilemap=tilemap,
        puzzle=puzzle,
        interactions=interactions,
        intro_dialogue=intro_dialogue,
        solved_dialogue=solved_dialogue,
        exit_position=pygame.Vector2(640, 80),
    )


def create_rooms_sequence() -> List[Room]:
    return [
        create_superposition_room(),
        create_entanglement_room(),
        create_uncertainty_room(),
        create_tunneling_room(),
    ]


def _simple_room_layout(width: int = config.GRID_WIDTH, height: int = config.GRID_HEIGHT) -> List[List[int]]:
    layout: List[List[int]] = []
    for y in range(height):
        row: List[int] = []
        for x in range(width):
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                row.append(1)
            else:
                row.append(0)
        layout.append(row)
    return layout
