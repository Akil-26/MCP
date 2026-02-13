import json
import os
import ollama
from databse_tool import show_datas, insert_data, update_data, delete_data

tools = [
    {
        "type": "function",
        "function": {
            "name": "show_datas",
            "description": "Read all students from database",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insert_data",
            "description": "Insert a new student into database. If no id is provided, it will be auto-generated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Student ID (optional, auto-generated if not provided)"},
                    "name": {"type": "string", "description": "Student name"},
                    "age": {"type": "integer", "description": "Student age"}
                },
                "required": ["name", "age"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_data",
            "description": "Delete a student by id from database",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Student ID to delete"}
                },
                "required": ["id"]
            }
        }
    }
]

def execute_tool(name, args):
    if name == "show_datas":
        return show_datas()
    elif name == "insert_data":
        return insert_data(args.get("id"), args["name"], args["age"])
    elif name == "update_data":
        return update_data(args["id"], args["name"], args["age"])
    elif name == "delete_data":
        return delete_data(args["id"])
    else:
        return "Unknown tool"

def chat(user_message):
    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that manages a student database. "
                    "Use 'show_datas' to list/read/show all students. "
                    "Use 'insert_data' to add a new student (requires 'name' as a string and 'age' as an integer). "
                    "Use 'delete_data' to remove a student by their integer 'id'. "
                    "Only call one tool per request. Do not invent parameter values."
                )
            },
            {"role": "user", "content": user_message}
        ],
        tools=tools
    )

    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            name = tool_call.function.name
            args = tool_call.function.arguments

            result = execute_tool(name, args)

            print("Tool:", name)
            print("Result:", result)
    else:
        print(response.message.content)

print("=== Student Database Chat ===")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "q"]:
        print("Goodbye!")
        break
    chat(user_input)
    print()