"""Example usage of math server with CrewAI."""
import asyncio
import logging
from crewai import Agent, Task, Crew
from crewai_adapters import CrewAIAdapterClient
from crewai_adapters.types import AdapterConfig

async def run_math_example():
    """Run an example using the math server with CrewAI."""
    async with CrewAIAdapterClient() as client:
        try:
            # Register math adapter with better logging
            logging.info("Registering math adapter...")
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
            logging.info("Math adapter registered successfully")

            # Get tools with proper error handling
            tools = client.get_tools()
            if not tools:
                raise ValueError("No tools available from the math adapter")
            logging.info(f"Retrieved {len(tools)} tools: {[t.name for t in tools]}")

            # Create math agent
            calculator = Agent(
                role="Math Calculator",
                goal="Perform mathematical calculations accurately",
                backstory="""I am a specialized calculator that performs arithmetic operations. 
                I use tools to add and multiply numbers with precision.""",
                tools=tools,
                allow_delegation=False,  # Prevent unnecessary delegation
                verbose=True
            )

            # Create and assign task with clear instructions
            math_task = Task(
                description="""Calculate (3 + 5) × 12 following these steps:
                1. Use the 'add' tool to add 3 and 5
                2. Use the 'multiply' tool to multiply the sum by 12
                Return the final result.""",
                expected_output="The numerical result of (3 + 5) × 12",
                agent=calculator
            )

            # Create and run crew
            crew = Crew(
                agents=[calculator],
                tasks=[math_task],
                verbose=True
            )

            # Execute with proper logging
            logging.info("Starting calculation...")
            result = crew.kickoff()
            logging.info(f"Calculation complete. Result: {result}")
            return result

        except Exception as e:
            logging.error(f"Error in math example: {str(e)}")
            raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(run_math_example())