"""Simple event bus for inter-module communication."""


class EventBus:
    """Publish-subscribe event system."""

    def __init__(self):
        self._listeners = {}

    def subscribe(self, event_name, callback):
        """Subscribe to an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def publish(self, event_name, data=None):
        """Publish an event to all subscribers."""
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"[EventBus] Error in {event_name}: {e}")

    def unsubscribe(self, event_name, callback):
        """Remove a subscriber."""
        if event_name in self._listeners:
            self._listeners[event_name].remove(callback)


event_bus = EventBus()