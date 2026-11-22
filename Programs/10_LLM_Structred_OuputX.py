from ollama import chat
import json

# Prompt for LLM
prompt = """Give me the information about Python programming language.
Return the result as JSON with these keys:
language
type
creator
"""

# Execute LLM
response = chat(
    model = "llama3.2:1b",
    messages = [
        {
        "role" : "user",
        "content" : prompt
        }
    ],
    format = "json"
)

answer = response.message.content

print("LLM Response")
print(answer)

# Convert JSON string to Python dictonary
data = json.loads(answer)

print("Data from dictonary is : ",data)

print("Data from Dictonary")

print("Language : ",data.get("language"))
print("Type : ",data.get("type"))
print("Creator : ",data.get("creator"))

