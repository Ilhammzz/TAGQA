import os, sys
sys.path.append(os.path.dirname(__file__))
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from init_llm import init_llm
from prompt_config import ANSWER_GENERATOR_INSTRUCTION

load_dotenv()


# ===================== FEW SHOT EXAMPLES =====================
few_shot_examples = """
Contoh 1:
Kolom-kolom: article_number, content
Data: [('3', 'Setiap orang dilarang melakukan akses tanpa hak terhadap sistem elektronik milik orang lain.')]

Pertanyaan: Apa isi dari Pasal 3?
Jawaban: Setiap orang dilarang melakukan akses tanpa hak terhadap sistem elektronik milik orang lain.
Referensi: Pasal 3 - Setiap orang dilarang melakukan akses tanpa hak terhadap sistem elektronik milik orang lain.

Contoh 2:
Kolom-kolom: name, definition
Data: [('Tanda Tangan Elektronik', 'Tanda Tangan Elektronik adalah tanda tangan yang terdiri atas Informasi Elektronik yang dilekatkan...')]

Pertanyaan: Apa itu Tanda Tangan Elektronik?
Jawaban: Tanda Tangan Elektronik adalah tanda tangan yang terdiri atas Informasi Elektronik yang dilekatkan pada Informasi Elektronik lainnya sebagai alat verifikasi dan autentikasi.
Referensi: Definisi Tanda Tangan Elektronik
"""


# Prompt zero-shot (tanpa contoh)
answer_prompt_zero = PromptTemplate(
    input_variables=["columns", "rows", "question"],
    template=ANSWER_GENERATOR_INSTRUCTION.replace("{few_shot_section}", "")
)

# Prompt few-shot (pakai contoh)
answer_prompt_few = PromptTemplate(
    input_variables=["columns", "rows", "question"],
    template=ANSWER_GENERATOR_INSTRUCTION.replace("{few_shot_section}", few_shot_examples)
)


def get_sql_chain(llm, mode="zero-shot"):
    prompt = answer_prompt_few if mode == "few-shot" else answer_prompt_zero
    return LLMChain(llm=llm, prompt=prompt)


# ===================== MAIN FUNCTION =====================
def generate_answer(columns, rows, question, mode: str = "few-shot", llm_mode: str = "gemini"):
    """
    Mengubah hasil query menjadi jawaban bahasa alami berdasarkan pertanyaan awal.
    Pilih LLM via llm_mode: "gemini" atau "ollama"
    Pilih prompt mode: "zero-shot" atau "few-shot"
    """
    rows_text = "\n".join([str(row) for row in rows])
    columns_text = ", ".join(columns)

    llm = init_llm(llm_mode)
    chain = get_sql_chain(llm, mode=mode)

    return chain.run(columns=columns_text, rows=rows_text, question=question).strip()
