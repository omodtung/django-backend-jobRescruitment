from rest_framework import serializers
from .models import Companies


pathCompany = "/api/companies/"
class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = '__all__'  
        # fields = [
        #     "id",
        #     "name",
        #     "address",
        #     "description",
        #     "created_at",
        #     "updated_at",
        #     "logo",
        #     "is_deleted",
        #     "deleted_at",
        #     "created_by",
        #     "updated_by",
        #     "delete_by",
        # ]
        # same import feild into  Model 
    
    def validate(self, data):
        if data.get('is_deleted') and not data.get('deleted_at'):
            raise serializers.ValidationError("`deleted_at` must be set when soft-deleting a company.")
        return data

    def to_representation(self, instance):
        """Customize the serialized output to replace `id` with `_id`."""
        representation = super().to_representation(instance)
        representation['_id'] = representation.pop('id')  # Replace `id` with `_id`
        return representation