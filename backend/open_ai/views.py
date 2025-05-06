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

