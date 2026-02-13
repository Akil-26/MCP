import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from databse_tool import show_datas, insert_data, update_data, delete_data

app = Server("student-db")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="show_datas",
            description="Read all students from database",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="insert_data",
            description="Insert a new student into database",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Student ID (optional, auto-generated if not provided)"},
                    "name": {"type": "string", "description": "Student name"},
                    "age": {"type": "integer", "description": "Student age"}
                },
                "required": ["name", "age"]
            }
        ),
        Tool(
            name="update_data",
            description="Update a student's name and age by id",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Student ID to update"},
                    "name": {"type": "string", "description": "New student name"},
                    "age": {"type": "integer", "description": "New student age"}
                },
                "required": ["id", "name", "age"]
            }
        ),
        Tool(
            name="delete_data",
            description="Delete a student by id from database",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Student ID to delete"}
                },
                "required": ["id"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "show_datas":
        result = show_datas()
    elif name == "insert_data":
        result = insert_data(arguments.get("id"), arguments["name"], arguments["age"])
    elif name == "update_data":
        result = update_data(arguments["id"], arguments["name"], arguments["age"])
    elif name == "delete_data":
        result = delete_data(arguments["id"])
    else:
        result = {"status": "error", "message": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=str(result))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())