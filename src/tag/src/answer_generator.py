import os, sys
sys.path.append(os.path.dirname(__file__))
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from init_llm import init_llm
from prompt_config import ANSWER_GENERATOR_INSTRUCTION

load_dotenv()


# ===================== FEW SHOT EXAMPLES =====================
few_shot_examples = """
Contoh 1:
Kolom-kolom: a.article_number, a.text, r.title
Data: ['Lembaga Penyiaran Asing dilarang didirikan di Indonesia.', 'Lembaga Penyiaran Asing hanya dapat menyelenggarakan kegiatan peliputan di Indonesia, yang meliputi :\na. kegiatan, siaran secara tidak tetap ; dan/atau\nb. kegiatan jurnalistik.', '(1) Lembaga Penyiaran Asing yang menyelenggarakan kegiatan siaran secara tidak tetap di Indonesia sebagaimana dimaksud dalam Pasal 3 dapat membawa perangkat pengiriman ke dan penerima siaran dari satelit dan/atau media lainnya.\n(2) Lembaga Penyiaran Asing yang menyelenggarakan kegiatan jurnalistik di Indonesia sebagaimana dimaksud dalam Pasal 3 dapat :\n\ta. menempatkan koresponden untuk melakukan kegiatan jurnalistik; atau\n\tb. membuka kantor penyiaran asing untuk mendukung bidang administratif.', 'Dalam membuka kantor penyiaran asing sebagaimana dimaksud dalam Pasal 4 ayat (2) huruf b, Lembaga Penyiaran Asing wajib memenuhi ketentuan sebagai berikut :\na. kantor penyiaran asing tersebut bukan merupakan stasiun penyiaran; dan\nb. kantor penyiaran asing tersebut berlokasi di ibukota negara dan berada pada wilayah yurisdiksi Negara Republik Indonesia.']

Pertanyaan: Apakah Lembaga Penyiaran Asing boleh mendirikan stasiun penyiaran di Indonesia?
Jawaban: Tidak, Lembaga Penyiaran Asing dilarang didirikan di Indonesia. Namun, mereka dapat menyelenggarakan kegiatan peliputan yang meliputi kegiatan siaran secara tidak tetap dan/atau kegiatan jurnalistik. Kegiatan jurnalistik ini dapat dilakukan dengan menempatkan koresponden atau membuka kantor penyiaran asing.

Contoh 2:
Kolom-kolom: d.name, .definition
Data: ['Dalam Peraturan Menteri ini yang dimaksud dengan:\n(1) Jaringan Dokumentasi dan Informasi Hukum Kementerian Komunikasi dan Informatika yang selanjutnya disebut JDIH Kemkominfo adalah wadah pendayagunaan bersama atas dokumen hukum secara tertib, terpadu, dan berkesinambungan, serta merupakan sarana pemberian pelayanan informasi hukum secara lengkap, akurat, mudah, dan tepat di lingkungan Kementerian Komunikasi dan Informatika.\n(2) Dokumen Hukum adalah produk hukum yang berupa peraturan perundang-undangan dan produk hukum selain peraturan perundang-undangan antara lain, putusan pengadilan, yurisprudensi, monografi hukum, artikel majalah hukum, buku hukum, penelitian hukum, pengkajian hukum, naskah akademis, dan rancangan peraturan perundang-undangan.\n(3) Pengelolaan Dokumentasi dan Informasi Hukum adalah kegiatan pengumpulan, pengolahan, penyimpanan, pelestarian, dan pendayagunaan informasi Dokumen Hukum.\n(4) Pusat Jaringan Dokumentasi dan Informasi Hukum Nasional yang selanjutnya disebut Pusat JDIHN adalah Badan Pembinaan Hukum Nasional, Kementerian Hukum dan Hak Asasi Manusia yang bertugas melakukan pembinaan, pengembangan, dan monitoring pada Anggota Jaringan Dokumentasi dan Informasi Hukum Nasional.\n(5) Anggota Jaringan Dokumentasi dan Informasi Hukum Nasional yang selanjutnya disebut Anggota JDIHN adalah kementerian negara, sekretariat lembaga negara, lembaga pemerintahan non kementerian, pemerintah provinsi, pemerintah kabupaten/kota, sekretariat dewan perwakilan rakyat daerah tingkat provinsi dan kabupaten/kota yang tugas dan fungsinya menyelenggarakan kegiatan yang berkaitan dengan Dokumen Hukum, dan perpustakaan hukum pada perguruan tinggi negeri dan perguruan tinggi swasta, serta lembaga lain yang bergerak di bidang pengembangan dokumentasi dan informasi hukum yang ditetapkan oleh menteri hukum dan hak asasi manusia.', '(1) Peraturan Menteri ini dimaksudkan untuk memberikan kepastian hukum dan kemanfaatan JDIH Kemkominfo.\n(2) Peraturan Menteri ini bertujuan untuk:\n\ta. menjamin terciptanya Pengelolaan Dokumentasi dan Informasi Hukum yang terpadu di lingkungan Kementerian Komunikasi dan Informatika dan terintegrasi dengan Pusat JDIHN dan sesama Anggota JDIHN;\n\tb. menjamin ketersediaan dokumen dan informasi hukum yang lengkap dan akurat, serta dapat diakses secara cepat dan mudah;\n\tc. mengembangkan kerja sama yang efektif dalam rangka penyelenggaraan JDIH Kemkominfo; dan\n\td. meningkatkan kualitas pembangunan hukum di bidang komunikasi dan informatika, serta pelayanan kepada publik sebagai salah satu wujud ketatapemerintahan yang baik, transparan, efektif, efisien, dan bertanggung jawab.']

Pertanyaan: Apa itu Jaringan Dokumentasi dan Informasi Hukum (JDIH) Kemkominfo, dan apa tujuannya?
Jawaban: JDIH Kemkominfo adalah wadah pendayagunaan bersama atas dokumen hukum secara tertib, terpadu, dan berkesinambungan di lingkungan Kementerian Komunikasi dan Informatika. Tujuannya adalah untuk menjamin terciptanya pengelolaan dokumentasi dan informasi hukum yang terpadu, menjamin ketersediaan dokumen dan informasi hukum yang lengkap dan akurat, mengembangkan kerja sama yang efektif, dan meningkatkan kualitas pembangunan hukum di bidang komunikasi dan informatika serta pelayanan kepada publik.

Contoh 3:
Kolom-kolom: r.title
Data: ["{'title': 'Peraturan Pemerintah (PP) Nomor 80 Tahun 2019 tentang Perdagangan Melalui Sistem Elektronik'}"]

Pertanyaan: Apa judul dari Peraturan Pemerintah (PP) Nomor 80 Tahun 2019?
Jawaban: Judul dari Peraturan Pemerintah (PP) Nomor 80 Tahun 2019 adalah Perdagangan Melalui Sistem Elektronik.

Contoh 4:
Kolom-kolom: r.title
Data: [
"{'title': 'Peraturan Menteri Komunikasi dan Informatika Nomor 13 Tahun 2019 tentang Penyelenggaraan Jasa Telekomunikasi', 'count': 22}",
 "{'title': 'Undang-undang (UU) Nomor 11 Tahun 2008 tentang Informasi dan Transaksi Elektronik', 'count': 13}",
 "{'title': 'Peraturan Menteri Komunikasi dan Informatika Nomor 1/PER/M.KOMINFO/1/2010 Tahun 2010 tentang Penyelenggaraan Jaringan Telekomunikasi', 'count': 9}",
 "{'title': 'Peraturan Menteri Komunikasi dan Informatika Nomor 26/PER/M.KOMINFO/5/2007 Tahun 2007 tentang Pengamanan Pemanfaatan Jaringan Telekomunikasi Berbasis Protokol Internet', 'count': 9}",
 "{'title': 'Undang-undang (UU) Nomor 19 Tahun 2016 tentang Perubahan Atas Undang-Undang Nomor 11 Tahun 2008 Tentang Informasi Dan Transaksi Elektronik', 'count': 5}"
]

Pertanyaan: Judul peraturan apa saja (lima) yang memiliki banyak pasal yang sudah tidak efektif atau tidak berlaku?
Jawaban: Berikut adalah 5 peraturan dengan jumlah pasal yang sudah tidak efektif terbanyak:
1. Peraturan Menteri Komunikasi dan Informatika Nomor 13 Tahun 2019 tentang Penyelenggaraan Jasa Telekomunikasi (22 pasal tidak efektif)
2. Undang-undang (UU) Nomor 11 Tahun 2008 tentang Informasi dan Transaksi Elektronik (13 pasal tidak efektif)
3. Peraturan Menteri Komunikasi dan Informatika Nomor 1/PER/M.KOMINFO/1/2010 Tahun 2010 tentang Penyelenggaraan Jaringan Telekomunikasi (9 pasal tidak efektif)
4. Peraturan Menteri Komunikasi dan Informatika Nomor 26/PER/M.KOMINFO/5/2007 Tahun 2007 tentang Pengamanan Pemanfaatan Jaringan Telekomunikasi Berbasis Protokol Internet (9 pasal tidak efektif)
5. Undang-undang (UU) Nomor 19 Tahun 2016 tentang Perubahan Atas Undang-Undang Nomor 11 Tahun 2008 Tentang Informasi Dan Transaksi Elektronik (5 pasal tidak efektif)

Contoh 5:
Kolom-kolom: a.article_number
Data: [
"{'number': '1'}",
 "{'number': '26'}",
 "{'number': '31'}",
 "{'number': '40'}",
 "{'number': '43'}",
 "{'number': '45'}"
]

Pertanyaan: Pasal nomor berapa saja dari UU Nomor 11 Tahun 2008 yang sudah tidak berlaku setelah diamandemen oleh UU Nomor 19 Tahun 2016?
Jawaban: Pasal-pasal dari UU Nomor 11 Tahun 2008 yang sudah tidak berlaku setelah diamandemen oleh UU Nomor 19 Tahun 2016 adalah:
*   Pasal 1
*   Pasal 26
*   Pasal 31
*   Pasal 40
*   Pasal 43
*   Pasal 45
"""


# # Prompt zero-shot (tanpa contoh)
# answer_prompt_zero = PromptTemplate(
#     input_variables=["columns", "rows", "question"],
#     template=ANSWER_GENERATOR_INSTRUCTION.replace("{few_shot_section}", "")
# )

few_shot_examples = few_shot_examples.replace("{", "{{").replace("}", "}}")


# Prompt few-shot (pakai contoh)
answer_prompt_few = PromptTemplate(
    input_variables=["columns", "rows", "question"],
    template=ANSWER_GENERATOR_INSTRUCTION.replace("{few_shot_section}", few_shot_examples)
)


# ===================== MAIN FUNCTION =====================
def generate_answer(columns, rows, question, llm_mode: str = "claude"):
    """
    Pilih hasil query kemudian susun menjadi jawaban bahasa alami berdasarkan pertanyaan user.
    Pilih LLM via llm_mode: "claude" atau "ollama"
    Pilih prompt mode: "zero-shot" atau "few-shot"
    """
    rows_text = "\n".join([f"| {' | '.join(map(str, row))} |" for row in rows])
    columns_text = f"| {' | '.join(columns)} |"

    llm = init_llm(llm_mode)
    prompt = answer_prompt_few 
    inputs = {
        "columns": columns_text,
        "rows": rows_text,
        "question": question
    }
    
    chain = prompt | llm
    result = chain.invoke(inputs)

    if hasattr(result, "content"):
        return result.content.strip()
    else:
        return str(result).strip()

