import asyncio
from google import genai
from google.genai import types
import os
import subprocess
import platform

os_name = platform.system().lower()

# API KEY
client = genai.Client(api_key= os.getenv("GOOGLE_API_KEY"))

# History
history = []

# Tool create karte hai, jo kisi bhi terminal / shell command ko execute kar sakta hai
def execute_command(command:str):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


        if result.stderr:
            return f"Error: {result.stderr}"
        
        return f"Success: {result.stdout}"
    
    except Exception as e:
        return f"Exception: {str(e)}"



execute_command_declaration = {
    "name": "executeCommand",
    "description": "Execute Terminal Command",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "command": {"type": "STRING"}
        },
        "required": ["command"]
    }
}


# 🧰 Tool Map
tools_map = {
    "executeCommand": execute_command,
}

# ➕ Helper to maintain history
def add_message(role, part):
    history.append({
        "role": role,
        "parts": [part]
    })


# 🤖 Agent Logic
async def run_agent(user_input):

    add_message("user", {"text": user_input})

    while True:

        config = types.GenerateContentConfig(
            system_instruction="""
            You are an expert AI agent specializing in automated frontend web development. Your goal is to build a complete, functional frontend for a website based on the user's request. You operate by executing terminal commands one at a time using the 'executeCommand' tool.

            Your user's operating system is: {os_name}

            <-- Core Mission: The PLAN -> EXECUTE -> VALIDATE -> REPEAT loop -->
            You must follow this workflow for every task:
            1. PLAN: Decide on the single, next logical command to execute.
            2. EXECUTE: Call the 'executeCommand' tool with that single command.
            3. VALIDATE: Carefully examine the result from the tool. The result will start with "Success:" or "Error:".
            - If "Success:", check the output (stdout) to confirm the command did what you expected.
            - If "Error:", analyze the error message and fix the problem.
            4. REPEAT until task is fully completed.

            <-- CRITICAL RULES for Writing to Files -->

            IF OS is linux or darwin:
            Use:
            cat << 'EOF' > my-project/index.html
            <!DOCTYPE html>
            <html>
            <head>
            <title>My App</title>
            </head>
            <body>
            <h1>Hello World</h1>
            </body>
            </html>
            EOF


            IF OS is windows:
            Use PowerShell Set-Content:

            @'
            const calculator = {{
                displayValue: '0',
                firstOperand: null,
                waitingForSecondOperand: false,
                operator: null,
            }};
            function updateDisplay() {{
                const display = document.querySelector('.calculator-screen');
                display.value = calculator.displayValue;
            }}
            updateDisplay();
            '@ | Set-Content -Path "my-app\\script.js"

            Note:
            - Use \\ for Windows paths
            - Do NOT use echo for large code

            <-- Standard Plan -->
            1. mkdir project
            2. verify directory
            3. create files (index.html, style.css, script.js)
            4. write HTML
            5. validate HTML
            6. write CSS
            7. validate CSS
            8. write JS
            9. validate JS

            <-- Final Step -->
            Give final summary only. Do not call tools after completion.
            """,
            tools=[{
                "functionDeclarations": [
                
                    execute_command_declaration
                ]
            }]
        )

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=history,
            config=config
        )

        # 🔧 Tool call handling
        # agar ai ne function call diya toh wo yaha handle hoga
        if response.function_calls:

            call = response.function_calls[0]
            name = call.name
            args = call.args

            print(f"🔧 Tool Called: {name} with {args}")

            tool = tools_map[name]

            if asyncio.iscoroutinefunction(tool):
                result = await tool(**args)
            else:
                result = tool(**args)

            # model call history
            # 1....user -> add 2+2
            # 2......toh ai ne mujhe ye call krne bola tha 
            # add_message("model", {
            #     "functionCall": {
            #         "name": name,
            #         "args": args
            #     }
            # })

            # tool response history
            # 3.....or uska result maine nikal liye jo ye hai 
            # history mai 3 chizzey store hongi user input, model function call, tool response
            # Ai ko waps se bejh apan logo ne result taki woh frame krke de 
            add_message("user", {
                "functionResponse": {
                    "name": name,
                    "response": {
                        "result": result
                    }
                }
            })

        # 🧠 Final response
        else:
            print("AI:", response.text)

            add_message("model", {"text": response.text})
            break



# 🔁 Main loop
async def main():
    print("🤖 AI Agent started (type 'exit' to quit)\n")

    while True:
        user_input = input("Ask --> ")

        if user_input.lower() == "exit":
            print("Chat ended")
            break

        await run_agent(user_input)


# 🚀 Run
asyncio.run(main())

