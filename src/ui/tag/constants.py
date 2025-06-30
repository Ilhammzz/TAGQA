import chainlit as cl
from chainlit.input_widget import Select

# Native Chainlit Settings
TAG_SETTINGS = [
    Select(
        id="llm_model",
        label="Pilih Model LLM",
        values=["evaluator", "claude", "ollama"],
        initial_index=0
    )
]

# Native Chainlit Starters
TAG_STARTERS = [
    cl.Starter(
        label="Morning routine ideation",
        message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
        icon="/public/idea.svg",
    ),
    cl.Starter(
        label="Explain superconductors",
        message="Explain superconductors like I'm five years old.",
        icon="/public/learn.svg",
    ),
    cl.Starter(
        label="Python script for daily email reports",
        message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up.",
        icon="/public/terminal.svg",
    )
]
TAG_DESC = """
Sistem tanya jawab berbasis Table-Augmented Generation (TAG) untuk menjawab pertanyaan hukum berdasarkan data tabel.
"""
