# NusantaraCare - Asisten GenAI Operasional Internal (RAG)

Repositori ini berisi implementasi _backend_ FastAPI untuk Final Project AI Engineer Intermediate: Membangun sistem _Retrieval-Augmented Generation_ (RAG) untuk dokumen Panduan Operasional Layanan Internal NusantaraCare.

---

## 1. Problem & Success Criteria

**Problem Statement:**
Karyawan NusantaraCare sering mengalami kesulitan dalam mencari jawaban spesifik mengenai prosedur dan kebijakan layanan internal karena dokumen SOP yang panjang dan tersebar. Pencarian menggunakan kata kunci konvensional (_keyword-based_) sering kali gagal menangkap konteks permasalahan. Selain itu, ada kebutuhan mendesak agar jawaban asisten AI selalu didasarkan pada dokumen resmi (tidak berhalusinasi) dan menyertakan kutipan sumber yang jelas.

**Success Criteria:**

1. Sistem mampu merespons pertanyaan karyawan secara akurat berdasarkan dokumen operasional resmi.
2. Respons selalu mengembalikan format JSON dengan 3 _field_ wajib: `answer`, `confidence_label`, dan `reason_code`.
3. Sistem secara tegas menolak menjawab pertanyaan di luar ruang lingkup (menjawab "tidak ditemukan dalam dokumen") dan menolak instruksi _prompt injection_.
4. Sistem tidak keliru menggunakan kebijakan versi lama (v1.4) dan hanya merujuk pada kebijakan aktif (v2.0).

---

## 2. Knowledge Base Understanding

Dokumen yang menjadi basis pengetahuan (_Knowledge Base_) adalah **Panduan Operasional Layanan Internal NusantaraCare v2.0**.

- **Metadata Dokumen:** `doc_id`: NC-OPS-001, `doc_version`: 2.0, `effective_date`: 2026-07-01.
- **Struktur Dokumen:** Memuat SOP layanan akses IT, penanganan gangguan, pengadaan perlengkapan, dan pelaporan insiden keamanan.
- **Pemahaman Konflik Versi (v2.0 vs v1.4):** Dokumen ini memuat catatan arsip versi 1.4 yang sudah nonaktif (berlaku efektif hingga 2026-06-30). Terdapat perbedaan fundamental, misalnya batas pengajuan perlengkapan kerja (3 hari kerja di v1.4 vs 5 hari kerja di v2.0), serta penggunaan saluran _email_ yang kini dibatasi hanya untuk situasi darurat `[DARURAT-PORTAL]`. Sistem harus mampu mengisolasi dan memblokir pembacaan arsip v1.4 ini agar keputusan operasional tetap relevan.

---

## 3. RAG Design & Data Preparation

Arsitektur RAG didesain dengan pertimbangan akurasi dan kemandirian sistem:

- **Chunking:** Pemotongan teks dilakukan menggunakan pemisah tajuk/heading level 2 (`\n## `) dari format Markdown.
  - _Alasan:_ Cara ini menjaga keutuhan konteks di setiap bab/SOP. Memotong murni berdasarkan jumlah karakter berisiko memutus alur logika sebuah prosedur.
- **Metadata per Chunk:** Saat _chunking_, sistem memindai teks untuk mendeteksi frasa "Arsip Kebijakan v1.4". Jika ditemukan, sistem memberikan label metadata `is_active: False`. Jika tidak, diberi label `is_active: True`. Terdapat pula metadata tambahan `source: NC-OPS-001`.
- **Vector Database (ChromaDB + Local Embedding):** Menggunakan **ChromaDB** dengan model _embedding_ lokal via `sentence-transformers`.
  - _Justifikasi:_ Pemrosesan _embedding_ secara lokal membuat sistem lebih tangguh, cepat (tanpa latensi jaringan), dan independen dari kegagalan API _provider_ LLM eksternal (menghindari _error_ 404 pada _endpoint_ _embedding_).
- **Retrieval:** Sistem mencari dokumen (_top-k = 3_) menggunakan _query text_, dengan filter wajib `where={"is_active": True}`. Ini menjamin aturan v1.4 tidak akan pernah disuplai ke LLM.
- **Prompting:** _System prompt_ diinstruksikan secara absolut untuk **hanya** menggunakan konteks yang diberikan, wajib merespons "tidak ditemukan dalam dokumen" untuk konteks nihil, menyertakan kutipan sumber, dan mengabaikan upaya perubahan peran/aturan (_prompt injection_).

---

## 4. Kesimpulan & Dokumentasi

**Kesimpulan & Rekomendasi:**
Sistem telah berjalan sangat baik dan berhasil menyaring informasi kebijakan yang sudah usang di level _database_. Penggunaan _embedding_ lokal mempercepat inisialisasi awal. Sebagai rekomendasi perbaikan, ke depannya sistem dapat dilengkapi dengan fitur _memory chat history_ agar dapat melayani pertanyaan lanjutan (_follow-up questions_) dari pengguna.

**Tautan Penting:**

- **Repositori GitHub:** https://github.com/windydwifebrianti/final-project-nusantaracare.git
- **Live API (FastAPI Cloud):** https://rag-agentic-nusantaracare.fastapicloud.dev
- **Documentation at** https://rag-agentic-nusantaracare.fastapicloud.dev/docs

**Struktur Repositori:**

```text
repository/
├── README.md               # Laporan teknis
├── data/raw_docs/
│   └── nusantaracare_panduan_operasional_internal_v2.md   # KB dokumen utuh
├── app/
│   ├── main.py             # Entry point FastAPI
│   ├── schemas.py          # Kontrak Pydantic
│   └── services/
│       └── rag.py          # Logika Retrieval dan LLM
├── requirements.txt        # Daftar dependencies
├── .env.example            # Contoh variabel lingkungan
└── .gitignore              # Mengabaikan .env dan cache
```
