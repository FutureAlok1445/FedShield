from rest_framework import serializers

from .models import ComplianceReport


class ComplianceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceReport
        fields = [
            'id', 'bank', 'report_type', 'period_start',
            'period_end', 'content_cid', 'file_path', 'generated_at',
        ]
        read_only_fields = ['id', 'generated_at']


class ComplianceGenerateSerializer(serializers.Serializer):
    bank_id = serializers.UUIDField()
    report_type = serializers.ChoiceField(choices=ComplianceReport.ReportType.choices)
    period_start = serializers.DateField(required=False)
    period_end = serializers.DateField(required=False)
