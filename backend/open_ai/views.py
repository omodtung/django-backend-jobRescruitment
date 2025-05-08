from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from openai import OpenAI
from django.conf import settings

class ChatBotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Lấy tin nhắn từ client
        user_message = request.data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message is required"}, status=400)

        try:
            # Khởi tạo client OpenAI sử dụng OpenRouter
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENAI_API_KEY,  # Lưu ý: phải đặt key trong settings
            )

            # Gửi yêu cầu tới OpenRouter
            response = client.chat.completions.create(
                model="meta-llama/llama-4-maverick:free",  # Có thể thay đổi model khác nếu cần
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that chats in Vietnamese."},
                    {"role": "user", "content": user_message},
                ],
                extra_headers={
                    "HTTP-Referer": "http://127.0.0.1:8000",
                    "X-Title": "Localhost Chat",
                    "Content-Type": "application/json"
                }
            )

            # Đảm bảo có phản hồi
            if response and response.choices:
                reply = response.choices[0].message.content
                return JsonResponse({"role": "system","content": reply}, status=200)
            else:
                return JsonResponse({"error": "No response from OpenRouter"}, status=502)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader  # Hoặc PostgreSQLLoader nếu có
from langchain.chains import RetrievalQA
from django.conf import settings
import psycopg2
from psycopg2 import sql
import os

class ChatBotDatabaseView(APIView):
    permission_classes = [AllowAny]

    def __init__(self):
        # Khởi tạo kết nối PostgreSQL
        self.db_connection = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        
        # Khởi tạo Ollama LLM và Embeddings
        self.llm = Ollama(model="llama3.2")  # Model chính
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")  # Model embedding
        
        # Tạo vector store từ dữ liệu trong PostgreSQL
        self.setup_vector_store()

    def setup_vector_store(self):
        """Lấy dữ liệu từ nhiều bảng và tạo vector store"""
        cursor = self.db_connection.cursor()
        
        all_documents = []

        # Truy vấn từ bảng companies
        cursor.execute("SELECT * FROM companies;")
        for row in cursor.fetchall():
            all_documents.append(f"[companies] ID: {row[0]}\nContent: {row[1]}")

        # Truy vấn từ bảng jobs
        cursor.execute("SELECT * FROM jobs;")
        for row in cursor.fetchall():
            all_documents.append(f"[jobs] ID: {row[0]}\nContent: {row[1]}")

        cursor.close()

        # Ghi ra file tạm
        with open("temp_docs.txt", "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_documents))

        # Load vào vector store
        loader = TextLoader("temp_docs.txt")
        pages = loader.load_and_split()
        self.vector_db = Chroma.from_documents(pages, self.embeddings)
        os.remove("temp_docs.txt")


    def post(self, request):
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Message is required"}, status=400)
        print("user_message to chat admin: ", user_message)

        try:
            # Bước 1: Tìm kiếm trong PostgreSQL bằng semantic search
            docs = self.vector_db.similarity_search(user_message, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Bước 2: Tạo prompt kết hợp dữ liệu từ DB
            prompt = f"""
            Dựa trên thông tin từ cơ sở dữ liệu sau:
            {context}
            
            Trả lời câu hỏi: {user_message}
            """
            
            # Bước 3: Gọi Ollama để tạo phản hồi
            reply = self.llm(prompt)
            
            return JsonResponse({
                "role": "system",
                "content": reply,
                "sources": [doc.metadata.get("source", "") for doc in docs]  # Trả về ID tài liệu tham khảo
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def __del__(self):
        """Đóng kết nối database khi hủy class"""
        if hasattr(self, 'db_connection'):
            self.db_connection.close()