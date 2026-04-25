from rest_framework import serializers

from .models import PoisoningEvent


class PoisoningEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoisoningEvent
        fields = [
            'id', 'update', 'bank', 'round', 'attack_type',
            'anomaly_score', 'detection_method', 'evidence_payload',
            'chain_tx_hash', 'resolved', 'resolution', 'detected_at',
        ]
        read_only_fields = ['id', 'detected_at']
