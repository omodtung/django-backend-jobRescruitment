from .models import Resume
from rest_framework import serializers

class ResumeSerializers(serializers.ModelSerializer):

    class Meta:
        model = Resume  
        fields = "__all__"

    def validate(self, data):
        """Kiểm tra logic dữ liệu đầu vào"""
        if data.get("is_deleted") and not data.get("deleted_at"):
            raise serializers.ValidationError("`deleted_at` phải được đặt khi xóa mềm.")
        return data
    

        
