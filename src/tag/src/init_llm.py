import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from google.colab import userdata

def init_llm(mode: str = "claude"):
    if mode == "claude":
        api_key = os.getenv("CLAUDE_API_TOKEN")
        if not api_key:
            raise ValueError("API Key tidak ditemukan.")
        return ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0.0,
            max_tokens_to_sample=4096,
            api_key=api_key,
            timeout=None
        )
    elif mode == "evaluator":
        api_key = userdata.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API Key untuk evaluator tidak ditemukan.")
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.0,
            google_api_key=api_key,
            timeout=None
        )
    elif mode == "ollama":
        return ChatOllama(model="llama3.1:8b-instruct-q4_K_M")
    else:
        raise ValueError("Mode LLM tidak dikenali. Gunakan 'claude' atau 'ollama'.")
