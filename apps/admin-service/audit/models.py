import uuid

from django.db import models


class AuditEntry(models.Model):
    """Audit trail entry for federation events."""

    class EventType(models.TextChoices):
        ROUND_STARTED = 'round_started', 'Round Started'
        ROUND_COMPLETED = 'round_completed', 'Round Completed'
        BANK_REGISTERED = 'bank_registered', 'Bank Registered'
        BANK_SUSPENDED = 'bank_suspended', 'Bank Suspended'
        POISONING_DETECTED = 'poisoning_detected', 'Poisoning Detected'
        MODEL_PUBLISHED = 'model_published', 'Model Published'
        REPORT_GENERATED = 'report_generated', 'Report Generated'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    actor = models.CharField(max_length=255, blank=True, default='', help_text='Who triggered the event')
    bank = models.ForeignKey(
        'banks.Bank', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_entries'
    )
    round_number = models.IntegerField(null=True, blank=True)
    chain_tx_hash = models.CharField(max_length=128, blank=True, default='')
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_entries'
        ordering = ['-created_at']
        verbose_name_plural = 'Audit entries'

    def __str__(self):
        return f'{self.event_type} at {self.created_at}'


# Import extra PRD §9 models so Django discovers them
from .extra_models import FraudPatternRegistry, ScoringRequest, ShapExplanation, DriftReport  # noqa: E402, F401
