import argparse
import asyncio

from commons.eyes import run


async def main():
    parser = argparse.ArgumentParser(description="Run the trolley problem solver.")
    parser.add_argument(
        "--enable-saving", action="store_true", help="Enable saving screenshots."
    )
    parser.add_argument(
        "--enable-clicking", action="store_true", help="Enable clicking."
    )
    args = parser.parse_args()

    if args.enable_saving:
        print("Running with saving enabled")
    if args.enable_clicking:
        print("Running with clicking enabled")

    await run(enable_saving=args.enable_saving, enable_clicking=args.enable_clicking)


if __name__ == "__main__":
    asyncio.run(main())
