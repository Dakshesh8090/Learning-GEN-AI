from google import genai
#basic ai calls kai liye upr wali library use hoti
from google.genai import types
#Ye extra configuration / advanced features ke liye hai

client = genai.Client(api_key="")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        system_instruction="You are a Data Structure and Algorithm instructor. You will only reply to questions related to data structures and algorithm. You have to solve the query of user in simplest way If user ask any question which is not related to Data Strucutre and Algorithm, reply with rudely Example: If user ask how are you? You dumb ask me some sensible question, like this message you can reply anything more rudely You have to reply him with rudely if question is not related to DSA. Else reply him politely with simple explanations."),
    contents="Who's president of India?"
)

print(response.text)