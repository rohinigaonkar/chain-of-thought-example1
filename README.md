# 🧠 MCP Learning Project - Chain of Thought

This project demonstrates the implementation of chain-of-thought reasoning using the Model Context Protocol (MCP) and Google's Gemini AI. It showcases how to integrate mathematical operations with step-by-step reasoning and verification capabilities.

## 🔧 What's Inside
The project implements three key components:

### 🤔 Chain of Thought Process

- Iterative reasoning with up to 10 steps
- Step-by-step problem decomposition
- Verification at each stage

### 🧮 Mathematical Tools

- Basic operations (add, subtract, multiply, divide)
- Advanced functions (factorial, log, trigonometry)
- Special operations (ASCII conversions, exponentials)

### ✅ Verification Tools

- Result validation
- Step-by-step verification
- Error detection

## 💡 Purpose
This project serves as a demonstration of:

- Implementing chain-of-thought reasoning with MCP
- Integrating Gemini AI for mathematical problem solving
- Building verification mechanisms into the reasoning process

## 🚀 Quick Start

Clone and Setup

```bash
git clone <your-repository-url>
cd mcp-learning-project
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Configure Environment Variables
Create .env file with your API key:

```
GEMINI_API_KEY=your_api_key_here
```

Run the Agent

```bash
python mcp-client.py "Your math query here"
```

## ✨ Features

Mathematical Capabilities

- Basic arithmetic operations
- Advanced mathematical functions
- ASCII value calculations
- Custom sequences (e.g., Fibonacci)
- Exponential operations

Reasoning Process

- Step-by-step problem decomposition
- Intermediate result verification
- Clear reasoning chain display
- Error handling and validation

🛠️ Technical Stack

- AI Model: Google Gemini 2.0
- Protocol: Model Context Protocol (MCP)
- Language: Python 3.x

📁 Project Structure
```
.
├── mcp-client.py        # Main client implementation
├── mcp-server.py        # MCP server with tool definitions
├── requirements.txt     # Dependencies
└── .env                 # Environment variables
```

### 🔧 Available Tools

Mathematical Operations

```python
# Basic Operations
add(a, b)              # Addition
subtract(a, b)         # Subtraction
multiply(a, b)         # Multiplication
divide(a, b)           # Division
power(a, b)            # Exponentiation

# Advanced Functions
factorial(n)           # Factorial calculation
log(x)                 # Natural logarithm
sin(x), cos(x), tan(x) # Trigonometric functions
sqrt(x)                # Square root
cbrt(x)                # Cube root

# Special Operations
strings_to_chars_to_int(s)      # ASCII conversion
int_list_to_exponential_sum(l)  # Sum of exponentials
fibonacci_numbers(n)            # Fibonacci sequence
```

Reasoning Tools

```python
# Chain of Thought
show_reasoning(steps)           # Display reasoning steps
verify(expression, expected)    # Verify calculations
```

### 🛡️ Error Handling

The system includes robust error handling for:

- Invalid mathematical operations
- Verification failures
- Tool execution errors
- Response timeouts

### 💡 Example Usage

```bash
python mcp-client.py "Calculate sum of first two prime numbers"
```

Example output at the end.

### System Prompt:

```
{
  "explicit_reasoning": true,
  "structured_output": true,
  "tool_separation": true,
  "conversation_loop": true,
  "instructional_framing": true,
  "internal_self_checks": true,
  "reasoning_type_awareness": true,
  "fallbacks": true,
  "overall_clarity": "Well-structured and robust prompt with strong formatting, error handling, and reasoning support. Fully supports iterative, tool-based math problem solving."
}
```

✅ Explicit Reasoning Instructions: Uses a dedicated show_reasoning tool with steps and tagged reasoning type.

✅ Structured Output Format: Enforces strict JSON formatting for all outputs—ensures reliable parsing.

✅ Separation of Reasoning and Tools: Differentiates clearly between reasoning (show_reasoning), function execution, and final results.

✅ Conversation Loop Support: Designed to operate over multiple steps with clarity and guidance for each stage.

✅ Instructional Framing: Rich set of rules, examples, and do’s/don’ts ensures precise behavior.

✅ Internal Self-Checks: Incorporates verification logic (verify tool) for validating results.

✅ Reasoning Type Awareness: Explicitly tags the reasoning type in the show_reasoning step.

✅ Error Handling or Fallbacks: Covers non-mathematical queries with clear fallback instruction.

✅ Overall Clarity and Robustness: Highly readable, comprehensive, and designed for error minimization and consistent behavior.


Example Output:

```
% uv run mcp-client.py "Add every multiple of 5 from 1 to 20, return the square root of that sum"

Starting main execution...
Establishing connection to MCP server...
Connection established, creating session...
Session created, initializing...

Requesting tool list...
Successfully retrieved 20 tools
Creating system prompt...

Number of tools: 20
1. show_reasoning(steps: string) - Shows the LLM's step-by-step reasoning thought process. RUN THIS ONLY ONCE IN FIRST STEP.
2. verify(expression: string, expected: string) - Verify if a calculation is correct uses the python eval function. Can handle both single values and lists.
3. add(a: integer, b: integer) - Add two numbers
4. add_list(l: array) - Add all numbers in a list
5. subtract(a: integer, b: integer) - Subtract two numbers
6. multiply(a: integer, b: integer) - Multiply two numbers
7. divide(a: integer, b: integer) - Divide two numbers
8. power(a: integer, b: integer) - Power of two numbers. Only accepts integer values for both base and exponent.
9. sqrt(a: integer) - Square root of a number
10. cbrt(a: integer) - Cube root of a number
11. factorial(a: integer) - factorial of a number
12. log(a: integer) - log of a number
13. remainder(a: integer, b: integer) - remainder of two numbers divison
14. sin(a: integer) - sin of a number
15. cos(a: integer) - cos of a number
16. tan(a: integer) - tan of a number
17. mine(a: integer, b: integer) - special mining tool
18. strings_to_chars_to_int(string: string) - Return the ASCII values of the characters in a word
19. int_list_to_exponential_sum(int_list: array) - Return sum of exponentials of numbers in a list
20. fibonacci_numbers(n: integer) - Return the first n Fibonacci Numbers
Successfully created tools description
Created system prompt...
Starting iteration loop...

--- Iteration 1 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
{"function_name": "show_reasoning", "parameters": ["First, I need to identify the multiples of 5 between 1 and 20. These are 5, 10, 15, and 20. Next, I need to add these multiples together. Finally, I need to find the square root of the sum. This is an arithmetic problem."]}
DEBUG: Calling tool show_reasoning
Iteration_result: ['{"steps": "First, I need to identify the multiples of 5 between 1 and 20. These are 5, 10, 15, and 20. Next, I need to add these multiples together. Finally, I need to find the square root of the sum. This is an arithmetic problem."}']

--- Iteration 2 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
{"function_name": "add_list", "parameters": [[5, 10, 15, 20]] }
DEBUG: Calling tool add_list
Iteration_result: ['50']

--- Iteration 3 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
{"function_name": "verify", "parameters": ["5+10+15+20", "50"]}
DEBUG: Calling tool verify
Iteration_result: ['True']

--- Iteration 4 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
{"function_name": "sqrt", "parameters": [50] }
DEBUG: Calling tool sqrt
Iteration_result: ['7.0710678118654755']

--- Iteration 5 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
{"function_name": "verify", "parameters": ["sqrt(50)", "7.0710678118654755"]}
DEBUG: Calling tool verify
Iteration_result: ['True']

--- Iteration 6 ---
Preparing to generate LLM response...
Starting LLM generation...
LLM generation completed
{"function_name": "FINAL_ANSWER", "parameters": [7.0710678118654755] }

=== Agent Execution Complete ===

```

### 🤝 Contributing
Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request