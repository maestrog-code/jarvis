"""Jarvis Safety — HITL gate, killswitch, and anomaly detection."""

from jarvis.safety.hitl import queue_for_approval, approve_item, reject_item
from jarvis.safety.killswitch import engage_auto_kill, is_killed
from jarvis.safety.anomaly import record_request

__all__ = [
    "queue_for_approval",
    "approve_item",
    "reject_item",
    "engage_auto_kill",
    "is_killed",
    "record_request",
]
