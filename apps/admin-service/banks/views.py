"""Bank management API views.

Audit fix: Added IsAuthenticated permission to all views.
Admin API must not be publicly accessible.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Bank
from .serializers import BankCreateSerializer, BankSerializer, BankStatusSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bank_list(request):
    """List all banks or register a new bank."""
    if request.method == 'POST':
        serializer = BankCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank = serializer.save()
        return Response(BankSerializer(bank).data, status=status.HTTP_201_CREATED)

    banks = Bank.objects.all()
    serializer = BankSerializer(banks, many=True)
    return Response({'banks': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bank_detail(request, bank_id):
    """Get bank details by ID."""
    try:
        bank = Bank.objects.get(pk=bank_id)
    except Bank.DoesNotExist:
        return Response({'error': 'bank not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response(BankSerializer(bank).data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bank_status_update(request, bank_id):
    """Update bank status (activate/suspend)."""
    try:
        bank = Bank.objects.get(pk=bank_id)
    except Bank.DoesNotExist:
        return Response({'error': 'bank not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BankStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    bank.status = serializer.validated_data['status']
    bank.last_active_at = timezone.now()
    bank.save()

    return Response(BankSerializer(bank).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bank_compliance(request, bank_id):
    """Get compliance data for a specific bank."""
    try:
        bank = Bank.objects.get(pk=bank_id)
    except Bank.DoesNotExist:
        return Response({'error': 'bank not found'}, status=status.HTTP_404_NOT_FOUND)

    reports = bank.compliance_reports.all()
    from compliance.serializers import ComplianceReportSerializer

    return Response({
        'bank_id': str(bank_id),
        'bank_name': bank.name,
        'report_types': ['rbi_dpsp', 'gdpr_art30', 'pci_dss', 'fiu_ind'],
        'reports': ComplianceReportSerializer(reports, many=True).data,
    })
