from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from banks.models import Bank

from .models import ComplianceReport
from .serializers import ComplianceGenerateSerializer, ComplianceReportSerializer


@api_view(['GET'])
def report_list(request):
    """List all compliance reports."""
    reports = ComplianceReport.objects.select_related('bank').all()
    serializer = ComplianceReportSerializer(reports, many=True)
    return Response({'reports': serializer.data})


@api_view(['POST'])
def generate_report(request):
    """Trigger compliance report generation."""
    serializer = ComplianceGenerateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        bank = Bank.objects.get(pk=serializer.validated_data['bank_id'])
    except Bank.DoesNotExist:
        return Response({'error': 'bank not found'}, status=status.HTTP_404_NOT_FOUND)

    report = ComplianceReport.objects.create(
        bank=bank,
        report_type=serializer.validated_data['report_type'],
        period_start=serializer.validated_data.get('period_start'),
        period_end=serializer.validated_data.get('period_end'),
    )

    # Trigger Celery task for actual PDF generation with ReportLab
    from .tasks import generate_compliance_pdf
    generate_compliance_pdf.delay(str(report.id))

    return Response(ComplianceReportSerializer(report).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def download_report(request, report_id):
    """Download a generated compliance report."""
    try:
        report = ComplianceReport.objects.get(pk=report_id)
    except ComplianceReport.DoesNotExist:
        return Response({'error': 'report not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'report_id': str(report_id),
        'report_type': report.report_type,
        'download_url': f'/static/reports/{report_id}.pdf',
        'generated_at': report.generated_at.isoformat(),
    })
