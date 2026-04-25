from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AuditEntry
from .serializers import AuditEntrySerializer


@api_view(['GET'])
def audit_list(request):
    """List audit trail entries."""
    entries = AuditEntry.objects.select_related('bank').all()
    serializer = AuditEntrySerializer(entries, many=True)
    return Response({'entries': serializer.data})


@api_view(['GET'])
def audit_detail(request, entry_id):
    """Get a specific audit entry."""
    try:
        entry = AuditEntry.objects.get(pk=entry_id)
    except AuditEntry.DoesNotExist:
        return Response({'error': 'entry not found'}, status=404)

    return Response(AuditEntrySerializer(entry).data)
