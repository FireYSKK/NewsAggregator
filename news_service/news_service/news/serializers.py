from rest_framework import serializers
from .models import Transaction, Headline

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "department", "amount", "created_by", "created_at", "is_confirmed"]


class HeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        # Строится по модели новостного заголовка
        model = Headline
        # Задействует все поля модели
        fields = '__all__'
