import uuid

from django.db import models


class Bank(models.Model):
    """Bank entity registered in the FedShield network."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'

    class Tier(models.TextChoices):
        STANDARD = 'standard', 'Standard'
        PREMIUM = 'premium', 'Premium'
        ANCHOR = 'anchor', 'Anchor'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=2, default='IN')
    regulator_id = models.CharField(max_length=255, blank=True, default='')
    public_key = models.TextField(unique=True, help_text='RSA-4096 public key')
    api_key_hash = models.CharField(max_length=128)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.STANDARD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    privacy_epsilon = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'banks'
        ordering = ['-joined_at']

    def __str__(self):
        return f'{self.name} ({self.status})'
