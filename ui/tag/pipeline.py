import time
from langchain.schema.runnable import RunnableLambda
from langchain.schema.output_parser import StrOutputParser
from src.tag.src.text2sql_pipeline import generate_sql
from src.tag.src.query_executor import execute_text2sql_response
from src.tag.src.answer_generator import generate_answer
from src.tag.database.db_connection import connect_db
from src.tag.database.schema_loader import load_schema

# Inisialisasi database dan schema
conn = connect_db()
schema = load_schema(conn)

def retry_until_success(func, *args, max_delay=60, base_delay=5, **kwargs):
    """
    Melakukan retry berulang dengan backoff jika error Claude overload (kode 529).
    """
    delay = base_delay
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if "overload" in error_msg or "529" in error_msg:
                print(f"⚠️ Claude overload. Menunggu {delay} detik lalu retry...")
                time.sleep(delay)
                delay = min(delay * 2, max_delay)  # backoff maksimal 60 detik
            else:
                print(f"❌ Error bukan overload: {e}")
                raise  # error lain (misal bug prompt) tetap dilempar
            
def text2sql_func(inputs):
    question = inputs["input"]  # Input dari user
    sql_query = retry_until_success(generate_sql, schema=schema, question=question, top_k=100, shot_mode="few-shot", llm_mode="claude")
    return {"input": question, "sql_query": sql_query}

def query_executor_func(inputs):
    sql_query = inputs["sql_query"]
    
    try:
        rows, columns = execute_text2sql_response(conn, sql_query)
        rows = rows[:30]  # Batasi hasil maksimal 30 baris

        if not rows:
            return {"input": inputs["input"], "rows": [["data tidak ditemukan"]], "columns": ["Hasil"]}
        else:
            return {"input": inputs["input"], "rows": rows, "columns": columns}

    except Exception as e:
        print(f"[!] Error executing SQL: {sql_query}")
        print(f"[!] Exception: {e}")
        try:
            conn.rollback()
            print("[ℹ️] Database rollback executed.")
        except Exception as rollback_error:
            print(f"[!] Rollback failed: {rollback_error}")

        # Kembalikan hasil fallback
        return {"input": inputs["input"], "rows": [["error executing query"]], "columns": ["Error"]}
    
    # rows, columns = execute_text2sql_response(conn, sql_query)
    # return {"input": inputs["input"], "rows": rows, "columns": columns}

def answer_generator_func(inputs):
    question = inputs["input"]
    rows = inputs["rows"]
    columns = inputs["columns"]
    answer = retry_until_success(generate_answer, columns, rows, question, llm_mode="claude")
    return answer

def build_tag_chain():
    tag_chain = (
        RunnableLambda(text2sql_func)
        | RunnableLambda(query_executor_func)
        | RunnableLambda(answer_generator_func)
        | StrOutputParser()
    )
    return tag_chain
