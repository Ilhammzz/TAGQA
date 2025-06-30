from src.tag.src.text2sql_pipeline import generate_sql
from src.tag.src.query_executor import execute_text2sql_response
from src.tag.src.answer_generator import generate_answer
from src.tag.database.db_connection import connect_db
from src.tag.database.schema_loader import load_schema
from langchain.schema.runnable import RunnableLambda
from langchain.schema.output_parser import StrOutputParser
import time

# Koneksi database
conn = connect_db()
schema = load_schema(conn)

def retry_until_success(func, *args, max_delay=60, base_delay=5, **kwargs):
    delay = base_delay
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if "overload" in error_msg or "529" in error_msg:
                print(f"⚠️ Claude overload. Menunggu {delay} detik lalu retry...")
                time.sleep(delay)
                delay = min(delay * 2, max_delay)
            else:
                print(f"❌ Error: {e}")
                raise

def build_tag_chain(llm_model="evaluator"):
    def text2sql_func(inputs):
        question = inputs["input"]
        sql_query = retry_until_success(
            generate_sql,
            schema=schema,
            question=question,
            top_k=100,
            shot_mode="few-shot",
            llm_mode=llm_model
        )
        return {"question": question, "sql_query": sql_query}

    def query_executor_func(inputs):
        sql_query = inputs["sql_query"]
        try:
            rows, columns = execute_text2sql_response(conn, sql_query)
            if not rows:
                rows = [["Data tidak ditemukan."]]
                columns = ["Hasil"]
        except Exception as e:
            print(f"[!] SQL Execution Error: {e}")
            try:
                conn.rollback()
                print("[ℹ️] Database rollback executed.")
            except Exception as rollback_error:
                print(f"[!] Rollback failed: {rollback_error}")
            raise Exception("Gagal mengeksekusi query SQL.")

        return {"question": inputs["question"], "rows": rows, "columns": columns}

    def answer_generator_func(inputs):
        question = inputs["question"]
        rows = inputs["rows"]
        columns = inputs["columns"]

        answer = retry_until_success(
            generate_answer,
            columns,
            rows,
            question,
            llm_mode=llm_model
        )
        return answer

    tag_chain = (
        RunnableLambda(text2sql_func)
        | RunnableLambda(query_executor_func)
        | RunnableLambda(answer_generator_func)
        | StrOutputParser()
    )

    return tag_chain
