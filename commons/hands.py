"""
hands.py
requirements:
- based off LLM response,
- click on the screen at the coordinates
- how to click on the correct screen?
"""

import json
import os

import pyautogui
from smolagents import tool

from commons.config import TrolleyProblemDecision


@tool
def DecideTrolleyProblemTool(
    question: str, reasoning: str, decision: TrolleyProblemDecision
) -> dict[str, str]:
    """
    Clicks at the given coordinates.
    Decision can be "Pull the lever" or "Do nothing"
    Args:
        question: the modifed trolley problem question that is posed
        reasoning: The reasoning behind the decision to click at the coordinates
        decision: The selected decision. Must be either "Pull the lever" or "Do nothing"
    """

    response = {
        "question": question,
        "reasoning": reasoning,
        "decision": decision,
    }

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, "reasoning_log.jsonl")

    with open(log_file_path, "a") as f:
        f.write(f"{json.dumps(response)}\n")

    return response


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

    click_at_coordinates(x_cord, y_cord)
    click_at_coordinates(x_cord, y_cord)
    return reasoning
    # y_cord = y_cord + 35
    # click_at_coordinates(x_cord, y_cord)†
    # print(f"Reasoning: {reasoning}")

    # x_cord = 625
    # y_cord = 815
    # return f"Clicked because: {reasoning}"


def click_at_coordinates(x, y):
    pyautogui.click(x, y)
