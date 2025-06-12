import os
from openai import AzureOpenAI

# Initialize the client
client = AzureOpenAI(
    api_key="65aaa9f6d52e77f1",  
    azure_endpoint="https://mavericks-secureapi.azurewebsites.net/api/azureai",
    api_version="2024-02-01"
)

# Call chat completion to get info about Hexaware
try:
    response = client.chat.completions.create(
        model="gpt-4o",  # Ensure this is the correct deployment name
        messages=[
            {"role": "system", "content": "You are an AI assistant providing detailed and up-to-date company information."},
            {"role": "user", "content": "Tell me about Hexaware. Include its business domains, services, global presence, and any recent highlights."}
        ],
        temperature=0.5,
        max_tokens=500
    )
    print("Hexaware Info:\n", response.choices[0].message.content)
except Exception as e:
    print(f"Error: {str(e)}")