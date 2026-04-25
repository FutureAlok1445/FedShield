import uuid

from django.db import models


class PoisoningEvent(models.Model):
    """A detected poisoning attempt during a federation round."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    update = models.ForeignKey(
        'rounds.ModelUpdate', on_delete=models.CASCADE, related_name='poisoning_events'
    )
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='poisoning_events')
    round = models.ForeignKey(
        'rounds.FederationRound', on_delete=models.CASCADE, related_name='poisoning_events'
    )
    attack_type = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text='gradient_scaling | sign_flip | backdoor | sybil',
    )
    anomaly_score = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    detection_method = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text='fltrust | cosine_similarity | norm_check | statistical',
    )
    evidence_payload = models.JSONField(default=dict, blank=True)
    chain_tx_hash = models.CharField(max_length=128, blank=True, default='')
    resolved = models.BooleanField(default=False)
    resolution = models.TextField(blank=True, default='')
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poisoning_events'
        ordering = ['-detected_at']

    def __str__(self):
        return f'Poisoning by {self.bank_id} in round {self.round.round_number}'
