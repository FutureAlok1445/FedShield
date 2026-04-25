from django.db.models import Max
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import FederationRound
from .serializers import (
    FederationRoundListSerializer,
    FederationRoundSerializer,
    RoundStartSerializer,
)


@api_view(['GET'])
def round_list(request):
    """List all federation rounds."""
    rounds = FederationRound.objects.all()
    serializer = FederationRoundListSerializer(rounds, many=True)
    return Response({'rounds': serializer.data})


@api_view(['GET'])
def round_detail(request, round_id):
    """Get round details with per-bank updates."""
    try:
        round_obj = FederationRound.objects.prefetch_related('updates').get(pk=round_id)
    except FederationRound.DoesNotExist:
        return Response({'error': 'round not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response(FederationRoundSerializer(round_obj).data)


@api_view(['POST'])
def round_start(request):
    """Start a new federation round."""
    serializer = RoundStartSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    max_round = FederationRound.objects.aggregate(Max('round_number'))['round_number__max'] or 0
    round_obj = FederationRound.objects.create(
        round_number=max_round + 1,
        participants_expected=serializer.validated_data['expected_participants'],
    )

    return Response(FederationRoundSerializer(round_obj).data, status=status.HTTP_201_CREATED)
