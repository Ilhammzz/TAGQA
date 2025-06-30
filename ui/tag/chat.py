import chainlit as cl
import os
from src.ui.tag.constants import TAG_SETTINGS, TAG_DESC, TAG_STARTERS
from src.ui.tag.prepare import build_tag_chain
from src.ui.tag.chat import save_table_visualization
from langchain.schema.runnable import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

# Deteksi apakah input termasuk pertanyaan hukum (keyword simple)
api_key = os.getenv("GEMINI_API_TOKEN")
llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.0,
            google_api_key=api_key,
            timeout=None
            )

async def detect_intent(question: str) -> str:
    prompt = f"""
    Tolong klasifikasikan pertanyaan berikut:
    
    "{question}"
    
    Apakah ini pertanyaan terkait hukum atau bukan? Jawab hanya dengan salah satu:
    - hukum
    - bukan hukum
    """
    response = await llm.ainvoke(prompt)
    return response.content.strip().lower()

@cl.on_chat_start
async def on_chat_start():
    settings = await cl.ChatSettings(TAG_SETTINGS).send()

    tag_chain = build_tag_chain(settings["llm_model"])

    cl.user_session.set("tag_chain", tag_chain)
    cl.user_session.set("tag_llm_model", settings["llm_model"])

@cl.on_settings_update
async def on_settings_update(settings):
    tag_chain = build_tag_chain(settings["llm_model"])
    cl.user_session.set("tag_chain", tag_chain)
    cl.user_session.set("tag_llm_model", settings["llm_model"])

@cl.on_message
async def on_message(input_msg: cl.Message):
    tag_chain = cl.user_session.get("tag_chain")
    msg = cl.Message(content="")

    # Lakukan intent detection
    intent = await detect_intent(input_msg.content)

    if intent != "hukum":
        await cl.Message(content="Maaf, saya hanya dapat menjawab pertanyaan yang berkaitan dengan hukum.").send()
        return

    # Proses normal jika pertanyaan hukum
    async for chunk in tag_chain.astream(
        {"input": input_msg.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
    # Simpan hasil visualisasi tabel (opsional, kalau kamu mau tampilkan tabelnya)
    # Simulasi data untuk visualisasi: kamu bisa ambil real data dari chain state kalau mau
    # Ini contoh sederhana
    sample_rows = [["Data tidak ditemukan."]]  # Ganti dengan hasil query kalau sudah di-trace
    sample_columns = ["Hasil"]

    # Buat dan tampilkan visualisasi tabel
    file_path = save_table_visualization(sample_rows, sample_columns)
    element = cl.CustomElement(name="TableViz", props={"src": file_path})

    await cl.Message(content="Hasil Tabel:", elements=[element]).send()
