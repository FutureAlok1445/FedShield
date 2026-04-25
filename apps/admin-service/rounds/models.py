import uuid

from django.db import models


class FederationRound(models.Model):
    """A single round of federated learning aggregation."""

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        AGGREGATING = 'aggregating', 'Aggregating'
        COMPLETE = 'complete', 'Complete'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    round_number = models.IntegerField(unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    global_model_hash = models.CharField(max_length=128, blank=True, default='')
    global_model_cid = models.CharField(max_length=128, blank=True, default='')
    chain_tx_hash = models.CharField(max_length=128, blank=True, default='')
    participants_expected = models.IntegerField()
    participants_received = models.IntegerField(default=0)
    aggregation_algo = models.CharField(max_length=20, default='fltrust')
    global_auc = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    global_precision = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    global_recall = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    global_f1 = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'federation_rounds'
        ordering = ['-round_number']

    def __str__(self):
        return f'Round {self.round_number} ({self.status})'


class ModelUpdate(models.Model):
    """A single bank's weight delta submission for a round."""

    class Status(models.TextChoices):
        RECEIVED = 'received', 'Received'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        FLAGGED = 'flagged', 'Flagged'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    round = models.ForeignKey(FederationRound, on_delete=models.CASCADE, related_name='updates')
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='model_updates')
    weight_delta_cid = models.CharField(max_length=128)
    weight_hash = models.CharField(max_length=128)
    signature = models.TextField()
    dp_epsilon_used = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    local_samples_used = models.IntegerField(null=True, blank=True)
    local_auc = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    trust_score = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    poisoning_flags = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'model_updates'
        unique_together = [['round', 'bank']]
        ordering = ['-submitted_at']

    def __str__(self):
        return f'Update by {self.bank_id} in round {self.round.round_number}'
