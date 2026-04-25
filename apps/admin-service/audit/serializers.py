from rest_framework import serializers

from .models import AuditEntry


class AuditEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEntry
        fields = [
            'id', 'event_type', 'actor', 'bank', 'round_number',
            'chain_tx_hash', 'details', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
