from google import genai
from google.genai import types


client = genai.Client(api_key="")  

# all config yaha pe ho rha hai  
chat = client.chats.create(model="gemini-3-flash-preview",
        config=types.GenerateContentConfig(
        system_instruction="you can give context here"))

while True:
    # User input le rha huun yha se
    userInput = input("Ask me anything: ")

    if userInput.lower() == "exit":
        print("chat ended")
        break


# ye maine msg bejh diya with context history
    response = chat.send_message(userInput)

    #ye maine print krwa liya
    print(response.text)