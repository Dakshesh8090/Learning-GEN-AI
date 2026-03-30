from google import genai

# yaha hum interact kr rhe hau ai se
client = genai.Client(api_key="")  

#yha na mai chat history create kr rha huun sab iske andar save ho rhi hai 
chat = client.chats.create(model="gemini-3-flash-preview")

while True:
    # User input le rha huun yha se
    userInput = input("Ask me anything:")

    if userInput.lower() == "exit":
        print("chat ended")
        break

# ye maine msg bejh diya with context history
    response = chat.send_message(userInput)

    #ye maine print krwa liya
    print(response.text)


