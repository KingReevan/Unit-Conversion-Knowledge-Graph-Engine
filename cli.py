import typer
import asyncio
from training import training_loop
from user_query import agent
from async_training import async_training_loop
from shortest_path import run_algorithm

app = typer.Typer()

@app.command()
def train(cycles: int = 1, questions_per_cycle: int = 100) -> None:
    """
    Run the training workflow for a given number of cycles.
    """
    training_loop(cycles, questions_per_cycle)

@app.command()
def async_train(cycles: int = 1, questions_per_cycle: int = 100) -> None:
    """
    Run the asynchronous version of the training workflow for a given number of cycles.
    """
    asyncio.run(async_training_loop(cycles, questions_per_cycle))

@app.command()
def ask(query: str) -> None:
    """
    Ask Knowledge Graph for Unit Conversions
    Parameters: query (str): The user query string -> eg. "convert 5 meters to centimeters"
    """
    print(agent(query))

@app.command()
def shortest_path() -> None:
    """
    Multi-hop Algorithm to find shortest path between two nodes
    """
    run_algorithm()

if __name__ == "__main__":
    app()
