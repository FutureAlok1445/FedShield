"""Per-bank gradient norm history tracker for Layer 3 anomaly detection."""

from collections import defaultdict, deque


class HistoryTracker:
    """Keeps a sliding window of gradient norms per bank."""

    def __init__(self, max_rounds: int = 10):
        self._max = max_rounds
        self._data: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_rounds))

    def record(self, bank_id: str, value: float) -> None:
        self._data[bank_id].append(value)

    def values(self, bank_id: str) -> list[float]:
        return list(self._data.get(bank_id, []))

    def clear(self, bank_id: str | None = None) -> None:
        if bank_id:
            self._data.pop(bank_id, None)
        else:
            self._data.clear()
