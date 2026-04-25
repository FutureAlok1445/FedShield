import uuid

from django.db import models


class ComplianceReport(models.Model):
    """A generated compliance report for regulatory purposes."""

    class ReportType(models.TextChoices):
        RBI_DPSP = 'rbi_dpsp', 'RBI DPSP'
        GDPR_ART30 = 'gdpr_art30', 'GDPR Art. 30'
        PCI_DSS = 'pci_dss', 'PCI-DSS'
        FIU_IND = 'fiu_ind', 'FIU-IND'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='compliance_reports')
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    content_cid = models.CharField(max_length=128, blank=True, default='')
    file_path = models.CharField(max_length=512, blank=True, default='')
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance_reports'
        ordering = ['-generated_at']

    def __str__(self):
        return f'{self.report_type} for {self.bank_id}'
