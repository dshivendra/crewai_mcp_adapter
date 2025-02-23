"""Example usage of math server with CrewAI."""
import asyncio
import logging
from crewai import Agent, Task, Crew
from crewai_adapters import CrewAIAdapterClient
from crewai_adapters.types import AdapterConfig

async def run_math_example():
    """Run an example using the math server with CrewAI."""
    async with CrewAIAdapterClient() as client:
        # Register math adapter
        await client.register_adapter(
            "math",
            AdapterConfig({
                "tools": [{
                    "name": "add",
                    "description": "Add two numbers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "integer", "description": "First number"},
                            "b": {"type": "integer", "description": "Second number"}
                        },
                        "required": ["a", "b"]
                    }
                }, {
                    "name": "multiply",
                    "description": "Multiply two numbers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "integer", "description": "First number"},
                            "b": {"type": "integer", "description": "Second number"}
                        },
                        "required": ["a", "b"]
                    }
                }]
            })
        )

        # Create math agent
        calculator = Agent(
            role="Math Calculator",
            goal="Perform mathematical calculations accurately",
            backstory="I am a specialized calculator that performs arithmetic operations",
            tools=client.get_tools(),
            verbose=True
        )

        # Create and assign task
        math_task = Task(
            description=(
                "Calculate the following expression: (3 + 5) × 12\n"
                "1. First add 3 and 5\n"
                "2. Then multiply the result by 12"
            ),
            expected_output="The final result of (3 + 5) × 12",
            agent=calculator
        )

        # Create and run crew
        crew = Crew(
            agents=[calculator],
            tasks=[math_task],
            verbose=True
        )

        result = await crew.kickoff()
        logging.info(f"Calculation result: {result}")
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_math_example())