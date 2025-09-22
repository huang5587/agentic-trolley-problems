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


def think_and_click(model: LiteLLMModel, prompt: str, input_image: Image.Image):
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
