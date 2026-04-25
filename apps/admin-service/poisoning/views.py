from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import PoisoningEvent
from .serializers import PoisoningEventSerializer


@api_view(['GET'])
def poisoning_list(request):
    """List all poisoning events."""
    events = PoisoningEvent.objects.select_related('bank', 'round').all()
    serializer = PoisoningEventSerializer(events, many=True)
    return Response({'events': serializer.data})


@api_view(['GET'])
def poisoning_detail(request, event_id):
    """Get poisoning event details."""
    try:
        event = PoisoningEvent.objects.select_related('bank', 'round', 'update').get(pk=event_id)
    except PoisoningEvent.DoesNotExist:
        return Response({'error': 'event not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response(PoisoningEventSerializer(event).data)
