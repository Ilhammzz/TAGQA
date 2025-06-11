from langchain.chains import LLMChain
import os, sys
sys.path.append(os.path.dirname(__file__))
from text2sqlchain_zero import POSTGRES_PROMPT_ZERO, init_llm
from text2sqlchain_few import get_prompt_by_intent, build_selectors_by_intent, detect_intent
from prompt_config import TAG_INSTRUCTION, PROMPT_SUFFIX_ID


selectors = build_selectors_by_intent()

def generate_sql(schema: str, question: str, top_k: str, shot_mode: str = "zero-shot", llm_mode: str = "gemini") -> str:
    llm = init_llm(llm_mode)

    if shot_mode == "few-shot":
        intent = detect_intent(question)
        prompt = get_prompt_by_intent(intent, selectors)
    elif shot_mode == "zero-shot":
        prompt = POSTGRES_PROMPT_ZERO
    else:
        raise ValueError("shot_mode harus 'zero-shot' atau 'few-shot'")

    chain = LLMChain(llm=llm, prompt=prompt)

    inputs = {
        "input": question,
        "table_info": schema,
        "top_k": str(top_k)
    }

    return chain.run(inputs).strip()


