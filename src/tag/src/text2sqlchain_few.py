from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
import os, sys
sys.path.append(os.path.dirname(__file__))
from prompt_config import TAG_INSTRUCTION, PROMPT_SUFFIX_ID

# ======================= INITIALIZE LLM ========================
def init_llm(mode="gemini"):
    if mode == "gemini":
        api_key = os.getenv("GEMINI_API_TOKEN")
        if not api_key:
            raise ValueError("API Key GEMINI tidak ditemukan.")
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.0,
            top_p=1,
            google_api_key=api_key,
            timeout=60
        )
    elif mode == "ollama":
        return ChatOllama(model="llama3.1:8b-instruct-q4_K_M")
    else:
        raise ValueError("Mode LLM tidak dikenali. Gunakan 'gemini' atau 'ollama'.")

# ======================= FEW-SHOT EXAMPLES ========================
examples = [
  {
    "question": "Dalam pembangunan infrastruktur telekomunikasi, bagaimana cara perhitungan persentase TKDN untuk belanja modal atau capital expenditure (Capex) yang digunakan?",
    "answer": """```sql\nSELECT a.article_number, a.text, r.title\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE a.text ILIKE '%TKDN%' OR a.text ILIKE '%belanja modal%' OR a.text ILIKE '%capital expenditure%'\nLIMIT 20\n```"""
  },
  {
    "question": "Apakah Lembaga Penyiaran Asing boleh mendirikan stasiun penyiaran di Indonesia?",
    "answer": """```sql\nSELECT a.article_number, a.text, r.title\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE a.text ILIKE '%Lembaga Penyiaran Asing%' OR a.text ILIKE '%stasiun penyiaran%'\nLIMIT 20;\n```"""
  },
  {
    "question": "Bagaimana cara mendapatkan rekomendasi untuk menyelenggarakan Diklat Radio Elektronika atau Operator Radio (REOR)?",
    "answer": """```sql\nSELECT a.article_number, a.text, r.title\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%Diklat Radio Elektronika%' OR a.text ILIKE '%Operator Radio%' OR a.text ILIKE '%REOR%'\nLIMIT 20;\n```"""
  },
  {
    "question": "Apa itu Jaringan Dokumentasi dan Informasi Hukum (JDIH) Kemkominfo, dan apa tujuannya?",
    "answer": """```sql\nSELECT d.name, d.definition, r.title\nFROM definitions d\nJOIN regulations r ON d.regulation_id = r.id\nWHERE d.name ILIKE '%Jaringan Dokumentasi dan Informasi Hukum%' OR d.name ILIKE '%JDIH%'\nLIMIT 20;\n```"""
  },
  {
    "question": "Jenis alat atau perangkat telekomunikasi apa saja yang wajib memenuhi persyaratan teknis?",
    "answer": """```sql\nSELECT a.article_number, a.text, r.title\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE a.text ILIKE '%perangkat telekomunikasi%' AND a.text ILIKE '%persyaratan teknis%' AND a.text ILIKE '%wajib%'\nLIMIT 20;\n```"""
  },
  {
    "question": "Kenapa pemberian perizinan penggunaan spektrum frekuensi radio harus melalui proses seleksi?",
    "answer": """```sql\nSELECT a.article_number, a.text\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%perizinan spektrum%'\r\n   OR a.text ILIKE '%proses seleksi%'\nLIMIT 20;\n```"""
  },
  {
    "question": "Tindakan apa saja yang dilarang dalam penggunaan Data Pribadi, dan sanksi pidana apa yang dapat dikenakan jika melanggar larangan tersebut?",
    "answer": """```sql\nSELECT a.article_number, a.text\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%data pribadi%'\r\n   AND (a.text ILIKE '%dilarang%' OR a.text ILIKE '%sanksi%' OR a.text ILIKE '%pidana%')\nLIMIT 20;\n```"""
  },
  {
    "question": "Ketika menggunakan layanan internet di rumah, data apa saja yang dicatat oleh penyedia jasa layanan internet (ISP) seperti Telkom atau penyedia lainnya?",
    "answer": """```sql\nSELECT a.article_number, a.text\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%layanan internet%'\r\n   AND (a.text ILIKE '%data dicatat%' OR a.text ILIKE '%ISP%' OR a.text ILIKE '%penyedia layanan internet%');\n```"""
  },
  {
    "question": "Apabila seseorang memanfaatkan jaringan WiFi yang disediakan secara publik, misalnya di kafe atau warnet, apakah data pribadi yang bersangkutan turut terekam oleh penyedia layanan WiFi tersebut?",
    "answer": """```sql\nSELECT a.article_number, a.text\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%WiFi publik%'\r\n   OR a.text ILIKE '%data pribadi%'\r\n   OR a.text ILIKE '%layanan internet publik%'\r\n   OR a.text ILIKE '%rekaman data pengguna%'\nLIMTIT 20;\n```"""
  },
  {
    "question": "Terkait pengamanan jaringan internet. Apa sebenarnya yang ingin diamankan dan ancaman apa saja yang perlu diwaspadai?",
    "answer": """```sql\nSELECT a.article_number, a.text\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%pengamanan jaringan%'\r\n   OR a.text ILIKE '%ancaman keamanan%'\r\n   OR a.text ILIKE '%internet%'\nLIMIT 20;\n```"""
  },
  {
    "question": "Ke daerah mana saja cakupan wilayah Siaran yang diperbolehkan dalam penyelenggaraan Penyiaran?",
    "answer": """```sql\nSELECT a.article_number, a.text\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%wilayah siaran%'\r\n   AND(a.text ILIKE '%jangkauan%' OR a.text ILIKE '%cakupan%')\nLIMIT 20\n```"""
  },
  {
    "question": "Berdasarkan seluruh peraturan teknologi informasi yang ada di database, apa saja daftar seluruh judul subjek yang ada?",
    "answer": """```sql\nSELECT DISTINCT s.subject\nFROM subjects s \nORDER BY s.subject ASC\nLIMIT 20;\n```"""
  },
  {
    "question": "Pasal 19 dalam Peraturan Kominfo Nomor 13 Tahun 2019 saat ini masih berlaku atau sudah dicabut?",
    "answer": """```sql\nSELECT\r\n    a.\"id\",\r\n    a.\"regulation_id\",\r\n    a.\"chapter_number\",\r\n    a.\"chapter_about\",\r\n    a.\"article_number\",\r\n    a.\"text\",\r\n    a.\"status\",\r\n    a.\"title\",\r\n    r.\"title\" AS \"regulation_title\",\r\n    r.\"short_type\",\r\n    r.\"number\",\r\n    r.\"year\"\r\nFROM\r\n    \"articles\" a\r\nJOIN\r\n    \"regulations\" r ON a.\"regulation_id\" = r.\"id\"\r\nWHERE\r\n    r.\"short_type\" = 'PERMENKOMINFO'\r\n    AND r.\"number\" = '13'\r\n    AND r.\"year\" = '2019'\r\n    AND a.\"article_number\" = '19'\nLIMIT 20;\n```"""
  },
  {
    "question": "Berapa total jumlah pasal yang merujuk ke Pasal 57 atau dirujuk oleh Pasal 57 dalam Undang-Undang Nomor 27 Tahun 2022?",
    "answer": """```sql\nSELECT COUNT(DISTINCT \"from_article_id\") AS \"jumlah_pasal_merujuk\"\r\nFROM \"article_relations\"\r\nWHERE \"to_article_id\" IN (SELECT \"id\" FROM \"articles\" WHERE \"article_number\" = '57' AND \"regulation_id\" IN (SELECT \"id\" FROM \"regulations\" WHERE \"number\" = '27' AND \"year\" = '2022'))\r\nUNION ALL\r\nSELECT COUNT(DISTINCT \"to_article_id\") AS \"jumlah_pasal_dirujuk\"\r\nFROM \"article_relations\"\r\nWHERE \"from_article_id\" IN (SELECT \"id\" FROM \"articles\" WHERE \"article_number\" = '57' AND \"regulation_id\" IN (SELECT \"id\" FROM \"regulations\" WHERE \"number\" = '27' AND \"year\" = '2022'))\nLIMIT 20;\n```"""
  },
  {
    "question": "PERMENKOMINFO No. 1 Tahun 2010 Pasal 70 sudah diamandemen berapa kali dan apa isi dari semua pasal amandemennya?",
    "answer": """```sql\nSELECT\r\n  COUNT(DISTINCT ar.\"from_article_id\")\r\nFROM\r\n  \"article_relations\" ar\r\nJOIN\r\n  \"articles\" a ON ar.\"to_article_id\" = a.\"id\"\r\nJOIN\r\n  \"regulations\" r ON a.\"regulation_id\" = r.\"id\"\r\nWHERE\r\n  r.\"short_type\" = 'PERMENKOMINFO'\r\n  AND r.\"number\" = '1'\r\n  AND r.\"year\" = '2010'\r\n  AND a.\"article_number\" = '70'\r\n  AND ar.\"relation_type\" = 'mengubah';\r\nSELECT\r\n  a.\"article_number\",\r\n  a.\"text\",\r\n  r.\"title\"\r\nFROM\r\n  \"article_relations\" ar\r\nJOIN\r\n  \"articles\" a ON ar.\"from_article_id\" = a.\"id\"\r\nJOIN\r\n  \"regulations\" r ON a.\"regulation_id\" = r.\"id\"\r\nWHERE\r\n  ar.\"relation_type\" = 'mengubah'\r\n  AND ar.\"to_article_id\" IN (\r\n    SELECT\r\n      a2.\"id\"\r\n    FROM\r\n      \"articles\" a2\r\n    JOIN\r\n      \"regulations\" r2 ON a2.\"regulation_id\" = r2.\"id\"\r\n    WHERE\r\n      r2.\"short_type\" = 'PERMENKOMINFO'\r\n      AND r2.\"number\" = '1'\r\n      AND r2.\"year\" = '2010'\r\n      AND a2.\"article_number\" = '70'\r\n  )\nLIMIT 20;\n```"""
  },
  {
    "question": "Judul peraturan apa saja (lima) yang memiliki banyak pasal yang sudah tidak efektif atau tidak berlaku?",
    "answer": """```sql\nSELECT\r\n    r.\"title\",\r\n    COUNT(CASE WHEN a.\"status\" = 'ineffective' THEN 1 END) AS \"jumlah_pasal_tidak_efektif\"\r\nFROM\r\n    \"regulations\" r\r\nJOIN\r\n    \"articles\" a ON r.\"id\" = a.\"regulation_id\"\r\nGROUP BY\r\n    r.\"title\"\r\nHAVING\r\n    COUNT(CASE WHEN a.\"status\" = 'ineffective' THEN 1 END) > 0\r\nORDER BY\r\n    \"jumlah_pasal_tidak_efektif\" DESC\r\nLIMIT 5;\n```"""
  },
  {
    "question": "Dari semua peraturan di bidang teknologi informasi di database, sebutkan semua pasal yang isinya membahas mengenai 'tanda tangan elektronik', sebutkan judul pasalnya",
    "answer": """```sql\n SELECT a.article_number, r.title\n FROM articles a\n JOIN regulations r ON a.regulation_id = r.id\n WHERE r.title ILIKE '%transaksi elektronik%'\n AND a.text ILIKE '%tanda tangan elektronik%'\nLIMIT 20;\n```"""
  },
  {
    "question": "Peraturan bidang teknologi informasi apa saja (lima) yang paling banyak di amandemen oleh peraturan lain? Sebutkan judulnya",
    "answer": """```sql\nSELECT r.title, COUNT(rr.id) AS jumlah_amandemen\n FROM regulation_relations rr\n JOIN regulations r ON rr.from_regulation_id = r.id\n WHERE rr.relation_type ILIKE '%mengubah%'\n GROUP BY r.title\n ORDER BY jumlah_amandemen DESC\n LIMIT 5;\n```"""
  },
  {
    "question": "Dari semua peraturan di bidang teknologi informasi di database, sebutkan semua pasal yang isinya membahas mengenai 'tanda tangan elektronik', sebutkan judul pasalnya",
    "answer": """```sql\nSELECT a.article_number, r.title\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE r.title ILIKE '%transaksi elektronik%'\r\n  AND a.text ILIKE '%tanda tangan elektronik%'\nLIMIT 20;\n```"""
  },
  {
    "question": "Peraturan bidang teknologi informasi apa saja (lima) yang paling banyak di amandemen oleh peraturan lain? Sebutkan judulnya",
    "answer": """```sql\nSELECT r.title, COUNT(rr.id) AS jumlah_amandemen\nFROM regulation_relations rr\nJOIN regulations r ON rr.from_regulation_id = r.id\nWHERE rr.relation_type ILIKE '%mengubah%'\nGROUP BY r.title\nORDER BY jumlah_amandemen DESC\nLIMIT 5;\n```"""
  },
  {
    "question": "Apa saja lima judul pasal yang paling banyak merujuk ke pasal lain atau dirujuk oleh pasal lain?",
    "answer": """```sql\nSELECT a."title", COUNT(ar."from_article_id") AS "jumlah_referensi"\n FROM articles a\n JOIN article_relations ar ON a.id = ar.from_article_id\n GROUP BY a."title"\n ORDER BY "jumlah_referensi" DESC\n LIMIT 5;\n```"""
  }
]

# Prompt untuk tiap contoh
example_prompt = PromptTemplate.from_template("Pertanyaan: {question}\n{answer}")

embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# Selector berbasis semantic similarity
example_selector = SemanticSimilarityExampleSelector.from_examples(
    # This is the list of examples available to select from.
    examples,
    # This is the embedding class used to produce embeddings which are used to measure semantic similarity.
    embedding_model,
    # This is the VectorStore class that is used to store the embeddings and do a similarity search over.
    Chroma,
    # This is the number of examples to produce.
    k=2,
)

# ======================= FINAL PROMPT ========================

POSTGRES_PROMPT_FEWSHOT = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix=TAG_INSTRUCTION,
    suffix=PROMPT_SUFFIX_ID,
    input_variables=["input", "table_info", "top_k"]
)

# ======================= SQL CHAIN ========================
def get_sql_chain(llm):
    return LLMChain(llm=llm, prompt=POSTGRES_PROMPT_FEWSHOT)

def generate_sql(schema: str, question: str, top_k: str, llm_mode: str = "gemini") -> str:
    llm = init_llm(llm_mode)
    chain = get_sql_chain(llm)
    inputs = {
        "input": question,
        "table_info": schema,
        "top_k": str(top_k)
    }
    return chain.run(inputs).strip()
