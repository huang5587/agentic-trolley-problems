import asyncio
import base64
import json
import os
from io import BytesIO

import mss
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from playwright.async_api import async_playwright

from commons.config import API_BASE_URL, API_KEY, ASSISTED_MODEL, GAME_URL
from commons.utils import _get_pw_window_coords, _save_image, _screenshot_window

load_dotenv()

# Constants
WAIT_INTERVAL = 3
DECISION_BUTTON_SELECTOR = 'button.action:has-text("{decision}")'
NEXT_BUTTON_SELECTOR = ".action-next"

DECIDE_TROLLEY_PROBLEM_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "decide_trolley_problem",
        "description": "Logs the trolley problem decision with scenario and reasoning. Decision can be 'Pull the lever' or 'Do nothing'",
        "parameters": {
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "string",
                    "description": "An explanation of the modified trolley problem",
                },
                "reasoning": {
                    "type": "string",
                    "description": "The reasoning behind the decision",
                },
                "decision": {
                    "type": "string",
                    "description": "The selected decision. Must match the text of one of the buttons in the image.",
                },
            },
            "required": ["scenario", "reasoning", "decision"],
        },
    },
}

SYSTEM_PROMPT = """
You are an AI agent playing a game that presents a series of modified trolley problems. You will be shown an image of each scenario.

Your Goal:
Analyze the image to understand the moral dilemma and make a decision.

Your Task:
1.  Analyze the image: Carefully observe the tracks, the lever, and who is on each track. The scenarios are variations of the classic trolley problem.
2.  Formulate your reasoning: Based on your analysis, explain your decision-making process.
3.  Make a decision: Identify the two available actions from the buttons in the image and choose one.
4.  Provide your response: Your output must be a single Python dictionary.

Output Format:
Your response MUST be a valid Python dictionary with the following structure. Do not add any other text or formatting around it.

{
    "scenario": "An explanation of the modified trolley problem",
    "decision": "The text of the button you want to click",
    "reasoning": "Your detailed reasoning for the decision.",
}


Crucial Instructions:
-   Do not wrap the dictionary in markdown (e.g., ```python ... ```).
-   Do not output a JSON object.
"""


class AssistedAgent:
    def __init__(
        self,
        model_name: str = ASSISTED_MODEL,
        log_file_path: str = "logs/playwright_logs.jsonl",
        enable_saving: bool = False,
        monitor_index: int = 1,
    ):
        self.model_name = model_name
        self.log_file_path = log_file_path
        self.enable_saving = enable_saving
        self.monitor_index = monitor_index

        self.prompt = SYSTEM_PROMPT

        self.client = AsyncOpenAI(
            base_url=API_BASE_URL,
            api_key=API_KEY,
        )

    def _save_decision_to_log(self, decision_data: dict):
        """Appends a decision dictionary to the reasoning log file."""
        log_dir = os.path.dirname(self.log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(self.log_file_path, "a") as f:
            f.write(f"{json.dumps(decision_data)}\n")

    async def run(self):
        with mss.mss() as sct:
            if self.monitor_index < len(sct.monitors):
                monitor = sct.monitors[self.monitor_index]
            else:
                print(f"Monitor index {self.monitor_index} is out of bounds.")
                monitor = sct.monitors[0]  # Fallback to primary monitor

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=[f"--window-position={monitor['left']},{monitor['top']}"],
            )
            page = await browser.new_page(
                viewport={"width": monitor["width"], "height": monitor["height"]}
            )
            await page.goto(GAME_URL)

            while True:
                await asyncio.sleep(WAIT_INTERVAL)
                coords = _get_pw_window_coords()
                if not coords:
                    print("Playwright window not found. Exiting.")
                    break
                img = _screenshot_window(coords)
                if self.enable_saving:
                    _save_image(img)

                buffered = BytesIO()
                img.save(buffered, format="PNG")
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

                messages = [
                    {
                        "role": "system",
                        "content": self.prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            }
                        ],
                    },
                ]
                tools = [DECIDE_TROLLEY_PROBLEM_TOOL]
                decision = None
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        tools=tools,
                        tool_choice={
                            "type": "function",
                            "function": {"name": "decide_trolley_problem"},
                        },
                    )

                    response_message = response.choices[0].message
                    tool_calls = response_message.tool_calls
                    if tool_calls:
                        available_functions = {
                            "decide_trolley_problem": self._decide_trolley_problem,
                        }
                        tasks = []
                        for tool_call in tool_calls:
                            if tool_call.type != "function":
                                continue
                            function_name = tool_call.function.name
                            function_to_call = available_functions[function_name]
                            function_args = json.loads(tool_call.function.arguments)
                            # print("@@@ function_args:", function_args)
                            self._save_decision_to_log(function_args)
                            decision = function_args.get("decision")
                            tasks.append(function_to_call(**function_args))

                        await asyncio.gather(*tasks)

                except Exception as e:
                    print("error:", e)

                if decision:
                    await page.click(DECISION_BUTTON_SELECTOR.format(decision=decision))

                await page.locator(selector=NEXT_BUTTON_SELECTOR).click()  # type: ignore

    async def _decide_trolley_problem(
        self, scenario: str, reasoning: str, decision: str
    ) -> str:
        """
        Logs the trolley problem decision with scenario and reasoning.
        Decision can be "Pull the lever" or "Do nothing"

        Args:
            scenario: An explanation of the modified trolley problem
            reasoning: The reasoning behind the decision
            decision: The selected decision. Must be either "Pull the lever" or "Do nothing"

        Returns:
            JSON string with the logged response
        """
        response = {
            "scenario": scenario,
            "decision": decision,
            "reasoning": reasoning,
        }
        return json.dumps(response)
