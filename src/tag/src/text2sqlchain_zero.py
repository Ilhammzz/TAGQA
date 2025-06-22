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


prompt = POSTGRES_PROMPT_ZERO


# ============================ GENERATE SQL ============================
def generate_sql(schema: str, question: str, top_k: int = 100, llm_mode: str = "claude") -> str:
    """
    Generate SQL query dari pertanyaan pengguna.

    Args:
        schema (str): Informasi struktur tabel.
        question (str): Pertanyaan hukum dari user.
        top_k (int): Batas maksimum hasil.
        llm_mode (str): 'claude' atau 'ollama'
    """
    llm = init_llm(llm_mode)

    inputs = {
        "input": question,
        "table_info": schema,
        "top_k": top_k
    }
    
    chain = prompt | llm
    result = chain.invoke(inputs)
    if hasattr(result, "content"):
        return result.content.strip()
    else:
        return str(result).strip()