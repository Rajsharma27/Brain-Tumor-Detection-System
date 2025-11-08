from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
import os
from dotenv import load_dotenv
from pathlib import Path
import glob

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE-API-KEY")

class RAGChatbot:
    def __init__(self, report_content=""):
        
        self.report_content = ""  
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        try:
            data_dir = Path(__file__).resolve().parent.parent.parent / "Data"
            if data_dir.exists():
                print(f"ℹ️  Initializing RAG knowledge base from PDFs at: {data_dir}")
                pdf_text = self._load_pdfs_text(data_dir)
                if pdf_text and pdf_text.strip():
                    self._initialize_chain(pdf_text)
                else:
                    print("⚠️  No usable text found in PDFs. Chatbot will start without retrieval context.")
            else:
                print(f"⚠️  Data directory not found at {data_dir}. Chatbot will start without retrieval context.")
        except Exception as e:
            print(f"❌ Error initializing from PDFs: {e}")
    
    def update_report_content(self, report_content):
        print("ℹ️  update_report_content called but ignored — this chatbot uses PDF knowledge base only.")
        return
    
    def _split_text(self, text, chunk_size=500, chunk_overlap=100):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)
    
    def _create_vector_store(self, text_chunks):
        documents = [Document(page_content=chunk) for chunk in text_chunks]
        vector_store = FAISS.from_documents(documents, self.embeddings)
        return vector_store

    def _load_pdfs_text(self, data_dir: Path) -> str:
        
        if PyPDF2 is None:
            print("⚠️  PyPDF2 not installed. Install it (pip install PyPDF2) to enable PDF context loading.")
            return ""

        texts = []
        pdf_paths = list(data_dir.glob("**/*.pdf"))
        if not pdf_paths:
            print(f"⚠️  No PDF files found in {data_dir}")
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
                    print(f"ℹ️  Loaded {p.name} ({len(joined)} chars)")
            except Exception as e:
                print(f"⚠️  Failed to read PDF {p}: {e}")

        return "\n\n".join(texts)
    
    def _initialize_chain(self, content):
        chunks = self._split_text(content)
        self.vector_store = self._create_vector_store(chunks)
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            memory=self.memory,
            verbose=False
        )
    
    def answer_question(self, question):
        try:
            if self.chain is None:
                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
                medical_prompt = f"""You are a friendly and knowledgeable AI medical assistant.

            Give answer to the:
            "{question}"
            Use the retrieved context for giving answers.

            Guidelines:
            - Use simple, empathetic language that anyone can understand.
            - Do NOT prescribe medication or give direct treatment plans.
            - If relevant, suggest consulting a neurologist or doctor for confirmation.
            - Keep your answer short (2–4 paragraphs max)."""
                response = llm.predict(medical_prompt)
                return response.strip()
            else:
                # Use invoke() instead of deprecated __call__
                response = self.chain.invoke({"question": question})
                answer_text = response.get("answer", "").strip()
        
                return answer_text

        except Exception as e:
            print(f"Error in answer_question: {e}")
            return f"Sorry, I couldn't process your question: {str(e)}"
    
    def clear_memory(self):
        self.memory.clear()


_chatbot_instance = None


def get_chatbot(report_content=""):
    global _chatbot_instance
    
    if report_content:
        _chatbot_instance = RAGChatbot(report_content=report_content)
    elif _chatbot_instance is None:
        _chatbot_instance = RAGChatbot()
    
    return _chatbot_instance
