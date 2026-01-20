from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id','product_name','price','description','image_url','component_type','stock','model_file']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.has_valid_image():
            try:
                return request.build_absolute_uri(obj.image.url)
            except (ValueError, AttributeError):
                return None
        return None
