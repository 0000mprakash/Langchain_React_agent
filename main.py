# from openai import OpenAI
# from openai import AzureOpenAI
# from dotenv import load_dotenv
import os

# load_dotenv()

from dotenv import load_dotenv
load_dotenv()

# response = client.responses.create(
#     model="gpt-4o-mini",
#     input = "Hello World"
# )

# print(response.output[0].content[0].text)


from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("azure_endpoint"),   # e.g. https://xxx.openai.azure.com/
    azure_deployment="gpt-4o-mini",    # e.g. https://xxx.openai.azure.com/
)


response = client.chat.completions.create(
    model="gpt-4o-mini",       # deployment name, not model name
    messages=[
        {"role": "user", "content": "hello world"}
    ]
)

print(response.choices[0].message.content)
