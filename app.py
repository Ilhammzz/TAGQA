"""Chainlit app: `chainlit run app.py`"""

import chainlit as cl
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
# from src.ui import (
#     GRAPH_RAG_DESC,
#     GRAPH_RAG_SETTINGS,
#     GRAPH_RAG_STARTERS,
#     configure_graph_rag,
#     graph_rag_on_message,
#     initialize_graph_rag,
# )
from ui.tag import (
    TAG_DESC,
    TAG_SETTINGS,
    TAG_STARTERS,
    build_tag_chain,
    on_message as tag_on_message
)


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Graph-RAG",
            markdown_description="Modul Graph-RAG sedang dalam pengembangan.",
            icon="https://picsum.photos/200",
            starters=[
                cl.Starter(
                    label="Coming Soon",
                    message="Fitur Graph-RAG sedang dikembangkan."
                )
            ],
        ),
        cl.ChatProfile(
            name="TAG",
            markdown_description=TAG_DESC,
            icon="https://picsum.photos/250",
            starters=TAG_STARTERS,
            default=True,
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")

    if chat_profile == "Graph-RAG":
        if not cl.user_session.get("is_graph_rag_initialized", False):
            neo4j_graph, embedder_model = initialize_graph_rag()

            cl.user_session.set("neo4j_graph", neo4j_graph)
            cl.user_session.set("embedder_model", embedder_model)
            cl.user_session.set("is_graph_rag_initialized", True)

        settings = await cl.ChatSettings(GRAPH_RAG_SETTINGS).send()

        llm, graph_workflow, graph_visualizer_tool = configure_graph_rag(
            llm_name=settings["llm_model"],
            neo4j_graph=cl.user_session.get("neo4j_graph"),
            embedder_model=cl.user_session.get("embedder_model"),
        )

        cl.user_session.set("llm", llm)
        cl.user_session.set("graph_workflow", graph_workflow)
        cl.user_session.set("graph_visualizer_tool", graph_visualizer_tool)

    elif chat_profile == "TAG":
        settings = await cl.ChatSettings(TAG_SETTINGS).send()
        tag_chain = build_tag_chain()
        cl.user_session.set("tag_chain", tag_chain)
        # cl.user_session.set("tag_llm_model", settings["llm_model"])


@cl.on_settings_update
async def setup_agent(settings):
    chat_profile = cl.user_session.get("chat_profile")

    if chat_profile == "Graph-RAG":
        llm, graph_workflow, graph_visualizer_tool = configure_graph_rag(
            llm_name=settings["llm_model"],
            neo4j_graph=cl.user_session.get("neo4j_graph"),
            embedder_model=cl.user_session.get("embedder_model"),
        )

        cl.user_session.set("llm", llm)
        cl.user_session.set("graph_workflow", graph_workflow)
        cl.user_session.set("graph_visualizer_tool", graph_visualizer_tool)

    elif chat_profile == "TAG":
        tag_chain = build_tag_chain(settings["llm_model"])
        cl.user_session.set("tag_chain", tag_chain)
        cl.user_session.set("tag_llm_model", settings["llm_model"])


@cl.on_message
async def on_message(input_msg: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    config = {"configurable": {"thread_id": cl.context.session.id}}

    if chat_profile == "Graph-RAG":
        graph_workflow = cl.user_session.get("graph_workflow")
        graph_visualizer_tool = cl.user_session.get("graph_visualizer_tool")

        await graph_rag_on_message(
            workflow=graph_workflow,
            graph_visualizer_tool=graph_visualizer_tool,
            input_msg=input_msg,
            config=config,
        )

    elif chat_profile == "TAG":
        await tag_on_message(input_msg)


if __name__ == "__main__":
    load_dotenv(".env")
