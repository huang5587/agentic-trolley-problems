import argparse
import asyncio

from commons.assisted_agent import AssistedAgent
from commons.unassisted_agent import UnassistedAgent


async def run(enable_saving: bool = False, assisted: bool = False):
    if assisted:
        print("running with playwright (assisted), enable_saving:", enable_saving)
        agent = AssistedAgent(enable_saving=enable_saving)
        await agent.run()
    else:
        print("running with clicking (unassisted), enable_saving:", enable_saving)
        agent = UnassistedAgent(enable_saving=enable_saving)
        await agent.run()


async def main():
    parser = argparse.ArgumentParser(description="Run the trolley problem solver.")
    parser.add_argument(
        "--enable-saving", action="store_true", help="Enable saving screenshots."
    )
    parser.add_argument(
        "--assisted",
        action="store_true",
        help="Enable assisted mode (uses playwright). Default is unassisted (direct clicking).",
    )
    args = parser.parse_args()

    await run(enable_saving=args.enable_saving, assisted=args.assisted)


if __name__ == "__main__":
    asyncio.run(main())
