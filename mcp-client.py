import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
#from google.genai import types
from concurrent.futures import TimeoutError
from functools import partial
import json
import sys

# Load environment variables from .env file
load_dotenv()



# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


max_iterations = 4
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main():
    reset_state()  # Reset at the start of main
    print("Starting main execution...")
    try:
        # Create a single MCP server connection
        print("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command="python",
            args=["mcp-server.py"]
        )

        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                await session.initialize()
                
                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Successfully retrieved {len(tools)} tools")

                # Create system prompt with available tools
                print("Creating system prompt...")
                print(f"Number of tools: {len(tools)}")
                
                try:
                    # First, let's inspect what a tool object looks like
                    # if tools:
                    #     print(f"First tool properties: {dir(tools[0])}")
                    #     print(f"First tool example: {tools[0]}")
                    
                    tools_description = []
                    for i, tool in enumerate(tools):
                        try:
                            # Get tool properties
                            params = tool.inputSchema
                            desc = getattr(tool, 'description', 'No description available')
                            name = getattr(tool, 'name', f'tool_{i}')
                            
                            # Format the input schema in a more readable way
                            if 'properties' in params:
                                param_details = []
                                for param_name, param_info in params['properties'].items():
                                    param_type = param_info.get('type', 'unknown')
                                    param_details.append(f"{param_name}: {param_type}")
                                params_str = ', '.join(param_details)
                            else:
                                params_str = 'no parameters'

                            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            tools_description.append(tool_desc)
                            print(f"{tool_desc}")
                        except Exception as e:
                            print(f"Error processing tool {i}: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")
                    
                    tools_description = "\n".join(tools_description)
                    print("Successfully created tools description")
                except Exception as e:
                    print(f"Error creating tools description: {e}")
                    tools_description = "Error loading tools"
                
                print("Created system prompt...")
                
                system_prompt = f"""You are a math reasoning agent solving problems in iterations. You have access to various mathematical tools.

                Available tools:
                {tools_description}

                You must respond with EXACTLY ONE line in one of these formats (no additional text):
                1. For function calls:
                {{"function_name": "function_name", "parameters": ["param1", "param2"] }}
                
                2. For final answers:
{{"function_name": "FINAL_ANSWER", "parameters": [number] }}

                Examples:
                - {{"function_name": "add", "parameters": [5, 3] }}
                - {{"function_name": "strings_to_chars_to_int", "parameters": ["INDIA"] }}
                - {{"function_name": "FINAL_ANSWER", "parameters": [42] }}
                - {{"function_name": "show_reasoning", "parameters": ["First, I need to identify the multiples of 5 between 1 and 20. These are 5, 10, 15, and 20.", "Next, I need to add these multiples together.", "Finally, I need to find the square root of the sum."] }}

                Important:
                - Run the show_reasoning tool only once in the first iteration.
                - When a function returns multiple values, you need to process all of them.
                - If parameters are strings, they must be enclosed in double quotes. 
                - If parameters are arrays, they must be enclosed in single square brackets.
                - Only give FINAL_ANSWER when you have completed all necessary calculations
                - Do not repeat function calls with the same parameters.
                - Do not add parentheses to the function name.
                - DO NOT include any explanations or additional text.
                - Your entire response should be a JSON object.
                - If user asks non-mathematical queries, you must respond with "I'm sorry, I can only help with mathematical queries."
                - If user asks to verify the result, you must call the verify tool with the result as the parameter.
                - For the show_reasoning tool, in the last step of the reasoning, tag the appropriate reasoning type in one word like arithmetic, logic, etc.

                """

                #query = """Find the ASCII values of characters in INDIA and then return sum of exponentials of those values. """

                # Get query from command line arguments or use default
                default_query = """Find the ASCII values of characters in INDIA and then return sum of exponentials of those values. """
                query = """ """
                query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else default_query
                
                print("Starting iteration loop...")
                
                # Use global iteration variables
                global iteration, last_response
                
                while iteration < max_iterations:
                    print(f"\n--- Iteration {iteration + 1} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    # Get model's response with timeout
                    print("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"{response_text}")
                        
                        # # Find the FUNCTION_CALL line in the response
                        # for line in response_text.split('\n'):
                        #     line = line.strip()
                        #     if line.startswith("FUNCTION_CALL:"):
                        #         response_text = line
                        #         break
                        
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        break


                    # if response_text.startswith("FUNCTION_CALL:"): 
                    #     _, function_info = response_text.split(":", 1)
                    #     parts = [p.strip() for p in function_info.split("|")]
                    #     func_name, params = parts[0], parts[1:]
                        
                    #     print(f"\nDEBUG: Raw function info: {function_info}")
                    #     print(f"DEBUG: Split parts: {parts}")
                    #     print(f"DEBUG: Function name: {func_name}")
                    #     print(f"DEBUG: Raw parameters: {params}")

                    # Parse the JSON response
                    try:
                        response_json = json.loads(response_text)
                        print(f"DEBUG: Parsed JSON: {response_json}")
                        func_name = response_json.get('function_name')
                        print(f"DEBUG: Function name: {func_name}")
                        params = response_json.get('parameters')
                        print(f"DEBUG: Parameters: {params}")
                    except json.JSONDecodeError:
                        print("Error parsing JSON response")
                        func_name = None
                        params = None
                        
                    if func_name and params:
                        try:
                            # Find the matching tool to get its input schema
                            tool = next((t for t in tools if t.name == func_name), None)

                            if func_name == "FINAL_ANSWER":
                                print("\n=== Agent Execution Complete ===")
                                break

                            if not tool:
                                print(f"DEBUG: Available tools: {[t.name for t in tools]}")
                                raise ValueError(f"Unknown tool: {func_name}")

                            print(f"DEBUG: Found tool: {tool.name}")
                            print(f"DEBUG: Tool schema: {tool.inputSchema}")

                            # Replace the parameter conversion section with this improved version
                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})

                            # Get the first property name from schema (since your format uses array of parameters)
                            param_names = list(schema_properties.keys())

                            for i, param_value in enumerate(params):
                                if i >= len(param_names):
                                    break  # Don't process more parameters than we have schema properties
                                    
                                param_name = param_names[i]
                                param_info = schema_properties[param_name]
                                param_type = param_info.get('type', 'string')
                                
                                # Convert value based on the parameter type
                                try:
                                    if param_type == 'integer':
                                        arguments[param_name] = int(param_value)
                                    elif param_type == 'number':
                                        arguments[param_name] = float(param_value)
                                    elif param_type == 'array':
                                        # If the value is already a list, use it directly
                                        if isinstance(param_value, list):
                                            arguments[param_name] = param_value
                                        # If it's a string representation of a list, parse it
                                        elif isinstance(param_value, str):
                                            # Remove brackets and split by comma
                                            clean_value = param_value.strip('[]')
                                            if clean_value:
                                                # Handle array item types based on items schema if available
                                                items_type = param_info.get('items', {}).get('type', 'string')
                                                if items_type == 'integer':
                                                    arguments[param_name] = [int(x.strip()) for x in clean_value.split(',')]
                                                elif items_type == 'number':
                                                    arguments[param_name] = [float(x.strip()) for x in clean_value.split(',')]
                                                else:
                                                    arguments[param_name] = [x.strip() for x in clean_value.split(',')]
                                            else:
                                                arguments[param_name] = []
                                    elif param_type == 'boolean':
                                        # Handle boolean values
                                        if isinstance(param_value, str):
                                            arguments[param_name] = param_value.lower() == 'true'
                                        else:
                                            arguments[param_name] = bool(param_value)
                                    else:
                                        # Default to string for unknown types
                                        arguments[param_name] = str(param_value)
                                except (ValueError, TypeError) as e:
                                    print(f"Error converting parameter {param_name}: {e}")
                                    raise ValueError(f"Invalid value for parameter {param_name}: {param_value}")



                            print(f"DEBUG: Final parameters: {params}")
                            print(f"DEBUG: Calling tool {func_name}")

                            
                            
                            result = await session.call_tool(func_name, arguments)
                            print(f"DEBUG: Raw result: {result}")
                            
                            # Get the full result content
                            if hasattr(result, 'content'):
                                print(f"DEBUG: Result has content attribute")
                                # Handle multiple content items
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        item.text if hasattr(item, 'text') else str(item)
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                print(f"DEBUG: Result has no content attribute")
                                iteration_result = str(result)
                                
                            print(f"DEBUG: Final iteration result: {iteration_result}")
                            
                            # Format the response based on result type
                            if isinstance(iteration_result, list):
                                result_str = f"[{', '.join(iteration_result)}]"
                            else:
                                result_str = str(iteration_result)
                            
                            if func_name == "show_reasoning":
                                iteration_response.append(
                                    f"User: In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                    f"and the function returned {result_str}. Now proceed to do the calculations."
                                )
                            elif func_name == "verify" and result_str == "True":
                                iteration_response.append(
                                    f"User: In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                    f"and the function returned {result_str}. Verified. Next step?"
                                )
                            else:
                                iteration_response.append(
                                    f"User: In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                    f"and the function returned {result_str}. Let's verify the result."
                                )

                            print(f"Iteration_response: {iteration_response}")
                            last_response = iteration_result

                            print(f"Iteration_result: {iteration_result}")

                        except Exception as e:
                            print(f"DEBUG: Error details: {str(e)}")
                            print(f"DEBUG: Error type: {type(e)}")
                            import traceback
                            traceback.print_exc()
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break

                    # elif response_text.startswith("FINAL_ANSWER:"):
                    #     print("\n=== Agent Execution Complete ===")
                        # break



                        #result = await session.call_tool("open_paint")
                        #result = await session.call_tool("mac_open_keynote")
                        #print(result.content[0].text)

                        # Wait longer for Paint to be fully maximized
                        #await asyncio.sleep(1)

                        # Draw a rectangle
                        # result = await session.call_tool(
                        #     "mac_draw_rectangle",
                        #     arguments={
                        #         "x1": 780,
                        #         "y1": 380,
                        #         "x2": 1140,
                        #         "y2": 700
                        #     }
                        # )
                        # print(result.content[0].text)

                        # Draw rectangle and add text
                        # result = await session.call_tool(
                        #     "mac_add_text_in_keynote",
                        #     arguments={
                        #         "text": response_text
                        #     }
                        # )
                        # print(result.content[0].text)
                        # break

                    iteration += 1

    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        reset_state()  # Reset at the end of main

if __name__ == "__main__":
    asyncio.run(main())
    
    
