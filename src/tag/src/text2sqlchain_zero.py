import os, sys
sys.path.append(os.path.dirname(__file__))
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from init_llm import init_llm
from prompt_config import TAG_INSTRUCTION, PROMPT_SUFFIX_ID

# Zero-shot prompt
POSTGRES_PROMPT_ZERO = PromptTemplate(
    input_variables=["input", "table_info", "top_k"],
    template=TAG_INSTRUCTION + PROMPT_SUFFIX_ID,
)


def get_sql_chain(llm):
    return LLMChain(llm=llm, prompt=POSTGRES_PROMPT_ZERO)


# ============================ GENERATE SQL ============================
def generate_sql(schema: str, question: str, top_k: int = 100, llm_mode: str = "gemini") -> str:
    """
    Generate SQL query dari pertanyaan pengguna.

    Args:
        schema (str): Informasi struktur tabel.
        question (str): Pertanyaan hukum dari user.
        top_k (int): Batas maksimum hasil.
        llm_mode (str): 'gemini' atau 'ollama'
    """
    llm = init_llm(llm_mode)
    chain = get_sql_chain(llm)
    inputs = {
        "input": question,
        "table_info": schema,
        "top_k": top_k
    }
    return chain.run(inputs).strip()