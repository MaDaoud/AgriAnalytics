from openai import OpenAI

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
)

def ask_chatbot(prompt, model="gpt-4o-mini", temperature=0.7, max_tokens=500):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Tu es un assistant utile et clair."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content
