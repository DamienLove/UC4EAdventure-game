"""Shared configuration constants for the UC4E prototype."""

from __future__ import annotations

import pygame

# Screen + grid settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 64
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Colors aligned with the art direction palette
COLOR_BACKGROUND = pygame.Color("#26363b")
COLOR_FLOOR = pygame.Color("#3b5358")
COLOR_FLOOR_ACCENT = pygame.Color("#576f77")
COLOR_HOLOGRAM = pygame.Color("#5ed5ff")
COLOR_ACCENT_GREEN = pygame.Color("#40b147")
COLOR_ACCENT_RED = pygame.Color("#e54b4b")
COLOR_ACCENT_VIOLET = pygame.Color("#8d6eff")
COLOR_ACCENT_AMBER = pygame.Color("#f3c451")
COLOR_WALL = pygame.Color("#0f1b1e")
COLOR_TEXT = pygame.Color("#f2f5f5")
COLOR_DIALOGUE_BG = pygame.Color(20, 32, 36, 220)

PLAYER_SPEED = 220  # units per second
INTERACT_DISTANCE = 72

FONT_MAIN = "freesansbold.ttf"

# Dialogue display
DIALOGUE_LINE_DURATION = 6.0
