"""
brain.py
"""

from PIL import Image
from smolagents import CodeAgent, LiteLLMModel

from commons.hands import DecideTrolleyProblemTool, click_at_coordinates_tool


def think(model: LiteLLMModel, prompt: str, input_image: Image.Image):
    agent = CodeAgent(
        tools=[DecideTrolleyProblemTool],
        model=model,
        max_steps=1,
        use_structured_outputs_internally=True,
    )

    result = agent.run(
        task=prompt,
        images=[input_image],
    )
    return result


def think_and_click(model: LiteLLMModel, input_image: Image.Image):
    prompt = """
    You are solving a modified trolley problem. Based off the situation, you must decide between pulling the lever or doing nothing.

    Your input image will depict the modified trolley problem, with an (x,y) coordinate overlay.

    To make your decision, give the click_at_coordinates_tool the coordinates that overlay over the button that corresponds to your decision.

    Your coordinate response must be based off the coordinate overlay in the image.
    The tool will then click on the button, causing the trolley to go left or right.

    Think carefully about your decision and its ethical repercussions. Please include your reasoning to the click_at_coordinates_tool as the reasoning parameter.
    
    If the input image has a button that says "Next", you must:
    1. click on it by returning its (x,y) coordinates to click_at_coordinates_tool.
    2. include the percentage of people in agreement stat as the scenario parameter. 
    """
    agent = CodeAgent(
        tools=[click_at_coordinates_tool],
        model=model,
        max_steps=1,
        use_structured_outputs_internally=True,
    )

    result = agent.run(
        task=prompt,
        images=[input_image],
    )
    return result
