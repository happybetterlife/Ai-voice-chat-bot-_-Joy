from openai import OpenAI
class ChatLLM:
    def __init__(self, api_key: str, model='gpt-4o-mini'):
        self.client = OpenAI(api_key=api_key); self.model=model
    def complete(self, messages, max_tokens=300):
        r = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.6, max_tokens=max_tokens, stream=False)
        return r.choices[0].message.content.strip()
