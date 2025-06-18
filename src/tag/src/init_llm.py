import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from google.colab import userdata

def init_llm(mode: str = "gemini"):
    if mode == "gemini":
        api_key = os.getenv("GEMINI_API_TOKEN")
        if not api_key:
            raise ValueError("API Key GEMINI tidak ditemukan.")
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.0,
            top_p=1,
            google_api_key=api_key,
            timeout=60
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
        raise ValueError("Mode LLM tidak dikenali. Gunakan 'gemini' atau 'ollama'.")
