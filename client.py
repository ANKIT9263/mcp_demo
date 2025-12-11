"""LLM Client for MCP Server Tools"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import add_numbers, greet, get_info, get_config

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define available tools for function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "The first number"
                    },
                    "b": {
                        "type": "integer",
                        "description": "The second number"
                    }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "greet",
            "description": "Greet someone by name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the person to greet"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_info",
            "description": "Get server information",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_config",
            "description": "Get server configuration",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

def call_tool(tool_name: str, arguments: dict) -> dict:
    """Call the MCP server tool function"""
    try:
        if tool_name == "add_numbers":
            result = add_numbers(arguments["a"], arguments["b"])
            return {"result": result, "status": "success"}
        elif tool_name == "greet":
            result = greet(arguments["name"])
            return {"result": result, "status": "success"}
        elif tool_name == "get_info":
            result = get_info()
            return {"result": result, "status": "success"}
        elif tool_name == "get_config":
            result = get_config()
            return {"result": result, "status": "success"}
        else:
            return {"error": f"Unknown tool: {tool_name}", "status": "error"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

def process_message(user_message: str, conversation_history: list = None) -> dict:
    """Process user message using LLM and return response with tool calls"""

    if conversation_history is None:
        conversation_history = []

    tool_calls_info = []

    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Get LLM response with function calling
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Convert response_message to dict for history
    response_dict = {
        "role": "assistant",
        "content": response_message.content
    }

    if tool_calls:
        response_dict["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in tool_calls
        ]

    conversation_history.append(response_dict)

    # If LLM wants to call a tool
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Track tool call
            tool_calls_info.append({
                "tool": function_name,
                "arguments": function_args
            })

            # Call the actual tool from MCP server
            function_response = call_tool(function_name, function_args)

            # Add tool response to conversation
            conversation_history.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response)
            })

        # Get final response from LLM after tool execution
        second_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
        )

        final_message = second_response.choices[0].message.content
        conversation_history.append({
            "role": "assistant",
            "content": final_message
        })

        return {
            "response": final_message,
            "conversation_history": conversation_history,
            "tool_calls": tool_calls_info
        }

    # No tool call needed, return direct response
    return {
        "response": response_message.content or "I'm not sure how to help with that.",
        "conversation_history": conversation_history,
        "tool_calls": tool_calls_info
    }
