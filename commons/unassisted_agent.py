import asyncio

import mss
from PIL import Image, ImageDraw, ImageFont
from smolagents import CodeAgent, LiteLLMModel

from commons.config import UNASSISTED_MODEL
from commons.tools import click_at_coordinates_tool, end_game_tool
from commons.utils import _save_image


class UnassistedAgent:
    def __init__(self, enable_saving: bool = False):
        self.enable_saving = enable_saving
        self.model = LiteLLMModel(model_id="openrouter/" + UNASSISTED_MODEL)

    def _screenshot_monitor(self) -> Image.Image:
        with mss.mss() as sct:
            # print(sct.monitors)
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img = self._draw_overlay(img)

        if self.enable_saving:
            _save_image(img)
        return img

    def _draw_overlay(self, img):
        draw = ImageDraw.Draw(img)
        grid_spacing = 100
        font = ImageFont.load_default(size=13)
        line_color = (137, 137, 137)  # grey gridlines
        text_color = (255, 0, 0)  # red text
        width, height = img.size

        # print(f"Width: {width}, Height: {height}")
        # draw grid
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=line_color)
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=line_color)

        # Display (x,y) coordinates at each grid point
        for x in range(0, width, grid_spacing):
            for y in range(0, height, grid_spacing):
                dot_radius = 2
                draw.ellipse(
                    [
                        (x - dot_radius, y - dot_radius),
                        (x + dot_radius, y + dot_radius),
                    ],
                    fill="black",
                )
                text = f"({x}, {y})"
                draw.text((x, y), text, fill=text_color, font=font)
        return img

    def think_and_click(self, input_image: Image.Image):
        prompt = """
        You are an advanced AI agent tasked with navigating a series of modified trolley problems. Your goal is to make ethical decisions based on the visual information provided in each scenario.

        You have access to an image of the current game screen, which includes a coordinate overlay to help you identify the location of buttons.

        Follow these instructions based on what you see in the image:

        1.  **If you see a "Next" button and statistics about public opinion:**
            *   Use the `click_at_coordinates_tool` to click the "Next" button.
            *   Set the `scenario` parameter to the text showing the percentage of people who agreed with your choice. The coordinate overlay exists to help you locate buttons.
            *   Set the `reasoning` parameter to "Proceeding to the next problem."
            *   This screen appears after you've made a decision.

        2.  **If you see a trolley problem scenario AND there is no "Next" button present:**
            *   Analyze the image and any text to understand the ethical dilemma.
            *   Formulate a clear line of reasoning for your choice. This is the most important step. Document your train of thought.
            *   Based on your reasoning, decide whether to "Pull the lever" or "Do nothing".
            *   Use the `click_at_coordinates_tool` to click on the button corresponding to your decision. The coordinate overlay exists to help you locate buttons.
            *   Set the `reasoning` parameter to your detailed ethical analysis.
            *   Set the `scenario` parameter to a brief description of the trolley problem itself.

        3.  **If you see the message "you have solved philosophy!":**
            *   The game is over.
            *   Call the `end_game_tool` with `finished=True` to exit. Do not use any other tool.

        Always use the coordinate overlay to find your bearings. Think step-by-step and justify your actions.
        Always use the tools provided to solve the problem. Do not chat with the user. Only use one tool at a time.
    """
        agent = CodeAgent(
            tools=[click_at_coordinates_tool, end_game_tool],
            model=self.model,
            max_steps=1,
            # use_structured_outputs_internally=True,
        )

        result = agent.run(
            task=prompt,
            images=[input_image],
            reset=False,
        )
        return result

    async def run(self):
        running = True
        while running:
            await asyncio.sleep(2.5)
            image = self._screenshot_monitor()
            result = self.think_and_click(image)
            output_str = str(result)
            if "end_game_tool" in output_str and "finished=True" in output_str:
                running = False
