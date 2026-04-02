import asyncio
import httpx
from google import genai
from google.genai import types

# 🔑 API KEY
client = genai.Client(api_key="")

# 🧠 History
history = []

# 🔧 Tools
def sum_tool(num1: float, num2: float):
    return num1 + num2


def prime_tool(num: int):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True


async def get_crypto_price(coin: str):
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin}"
    async with httpx.AsyncClient() as client_http:
        res = await client_http.get(url)
        return res.json()


# 🧾 Tool Declarations

sum_declaration = {
    "name": "sum",
    "description": "Add two numbers",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "num1": {"type": "NUMBER"},
            "num2": {"type": "NUMBER"}
        },
        "required": ["num1", "num2"]
    }
}

prime_declaration = {
    "name": "prime",
    "description": "Check if number is prime",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "num": {"type": "NUMBER"}
        },
        "required": ["num"]
    }
}

crypto_declaration = {
    "name": "getCryptoPrice",
    "description": "Get crypto price in USD",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "coin": {"type": "STRING"}
        },
        "required": ["coin"]
    }
}

# 🧰 Tool Map
tools_map = {
    "sum": sum_tool,
    "prime": prime_tool,
    "getCryptoPrice": get_crypto_price
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
            You are an AI agent.
            You can use tools:
            - sum
            - prime
            - getCryptoPrice
            
            Use tools when needed, otherwise answer normally if you don't need help of these tools.
            """,
            tools=[{
                "functionDeclarations": [
                    sum_declaration,
                    prime_declaration,
                    crypto_declaration
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
            add_message("model", {
                "functionCall": {
                    "name": name,
                    "args": args
                }
            })

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

