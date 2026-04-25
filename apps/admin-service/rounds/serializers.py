from rest_framework import serializers

from .models import FederationRound, ModelUpdate


class ModelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelUpdate
        fields = [
            'id', 'round', 'bank', 'weight_delta_cid', 'weight_hash',
            'signature', 'dp_epsilon_used', 'local_samples_used',
            'local_auc', 'trust_score', 'poisoning_flags', 'status',
            'submitted_at',
        ]
        read_only_fields = ['id', 'submitted_at']


class FederationRoundSerializer(serializers.ModelSerializer):
    updates = ModelUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = FederationRound
        fields = [
            'id', 'round_number', 'status', 'global_model_hash',
            'global_model_cid', 'chain_tx_hash', 'participants_expected',
            'participants_received', 'aggregation_algo', 'global_auc',
            'global_precision', 'global_recall', 'global_f1',
            'started_at', 'completed_at', 'updates',
        ]
        read_only_fields = ['id', 'started_at']


class FederationRoundListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no nested updates)."""

    class Meta:
        model = FederationRound
        fields = [
            'id', 'round_number', 'status', 'participants_expected',
            'participants_received', 'global_auc', 'started_at', 'completed_at',
        ]


class RoundStartSerializer(serializers.Serializer):
    expected_participants = serializers.IntegerField(min_value=1)
