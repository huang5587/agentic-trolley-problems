# Agentic Trolley Problems

This project two AI agents that plays the "Absurd Trolley Problems" game on neal.fun.

## Installation and Usage

You can run the agent in two different modes: unassisted (default) and assisted.

The assisted agent uses playwright to assist with game interaction. The unassisted agent relies on tool-use to interact with the game.

The `--enable-saving` flag can be used with either mode to save screenshots of the agent's actions.

```python
 # install dependencies
 pip install -r requirements.txt

 # run unassisted agent
 python main.py

 # run assisted agent
 python main.py --assisted

 # run while saving screen captures to memory.
 python main.py --enable-saving
```
