"""Core game loop for the UC4E tutorial level."""

from __future__ import annotations

from typing import List

import pygame

from . import config, dialogue, rooms, puzzles
from .player import Player
from .ui import DialogueBox, DialogueLine


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("UNIVERSE CONNECTED FOR EVERYONE — The Quantum Lab")
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(config.FONT_MAIN, 20)
        self.small_font = pygame.font.Font(config.FONT_MAIN, 16)

        self.players = [
            Player("Dr. Elena Vega", pygame.Vector2(200, 200), pygame.Color("#7eb2c6")),
            Player("Dr. Arun Patel", pygame.Vector2(260, 200), pygame.Color("#c1dadd")),
        ]
        self.active_player_index = 0

        self.rooms: List[rooms.Room] = rooms.create_rooms_sequence()
        self.current_room_index = 0
        self.current_room = self.rooms[self.current_room_index]
        self.dialogue_box = DialogueBox(self.font)
        self.dialogue_box.add_lines(dialogue.opening_briefing())

        self.hud_messages: List[str] = []
        self.running = True

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_TAB:
                    self.active_player_index = (self.active_player_index + 1) % len(self.players)
                elif event.key == pygame.K_e:
                    self._try_interact()
                elif event.key == pygame.K_RETURN:
                    self._try_advance_room()

    def update(self, dt: float) -> None:
        room = self.current_room
        self.hud_messages = []
        walls = tuple(room.world_rects())
        active_player = self.players[self.active_player_index]
        active_player.update(dt, walls)

        # Keep companion nearby
        companion_index = (self.active_player_index + 1) % len(self.players)
        companion = self.players[companion_index]
        direction = active_player.position - companion.position
        if direction.length_squared() > 1:
            if direction.length() > 1:
                direction = direction.normalize()
            companion.position += direction * 120 * dt

        self.dialogue_box.update(dt)
        room.try_trigger_intro(self.dialogue_box)
        room.try_trigger_completion(self.dialogue_box)

        if isinstance(room.puzzle, puzzles.TunnelingPuzzle):
            probability = room.puzzle.last_probability
            self.hud_messages.append(f"Tunneling probability: {probability:.2f}")
        elif isinstance(room.puzzle, puzzles.UncertaintyPuzzle):
            self.hud_messages.append(
                f"Beam waist: {room.puzzle.slider_position.value:.2f}  Momentum spread: {room.puzzle.slider_momentum.value:.2f}"
            )

    def draw(self) -> None:
        self.screen.fill(config.COLOR_BACKGROUND)
        room = self.current_room
        room.draw(self.screen)

        for player in self.players:
            player.draw(self.screen)

        self._draw_interaction_prompts()
        self.dialogue_box.draw(self.screen)
        self._draw_hud()
        pygame.display.flip()

    def _draw_interaction_prompts(self) -> None:
        room = self.current_room
        active_player = self.players[self.active_player_index]
        for interaction in room.interactions:
            distance = active_player.position.distance_to(interaction.position)
            if distance <= config.INTERACT_DISTANCE:
                prompt = self.small_font.render(f"[E] {interaction.prompt}", True, config.COLOR_TEXT)
                self.screen.blit(prompt, (interaction.position.x - prompt.get_width() / 2, interaction.position.y - 40))

        if room.exit_position and room.puzzle.solved:
            distance = active_player.position.distance_to(room.exit_position)
            if distance <= config.INTERACT_DISTANCE:
                prompt = self.small_font.render("[ENTER] Continue", True, config.COLOR_HOLOGRAM)
                self.screen.blit(prompt, (room.exit_position.x - prompt.get_width() / 2, room.exit_position.y - 40))

    def _draw_hud(self) -> None:
        header = self.font.render(self.current_room.name, True, config.COLOR_TEXT)
        self.screen.blit(header, (24, 24))
        active_name = self.players[self.active_player_index].name
        controlled = self.small_font.render(f"Active: {active_name} (TAB to switch)", True, config.COLOR_HOLOGRAM)
        self.screen.blit(controlled, (24, 60))
        instructions = self.small_font.render("Move: WASD/Arrows   Interact: E   Advance: Enter", True, config.COLOR_TEXT)
        self.screen.blit(instructions, (24, 88))
        for idx, message in enumerate(self.hud_messages):
            rendered = self.small_font.render(message, True, config.COLOR_ACCENT_AMBER)
            self.screen.blit(rendered, (24, 120 + idx * 22))

        codex = self.small_font.render("Codex Recap: press C (not implemented)", True, config.COLOR_BACKGROUND)
        self.screen.blit(codex, (24, config.SCREEN_HEIGHT - 40))

    def _try_interact(self) -> None:
        room = self.current_room
        active_player = self.players[self.active_player_index]
        for interaction in room.interactions:
            if active_player.position.distance_to(interaction.position) <= config.INTERACT_DISTANCE:
                interaction.callback(room)
                break

    def _try_advance_room(self) -> None:
        room = self.current_room
        if not room.puzzle.solved or room.exit_position is None:
            return
        active_player = self.players[self.active_player_index]
        if active_player.position.distance_to(room.exit_position) > config.INTERACT_DISTANCE:
            return
        if self.current_room_index + 1 < len(self.rooms):
            self.current_room_index += 1
            self.current_room = self.rooms[self.current_room_index]
            for player in self.players:
                player.position = pygame.Vector2(200, 600)
            self.dialogue_box.add_lines(dialogue.hallway_transition(self.current_room.name))
        else:
            self.dialogue_box.add_lines(
                [
                    DialogueLine("Dr. Elena Vega", "Tutorial complete. Let's debrief with the codex."),
                    DialogueLine("System", dialogue.codex_recap()),
                ]
            )


def run() -> None:
    Game().run()
