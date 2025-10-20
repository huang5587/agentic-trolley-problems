import base64
import datetime
import os
from io import BytesIO

import mss
import pywinctl as pwc
from PIL import Image


def _get_pw_window_coords() -> tuple[int, int, int, int]:
    """gets coordinates of playwright browser window"""
    window = pwc.getWindowsWithTitle("Chromium", condition=pwc.Re.CONTAINS)[0]
    coords = window.getClientFrame()
    return coords


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


def _screenshot_window(coords: tuple[int, int, int, int]) -> Image.Image:
    with mss.mss() as sct:
        sct_img = sct.grab(coords)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    return img


def _image_to_base64(img: Image.Image) -> str:
    """converts a PIL image to a base64 string"""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str
