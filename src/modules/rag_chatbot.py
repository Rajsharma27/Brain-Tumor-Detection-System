import os
from pathlib import Path

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    import faiss
except Exception:
    faiss = None

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Google Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE-API-KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class RAGChatbot:
    def __init__(self, report_content=""):
        self.report_content = report_content
        self.model = None
        self.index = None
        self.chunks = []

        # Initialize Gemini Session for conversation history
        try:
            self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
            self.chat_session = self.gemini_model.start_chat(history=[])
        except Exception as e:
            print(f"Failed to initialize Gemini: {e}")
            self.gemini_model = None
            self.chat_session = None

        # Initialize FAISS and SentenceTransformers for RAG
        try:
            if SentenceTransformer and faiss:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                data_dir = Path(__file__).resolve().parent.parent.parent / "Data"
                if data_dir.exists():
                    print(f"Initializing RAG knowledge base from PDFs at: {data_dir}")
                    pdf_text = self._load_pdfs_text(data_dir)
                    if pdf_text and pdf_text.strip():
                        self._initialize_vector_store(pdf_text)
                    else:
                        print("No usable text found in PDFs. Chatbot will start without retrieval context.")
                else:
                    print(f"Data directory not found at {data_dir}. Chatbot will start without retrieval context.")
            else:
                print("sentence_transformers or faiss not installed. Chatbot will run without RAG.")
        except Exception as e:
            print(f"Error initializing RAG components: {e}")

    def update_report_content(self, report_content):
        self.report_content = report_content

    def _split_text(self, text, chunk_size=500, chunk_overlap=100):
        """A simple string chunker to replace LangChain's RecursiveCharacterTextSplitter"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start += (chunk_size - chunk_overlap)
        return chunks

    def _initialize_vector_store(self, content):
        self.chunks = self._split_text(content)
        if not self.chunks:
            return

        embeddings = self.model.encode(self.chunks)
        dim = embeddings.shape[1]

        # Create FAISS Index
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype('float32'))

    def _load_pdfs_text(self, data_dir: Path) -> str:
        if PyPDF2 is None:
            return ""

        texts = []
        pdf_paths = list(data_dir.glob("**/*.pdf"))
        if not pdf_paths:
            return ""

        for p in pdf_paths:
            try:
                with open(p, "rb") as fh:
                    reader = PyPDF2.PdfReader(fh)
                    page_texts = []
                    for page in reader.pages:
                        try:
                            page_texts.append(page.extract_text() or "")
                        except Exception:
                            continue
                    joined = "\n".join(page_texts)
                    texts.append(f"\n\n--- {p.name} ---\n\n" + joined)
            except Exception as e:
                print(f"Failed to read PDF {p}: {e}")

        return "\n\n".join(texts)

    def answer_question(self, question):
        try:
            if self.chat_session is None:
                return "Gemini API is not configured or failed to initialize. Please check your .env file and GOOGLE_API_KEY."

            context = ""
            if self.index is not None and self.model is not None and len(self.chunks) > 0:
                # Retrieve relevant context using raw FAISS
                q_emb = self.model.encode([question]).astype('float32')
                distances, indices = self.index.search(q_emb, 3) # top 3 matches
                retrieved_chunks = [self.chunks[i] for i in indices[0] if i < len(self.chunks) and i >= 0]
                context = "\n\n".join(retrieved_chunks)

            medical_prompt = f"""You are a friendly and knowledgeable AI medical assistant.

Answer the following question using the provided context as background knowledge. If the context is irrelevant, rely on your general medical knowledge safely.
Question: "{question}"

Context:
{context}

Guidelines:
- Use clear, compassionate, and easy-to-understand language suitable for anyone.
- Naturally incorporate the relevant information from the context to support your answer (do not explicitly say 'According to the context').
- Do not prescribe medication or provide specific treatment plans.
- If appropriate, gently recommend consulting a doctor or neurologist for confirmation.
- Keep your response concise — no more than 2–4 paragraphs."""

            # Send to Gemini
            response = self.chat_session.send_message(medical_prompt)
            return response.text.strip()

        except Exception as e:
            print(f"Error in answer_question: {e}")
            return f"Sorry, I couldn't process your question: {str(e)}"

    def clear_memory(self):
        """Reset conversation history by starting a new chat session"""
        if self.gemini_model:
            self.chat_session = self.gemini_model.start_chat(history=[])


_chatbot_instance = None


def get_chatbot(report_content=""):
    global _chatbot_instance

    if report_content:
        _chatbot_instance = RAGChatbot(report_content=report_content)
    elif _chatbot_instance is None:
        _chatbot_instance = RAGChatbot()

    return _chatbot_instance
