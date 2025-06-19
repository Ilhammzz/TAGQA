from langchain_core.prompts import FewShotPromptTemplate
from langchain.chains import LLMChain
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from collections import defaultdict
import os, sys
sys.path.append(os.path.dirname(__file__))
from prompt_config import TAG_INSTRUCTION, PROMPT_SUFFIX_ID, example_prompt

      
# ======================= EMBEDDING MODEL ========================
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# ======================= INTENT DETECTION ========================
def detect_intent(question: str) -> str:
    q = question.lower()
    if any(x in q for x in ["apa itu", "apa definisi", "yang dimaksud dengan"]):
        return "definition"
    elif any(x in q for x in ["pasal", "kewajiban", "sanksi", "hak", "larangan"]):
        return "article"
    elif "judul peraturan" in q or "nama peraturan" in q:
        return "regulation"
    elif any(x in q for x in ["tahun", "terbit", "kapan"]):
        return "date"
    elif any(x in q for x in ["mengubah", "diubah", "diamandemen"]):
        return "regulation_relations"
    elif "merujuk" in q or "dirujuk" in q:
        return "article_relations"
    else:
        return "general"
      
# ======================= FEW-SHOT EXAMPLES ========================
examples = [
  {
    "question": "Dalam pembangunan infrastruktur telekomunikasi, bagaimana cara perhitungan persentase TKDN untuk belanja modal atau capital expenditure (Capex) yang digunakan?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE a.text ILIKE '%TKDN%' OR a.text ILIKE '%belanja modal%' OR a.text ILIKE '%capital expenditure%';\n``` \"\"\""
  },
  {
    "question": "Apakah Lembaga Penyiaran Asing boleh mendirikan stasiun penyiaran di Indonesia?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE a.text ILIKE '%Lembaga Penyiaran Asing%' OR a.text ILIKE '%stasiun penyiaran%';\n``` \"\"\""
  },
  {
    "question": "Bagaimana cara mendapatkan rekomendasi untuk menyelenggarakan Diklat Radio Elektronika atau Operator Radio (REOR)?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%Diklat Radio Elektronika%' OR a.text ILIKE '%Operator Radio%' OR a.text ILIKE '%REOR%';\n``` \"\"\""
  },
  {
    "question": "Apa itu Jaringan Dokumentasi dan Informasi Hukum (JDIH) Kemkominfo, dan apa tujuannya?",
    "answer": "\"\"\" ```sql\nSELECT d.name, d.definition, r.title\nFROM definitions d\nJOIN regulations r ON d.regulation_id = r.id\nWHERE d.name ILIKE '%Jaringan Dokumentasi dan Informasi Hukum%' OR d.name ILIKE '%JDIH%';\n``` \"\"\""
  },
  {
    "question": "Bagaimana proses pendaftaran Nama Domain dilakukan, dan apa prinsip yang digunakan?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%pendaftaran nama domain%' \r\n  AND a.text ILIKE '%prinsip%';\n``` \"\"\""
  },
  {
    "question": "Apa persyaratan teknis yang harus dipenuhi oleh pembaca kartu cerdas nirkontak?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%persyaratan teknis%'\r\n\tAND a.text ILIKE '%pembaca kartu cerdas nirkontak%';\n``` \"\"\""
  },
  {
    "question": "Apa yang dimaksud dengan alat dan perangkat telekomunikasi jarak dekat (short range devices), dan mengapa persyaratan teknisnya perlu diatur?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE a.text ILIKE '%alat dan perangkat telekomunikasi jarak dekat%'\n AND a.text ILIKE '%persyaratan%';\n``` \"\"\""
  },
  {
    "question": "Apa sanksi yang akan diberikan jika ada pihak yang melanggar ketentuan dalam peraturan Nomor Panggilan Darurat, misalnya memberikan informasi yang tidak benar saat melakukan panggilan ke Pusat Panggilan Darurat?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE r.title ILIKE '%panggilan darurat%'\r\n  AND (a.text ILIKE '%sanksi%' OR a.text ILIKE '%pelanggaran%' OR a.text ILIKE '%informasi tidak benar%');\n``` \"\"\""
  },
  {
    "question": "Apa yang dimaksud dengan pemetaan urusan pemerintahan daerah di bidang komunikasi dan informatika dan mengapa hal ini penting?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%urusan pemerintahan daerah%'\r\n  AND( a.text ILIKE '%pemetaan%'\r\n  OR a.text ILIKE '%komunikasi dan informatika%');\n``` \"\"\""
  },
  {
    "question": "Apa saja tugas dan fungsi Dinas Komunikasi dan Informatika Provinsi dan Kabupaten atau Kota?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE a.text ILIKE '%tugas%'\r\n AND a.text ILIKE '%fungsi%'\r\n AND a.text ILIKE '%dinas komunikasi dan informatika%' AND (a.text ILIKE '%kabupaten%' OR a.text ILIKE '%kota%');\n``` \"\"\""
  },
  {
    "question": "Apakah ada peraturan yang menjelaskan bahwa Penyelenggara Jasa Telekomunikasi wajib melakukan sosialisasi skema tarif yang jelas kepada pengguna atau pelanggan?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text, r.title\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE a.text ILIKE '%penyelenggara jasa telekomunikasi%' \n        AND a.text ILIKE '%sosialisasi%'\n        AND a.text ILIKE '%wajib%'\n        AND a.text ILIKE '%tarif%'\n        AND (a.text ILIKE '%user%' OR a.text ILIKE '%pengguna%' OR a.text ILIKE '%pelanggan%')\n``` \"\"\""
  },
  {
    "question": "Apakah registrasi kartu SIM (Nomor MSISDN) merupakan suatu kewajiban bagi pelanggan jasa telekomunikasi, dan apa konsekuensi hukum apabila kewajiban tersebut tidak dipenuhi?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE a.text ILIKE '%registrasi kartu SIM%'\n   OR a.text ILIKE '%registrasi pelanggan%'\n   OR a.text ILIKE '%kewajiban pelanggan%'\n   OR a.text ILIKE '%nomor MSISDN%'\n   OR a.text ILIKE '%konsekuensi hukum%';\n``` \"\"\""
  },
  {
    "question": "Apa judul dari Peraturan Pemerintah (PP) Nomor 80 Tahun 2019?",
    "answer": "\"\"\" ```sql\nSELECT r.title, r.id\nFROM regulations r\nWHERE \nr.short_type = 'PP' AND \nr.number = '80' AND \nr.YEAR = '2019';\n``` \"\"\""
  },
  {
    "question": "Apa isi Pasal 2 Peraturan Pemerintah (PP) Nomor 80 Tahun 2019?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text\r\nFROM articles a\r\nJOIN regulations r ON a.regulation_id = r.id\r\nWHERE \r\nr.short_type = 'PP' AND \r\nr.number = '80' AND \r\nr.YEAR = '2019' AND \r\na.article_number = '2';\n``` \"\"\""
  },
  {
    "question": "Apa isi Pasal 10 Peraturan Menteri Komunikasi dan Informatika (PERMENKOMINFO) Nomor 4 Tahun 2016?",
    "answer": "\"\"\" ```sql\nSELECT a.article_number, a.text\nFROM articles a\nJOIN regulations r ON a.regulation_id = r.id\nWHERE \nr.short_type = 'PERMENKOMINFO' AND \nr.number = '4' AND \nr.YEAR = '2016' AND \na.article_number = '10';\n``` \"\"\""
  },
  {
    "question": "Berdasarkan seluruh peraturan teknologi informasi yang ada di database, apa saja daftar seluruh judul subjek yang ada?",
    "answer": "\"\"\" ```sql\nSELECT DISTINCT s.subject\nFROM subjects s \nORDER BY s.subject ASC;\n``` \"\"\""
  },
  {
    "question": "Apa judul pasal selanjutnya setelah Pasal 39 UU Nomor 11 Tahun 2008?",
    "answer": "\"\"\" ```sql\nSELECT a2.title, a2.status \nFROM articles a1\nJOIN regulations r ON a1.regulation_id = r.id\nJOIN article_relations ar ON a1.id = ar.from_article_id\nJOIN articles a2 ON ar.to_article_id = a2.id\nWHERE r.short_type = 'UU' and r.\"number\" = '11' and r.\"year\" = 2008\n  AND a1.article_number = '39'\n  AND ar.relation_type = 'berikutnya';\n``` \"\"\""
  },
  {
    "question": "Apa urutan judul peraturan amandemen yang terjadi pada Peraturan Menteri Komunikasi dan Informatika Nomor 26 Tahun 2007?",
    "answer": "\"\"\" ```sql\nSELECT r.\"title\"\r\nFROM regulations r\r\nJOIN regulation_relations rr ON r.\"id\" = rr.\"to_regulation_id\"\r\nWHERE rr.\"relation_type\" = 'mengubah'\r\nAND rr.\"from_regulation_id\" IN (SELECT id FROM regulations WHERE \"short_type\" = 'PERMENKOMINFO' AND \"number\" = '26' AND \"year\" = '2007')\n``` \"\"\""
  },
  {
    "question": "Pasal 19 dalam Peraturan Kominfo Nomor 13 Tahun 2019 saat ini masih berlaku atau sudah dicabut?",
    "answer": "\"\"\" ```sql\nSELECT\r\n    a.\"id\",\r\n    a.\"regulation_id\",\r\n    a.\"chapter_number\",\r\n    a.\"chapter_about\",\r\n    a.\"article_number\",\r\n    a.\"text\",\r\n    a.\"status\",\r\n    a.\"title\",\r\n    r.\"title\" AS \"regulation_title\",\r\n    r.\"short_type\",\r\n    r.\"number\",\r\n    r.\"year\"\r\nFROM\r\n    \"articles\" a\r\nJOIN\r\n    \"regulations\" r ON a.\"regulation_id\" = r.\"id\"\r\nWHERE\r\n    r.\"short_type\" = 'PERMENKOMINFO'\r\n    AND r.\"number\" = '13'\r\n    AND r.\"year\" = '2019'\r\n    AND a.\"article_number\" = '19'\n``` \"\"\""
  },
  {
    "question": "Apa judul Peraturan Pemerintah (PP) yang dikeluarkan pada tahun 2019 yang terkait dengan subjek Telekomunikasi, Informatika, Siber, dan Internet?",
    "answer": "\"\"\" ```sql\nSELECT r.title FROM regulations r \r\nWHERE\r\nr.short_type = 'PP' AND\r\nr.YEAR = '2019';\n``` \"\"\""
  },
  {
    "question": "Pasal nomor berapa saja dari PERMENKOMINFO Nomor 26 Tahun 2007 yang sudah tidak berlaku?",
    "answer": "\"\"\" ```sql\nSELECT\n    a.\"article_number\",\n    a.\"title\",\n    a.\"status\",\n    r.\"title\" AS \"regulation_title\",\n    r.\"short_type\",\n    r.\"number\",\n    r.\"year\"\nFROM\n    \"articles\" a\nJOIN\n    \"regulations\" r ON a.\"regulation_id\" = r.\"id\"\nWHERE\n    r.\"short_type\" = 'PERMENKOMINFO'\n    AND r.\"number\" = '26'\n    AND r.\"year\" = '2007'\n    AND a.\"status\" = 'ineffective'\n``` \"\"\""
  },
  {
    "question": "Pasal nomor berapa saja dari UU Nomor 11 Tahun 2008 yang sudah tidak berlaku?",
    "answer": "\"\"\" ```sql\nSELECT\r\n    a.\"article_number\",\r\n    a.\"title\",\r\n    a.\"status\",\r\n    r.\"title\" AS \"regulation_title\",\r\n    r.\"number\" AS \"regulation_number\",\r\n    r.\"year\" AS \"regulation_year\"\r\nFROM\r\n    \"articles\" a\r\nJOIN\r\n    \"regulations\" r ON a.\"regulation_id\" = r.\"id\"\r\nWHERE\r\n    r.\"short_type\" = 'UU'\r\n    AND r.\"number\" = '11'\r\n    AND r.\"year\" = '2008'\r\n    AND a.\"status\" = 'ineffective'\n``` \"\"\""
  },
  {
    "question": "Berapa total jumlah pasal yang merujuk ke Pasal 57 atau dirujuk oleh Pasal 57 dalam Undang-Undang Nomor 27 Tahun 2022?",
    "answer": "\"\"\" ```sql\nSELECT COUNT(DISTINCT \"from_article_id\") AS \"jumlah_pasal_merujuk\"\r\nFROM \"article_relations\"\r\nWHERE \"to_article_id\" IN (SELECT \"id\" FROM \"articles\" WHERE \"article_number\" = '57' AND \"regulation_id\" IN (SELECT \"id\" FROM \"regulations\" WHERE \"number\" = '27' AND \"year\" = '2022'))\r\nUNION ALL\r\nSELECT COUNT(DISTINCT \"to_article_id\") AS \"jumlah_pasal_dirujuk\"\r\nFROM \"article_relations\"\r\nWHERE \"from_article_id\" IN (SELECT \"id\" FROM \"articles\" WHERE \"article_number\" = '57' AND \"regulation_id\" IN (SELECT \"id\" FROM \"regulations\" WHERE \"number\" = '27' AND \"year\" = '2022'))\n``` \"\"\""
  },
  {
    "question": "Kapan (tanggal) Pasal 40 UU Nomor 11 Tahun 2008 terakhir kali diamandemen?",
    "answer": "\"\"\" ```sql\select rfrom.issue_date\n from article_relations ar join articles afrom on ar.from_article_id = afrom.id join articles ato on ar.to_article_id = ato.id\n join regulations rfrom on afrom.regulation_id = rfrom.id join regulations rto on ato.regulation_id = rto.id\n where rto.short_type = 'UU' and rto.number = '11' and rto.year = 2008\n and ar.relation_type ilike '%mengubah%' and ato.article_number = '40'\n order by rfrom.issue_date desc \n limit 1;\n``` \"\"\""
  },
  {
    "question": "Pasal mana saja yang diamandemen oleh UU No. 19 Tahun 2016?",
    "answer": " ```sql\nSELECT\n  ar.from_article_id,\n  a.article_number,\n  a.title,\n  a.text,\n  r.title AS regulation_title\nFROM article_relations AS ar\nJOIN articles AS a ON ar.from_article_id = a.id\nJOIN regulations AS r ON a.regulation_id = r.id\nWHERE ar.relation_type = 'mengubah'\n  AND r.short_type = 'UU'\n  AND r.number = 19\n  AND r.year = 2016\nLIMIT 100;\n``` "
  },
  {
    "question": "Apa hubungan antara Pasal 40 UU Nomor 19 Tahun 2016 dan Pasal 40 UU Nomor 11 Tahun 2008?",
    "answer": " ```sql\nSELECT\n  ar.relation_type\nFROM article_relations ar\nJOIN articles a1 ON ar.from_article_id = a1.id\nJOIN regulations r1 ON a1.regulation_id = r1.id\nJOIN articles a2 ON ar.to_article_id = a2.id\nJOIN regulations r2 ON a2.regulation_id = r2.id\nWHERE a1.article_number = '40'\n  AND r1.short_type = 'UU'\n  AND r1.number = '19'\n  AND r1.year = '2016'\n  AND a2.article_number = '40'\n  AND r2.short_type = 'UU'\n  AND r2.number = '11'\n  AND r2.year = '2008';\n``` "
  },
  {
    "question": "Apa isi pasal yang dirujuk oleh Pasal 25 PERMENKOMINFO No. 4 Tahun 2016?",
    "answer": " ```sql\nSELECT a.article_number, a.text\nFROM article_relations ar\nJOIN articles a ON ar.to_article_id = a.id\nJOIN regulations r ON a.regulation_id = r.id\nWHERE ar.relation_type = 'merujuk'\n  AND ar.from_article_id IN (\n    SELECT a2.id\n    FROM articles a2\n    JOIN regulations r2 ON a2.regulation_id = r2.id\n    WHERE a2.article_number = '25'\n      AND r2.short_type = 'PERMENKOMINFO'\n      AND r2.number = '4'\n      AND r2.year = '2016'\n  );\n``` "
  }
]

# ======================= EXAMPLE SELECTOR ========================

# BUILD SELECTOR
def build_selector(examples):
    return SemanticSimilarityExampleSelector.from_examples(
        examples,
        embedding_model,
        Chroma,
        k=5
    )
    
def make_prompt(selector):
    return FewShotPromptTemplate(
        example_selector=selector,
        example_prompt=example_prompt,
        prefix=TAG_INSTRUCTION,
        suffix=PROMPT_SUFFIX_ID,
        input_variables=["input", "table_info", "top_k"]
    )

# BUILD SELECTORS BY INTENT
def build_selectors_by_intent():
    grouped = defaultdict(list)
    for ex in examples:
        intent = detect_intent(ex["question"])
        grouped[intent].append(ex)
    # buat selector untuk setiap intent
    return {intent: build_selector(exlist) for intent, exlist in grouped.items()}
  
# GET PROMPT BY INTENT
def get_prompt_by_intent(intent, selectors):
    return make_prompt(selectors.get(intent, selectors.get("general")))
  
  # GET SQL CHAIN
def get_sql_chain(llm, question, selectors):
    intent = detect_intent(question)
    prompt = get_prompt_by_intent(intent, selectors)
    return LLMChain(llm=llm, prompt=prompt)
  
