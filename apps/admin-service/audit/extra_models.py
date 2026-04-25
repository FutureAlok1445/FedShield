"""
FedShield — Additional Django Models (PRD §9)

Models for tables that were specified in the PRD database schema
but not yet created: fraud_pattern_registry, scoring_requests,
shap_explanations, drift_reports.

These are registered in the 'audit' app since they are cross-cutting concerns.
"""
import uuid

from django.db import models


class FraudPatternRegistry(models.Model):
    """Registry of discovered fraud patterns across the federation (PRD §9)."""

    class Severity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pattern_hash = models.CharField(max_length=128, unique=True)
    pattern_type = models.CharField(
        max_length=30,
        help_text='velocity | mule | card_testing | account_takeover',
    )
    first_seen_round = models.IntegerField(null=True, blank=True)
    last_seen_round = models.IntegerField(null=True, blank=True)
    detection_count = models.IntegerField(default=1)
    reporting_bank_count = models.IntegerField(default=1)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'fraud_pattern_registry'
        ordering = ['-detection_count']

    def __str__(self):
        return f'{self.pattern_type} ({self.severity})'


class ScoringRequest(models.Model):
    """Real-time scoring log (PRD §9 — would be TimescaleDB hypertable in prod)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='scoring_requests')
    txn_ref_hash = models.CharField(max_length=64)
    model_round = models.IntegerField(null=True)
    fraud_probability = models.DecimalField(max_digits=6, decimal_places=5)
    risk_tier = models.CharField(max_length=10, help_text='low | medium | high | critical')
    decision = models.CharField(max_length=10, help_text='allow | review | block')
    shap_values = models.JSONField(default=dict, blank=True)
    latency_ms = models.IntegerField(null=True)
    scored_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scoring_requests'
        ordering = ['-scored_at']
        indexes = [
            models.Index(fields=['bank', '-scored_at'], name='idx_scoring_bank_time'),
            models.Index(fields=['risk_tier', '-scored_at'], name='idx_scoring_risk_tier'),
        ]

    def __str__(self):
        return f'{self.txn_ref_hash[:12]}... → {self.decision}'


class ShapExplanation(models.Model):
    """Pre-computed SHAP explanations cache (PRD §9)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    score = models.ForeignKey(ScoringRequest, on_delete=models.CASCADE, related_name='shap_explanations')
    feature_values = models.JSONField(help_text='{feature_name: shap_value}')
    base_value = models.DecimalField(max_digits=6, decimal_places=5, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shap_explanations'

    def __str__(self):
        return f'SHAP for {self.score_id}'


class DriftReport(models.Model):
    """Model drift monitoring reports (PRD §9, §10.7)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    round_from = models.IntegerField()
    round_to = models.IntegerField()
    auc_delta = models.DecimalField(max_digits=6, decimal_places=5, null=True)
    drift_detected = models.BooleanField(default=False)
    drift_features = models.JSONField(default=list, blank=True, help_text='Which features drifted')
    alert_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'drift_reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['round_from', 'round_to'], name='idx_drift_rounds'),
        ]

    def __str__(self):
        return f'Drift R{self.round_from}→R{self.round_to}'
