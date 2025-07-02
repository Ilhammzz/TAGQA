import chainlit as cl
from src.tag.src.init_llm import init_llm
from ui.tag.pipeline import build_tag_chain

# Intent detection langsung di sini
async def detect_intent(question: str) -> str:
    prompt = f"""
    Tolong klasifikasikan pertanyaan berikut:

    "{question}"

    Apakah ini pertanyaan terkait hukum atau bukan? Jawab hanya dengan salah satu:
    - hukum
    - bukan hukum
    """
    llm = init_llm(mode="claude")

    response = await llm.ainvoke(prompt)
    return response.content.strip().lower()

@cl.on_chat_start
async def on_chat_start():
    if not cl.global_state.get("tag_chain"):
        print("[INFO] Build pipeline...")
        tag_chain = build_tag_chain()
        cl.global_state.set("tag_chain", tag_chain)
    else:
        print("[INFO] Load pipeline from cache.")
        tag_chain = cl.global_state.get("tag_chain")

    cl.user_session.set("tag_chain", tag_chain)
    

@cl.on_message
async def on_message(input_msg: cl.Message):
    tag_chain = cl.user_session.get("tag_chain")
    msg = cl.Message(content="")
    history = cl.user_session.get("history", [])

    # Intent detection
    intent = await detect_intent(input_msg.content)

    if intent != "hukum":
        await cl.Message(content="Maaf, saya hanya dapat menjawab pertanyaan yang berkaitan dengan hukum.").send()
        return

    # history_text = ""
    # for h in history:
    #     history_text += f"User: {h['user']}\nBot: {h['bot']}\n"
        
    # pipeline_input = f"{history_text}User: {input_msg.content}\nBot:"
    # if len(pipeline_input) > 4000:
    #         pipeline_input = pipeline_input[-4000:]

    
    # Streaming jawaban bahasa alami
    jawaban = ""
    async for chunk in tag_chain.astream(
        {"input": input_msg.content},
        config=None,  
    ):
        jawaban += chunk
        await msg.stream_token(chunk)

    await msg.send()
    
    history.append({"user": input_msg.content, "bot": jawaban})
    cl.user_session.set("history", history)
