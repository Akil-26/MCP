import asyncio
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from contextlib import AsyncExitStack

import ollama
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


class MCPOllamaClient:
    def __init__(self):
        self.session: ClientSession = None
        self.exit_stack = AsyncExitStack()
        self.tools = []

    async def connect(self, server_script: str):
        """Connect to the MCP server via stdio."""
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            cwd=str(Path(server_script).parent)
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()

        # Discover tools from MCP server
        response = await self.session.list_tools()
        self.tools = response.tools
        print(f"Connected! Available tools: {[t.name for t in self.tools]}")

    def _mcp_tools_to_ollama(self):
        """Convert MCP tools to Ollama tool format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in self.tools
        ]

    async def chat(self, user_message: str):
        """Send message to Ollama, route tool calls through MCP server."""
        model = os.getenv("OLLAMA_MODEL", "llama3.2")

        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that manages a student database. "
                        "Use 'show_datas' to list/read/show all students. "
                        "Use 'insert_data' to add a new student (requires 'name' as a string and 'age' as an integer; 'id' is optional). "
                        "Use 'update_data' to update a student (requires 'id', 'name', 'age'). "
                        "Use 'delete_data' to remove a student by their integer 'id'. "
                        "Only call one tool per request. Do not invent parameter values."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            tools=self._mcp_tools_to_ollama()
        )

        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                name = tool_call.function.name
                args = tool_call.function.arguments

                # Cast numeric args to int (Ollama sometimes sends them as strings)
                for key in ("id", "age"):
                    if key in args:
                        try:
                            args[key] = int(args[key])
                        except (ValueError, TypeError):
                            pass

                print(f"Tool: {name}")
                print(f"Args: {args}")

                # Call tool through MCP server
                result = await self.session.call_tool(name, args)
                print(f"Result: {result.content[0].text}")
        else:
            print(response.message.content)

    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
        except (asyncio.CancelledError, Exception):
            pass


async def main():
    client = MCPOllamaClient()
    server_path = str(Path(__file__).parent / "MCP-tools.py")

    try:
        await client.connect(server_path)

        print("\n=== Student Database Chat (MCP + Ollama) ===")
        print("Type 'exit' to quit\n")

        while True:
            try:
                user_input = input("You: ")
            except EOFError:
                print("\nGoodbye!")
                break
            if user_input.strip().lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            await client.chat(user_input)
            print()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())