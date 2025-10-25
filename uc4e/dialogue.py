"""Narrative beats and codex entries."""

from __future__ import annotations

from typing import List

from .ui import DialogueLine


def opening_briefing() -> List[DialogueLine]:
    return [
        DialogueLine("Dr. Elena Vega", "Systems nominal. Dr. Patel, ready to bring the Quantum Lab online?"),
        DialogueLine("Dr. Arun Patel", "Always. Once the prototype array spins up we can prove the UNIVERSE CONNECTED FOR EVERYONE thesis."),
        DialogueLine("Dr. Elena Vega", "Any anomalies become teachable moments—perfect for onboarding our new field operator."),
    ]


def hallway_transition(room_name: str) -> List[DialogueLine]:
    return [
        DialogueLine("Dr. Arun Patel", f"Next stop: {room_name}. Let's translate theory into puzzles."),
    ]


def codex_recap() -> str:
    return (
        "Level Recap — The Quantum Lab: We collapsed a superposed doorway with a detector, synced entangled switches across "
        "distance, balanced focus and spread to honor the uncertainty principle, and tuned wave energy until tunneling succeeded. "
        "Quantum behaviors make intuitive sense when you choreograph the lab around them."
    )
