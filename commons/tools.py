"""
tools.py
file contains smolagent tools for UnassistedAgent
"""

import json
import os

import pyautogui
from smolagents import tool


@tool
def end_game_tool(finished: bool) -> bool:
    """
    Ends the agent loop when finished is true.

    Args:
        finished: True if the game has ended, false otherwise.

    """
    return finished


@tool
def click_at_coordinates_tool(
    x_cord: int, y_cord: int, reasoning: str, scenario: str
) -> str:
    """
    Clicks at the given coordinates.

    Args:
        x_cord: The x coordinate of the button to click
        y_cord: The y coordinate of the button to click
        scenario: an explanation of the modified trolley problem
        reasoning: The reasoning behind the decision to click at the coordinates

    """

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, "reasoning_log.jsonl")

    response = {
        "scenario": scenario,
        "x_cord": x_cord,
        "y_cord": y_cord,
        "reasoning": reasoning,
    }
    with open(log_file_path, "a") as f:
        f.write(f"{json.dumps(response)}\n")

    # click twice for good measure
    _click_at_coordinates(x_cord, y_cord)
    _click_at_coordinates(x_cord, y_cord)
    return reasoning


def _click_at_coordinates(x, y):
    pyautogui.click(x, y)
