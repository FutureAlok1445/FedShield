from rest_framework import serializers

from .models import Bank


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            'id', 'name', 'country_code', 'regulator_id',
            'tier', 'status', 'privacy_epsilon',
            'joined_at', 'last_active_at',
        ]
        read_only_fields = ['id', 'joined_at']


class BankCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['name', 'country_code', 'regulator_id', 'public_key', 'api_key_hash', 'tier', 'privacy_epsilon']


class BankStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Bank.Status.choices)
