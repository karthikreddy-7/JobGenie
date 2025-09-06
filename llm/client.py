from ollama import chat

prompt="""
Hi
"""
stream = chat(
    model='gemma3:1b',
    #model='gemma3:270m',
    messages=[{'role': 'user', 'content':prompt}],
    stream=True,
)
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)