"""
eyes.py
requirements:
- screenshot current window
- apply (x, y) coordinates to the screenshot
- return image with the coordinates applied
"""

import asyncio
import datetime
import os

import mss
import pywinctl as pwc
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright
from smolagents import LiteLLMModel

from commons.brain import think, think_and_click
from commons.config import MODELS, URL, TrolleyProblemDecision


def _screenshot_monitor(enable_saving: bool = False) -> Image.Image:
    with mss.mss() as sct:
        print(sct.monitors)
        monitor = sct.monitors[1]  # Use the primary monitor
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    img = _draw_overlay(img)

    if enable_saving:
        _save_image(img)

    return img


def _draw_overlay(img):
    draw = ImageDraw.Draw(img)
    grid_spacing = 135
    font = ImageFont.load_default(size=13)
    line_color = (200, 200, 200)
    text_color = (255, 0, 0)
    width, height = img.size

    print(f"Width: {width}, Height: {height}")
    # Draw grid lines
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=line_color)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=line_color)

    # Display (x,y) coordinates at each grid point
    for x in range(0, width, grid_spacing):
        for y in range(0, height, grid_spacing):
            text = f"({x}, {y})"
            draw.text((x, y), text, fill=text_color, font=font)
    return img


def _get_pw_window_coords() -> tuple[int, int, int, int]:
    """gets coordinates of playwright browser window"""
    window = pwc.getWindowsWithTitle("Chromium", condition=pwc.Re.CONTAINS)[0]
    coords = window.getClientFrame()
    return coords


def _screenshot_window(coords: tuple[int, int, int, int]) -> Image.Image:
    with mss.mss() as sct:
        sct_img = sct.grab(coords)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    return img


def _save_image(img: Image.Image):
    # save image
    output_dir = "captures"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filepath = os.path.join(
        output_dir, f"cap_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    )
    print(f"Saving image to {output_filepath}")
    img.save(output_filepath)


async def _run_with_playwright(enable_saving: bool = False):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[f"--window-position={monitor['left']},{monitor['top']}"],
        )
        page = await browser.new_page(
            viewport={"width": monitor["width"], "height": monitor["height"]}
        )
        await page.goto(URL)

        OR_KEY = os.environ["OPENROUTER_API_KEY"]
        model = LiteLLMModel(model_id="openrouter/" + MODELS[2])
        while True:
            await asyncio.sleep(4)
            coords = _get_pw_window_coords()
            img = _screenshot_window(coords)
            if enable_saving:
                _save_image(img)

            prompt = """
            You are solving a modified trolley problem. Based off the situation, you must decide between pulling the lever or doing nothing.

            Your input image will depict the modified trolley problem, with an (x,y) coordinate overlay.

            To make your decision, give the DecideTrolleyProblemTool the string "Pull the Lever" or "Do Nothing".
    
            Your response must be a python dict according to the following schema:
            {
                "reasoning": str,
                "decision": Literal["Pull the lever", "Do nothing"]
            }
            
            Never ever return JSON object, python wrapped in markdown. Only return a python dict. Never wrap your response in markdown.
            """

            response = think(model, prompt, img)

            # print(f"\n response: {response}, type: {type(response)}")
            if response["decision"] == TrolleyProblemDecision.Pull_lever.value:
                await page.click('button.action:has-text("Pull the lever")')
            elif response["decision"] == TrolleyProblemDecision.Do_nothing.value:
                await page.click('button.action:has-text("Do nothing")')
            else:
                raise ValueError(f"Invalid decision: {response['decision']}")
            await page.locator(selector=".action-next").click()  # type: ignore


async def _run_with_clicking(enable_saving: bool = False):
    OR_KEY = os.environ["OPENROUTER_API_KEY"]
    model = LiteLLMModel(model_id="openrouter/" + MODELS[3])
    prompt = """
    You are solving a modified trolley problem. Based off the situation, you must decide between pulling the lever or doing nothing.

    Your input image will depict the modified trolley problem, with an (x,y) coordinate overlay.

    To make your decision, give the click_at_coordinates_tool the coordinates that overlay over the button that corresponds to your decision.

    Your coordinate response must be based off the coordinate overlay in the image.
    The tool will then click on the button, causing the trolley to go left or right.

    If the input image has a button that says "Next", you must click on it by returning its (x,y) coordinates to click_at_coordinates_tool
    """
    while True:
        await asyncio.sleep(4)
        image = _screenshot_monitor(enable_saving)
        think_and_click(model, prompt, image)


async def run(enable_saving: bool = False, enable_clicking: bool = False):
    if enable_clicking:
        print("running with clicking, enable_saving:", enable_saving)
        await _run_with_clicking(enable_saving)
    else:
        print("running with playwright, enable_saving:", enable_saving)
        await _run_with_playwright(enable_saving)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
