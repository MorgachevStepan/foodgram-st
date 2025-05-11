import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers

class Base64ImageField(serializers.ImageField):
    """Кастомное поле для обработки изображений в Base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                filename = f'{uuid.uuid4()}.{ext}'
                data = ContentFile(base64.b64decode(imgstr), name=filename)
            except Exception:
                raise serializers.ValidationError("Некорректный формат base64-изображения.")
        elif data is None and self.allow_null:
            return None
        elif not isinstance(data, ContentFile) and 'request' in self.context:
             pass

        try:
            return super().to_internal_value(data)
        except Exception as e:
            raise serializers.ValidationError(f"Ошибка обработки изображения: {e}")


    def to_representation(self, value):
        if not value:
            return None
        request = self.context.get('request', None)
        if request is not None:
            try:
                return request.build_absolute_uri(value.url)
            except Exception:
                return str(value)

        try:
             return value.url
        except AttributeError:
             return str(value)