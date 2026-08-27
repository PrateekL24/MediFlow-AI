from backend.core.llm import llm

response = llm.invoke("Reply with exactly: Hello")

print(response.content[0]["text"])