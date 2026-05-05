from typing import List
from .schemas import ContextSignals

ACTIONS: List[str] = [
    "ASK_REPEAT","SHORT_REPLY","OFFLINE_DEFER","PRIVACY_MASK","VERBOSE_EXPLAIN","HANDS_FREE_MODE",
    "DIRECT_CONFIRM","TOOL_SUMMARY","MEETING_MINUTES","CLARIFY_SLOT",
] + [f"GEN_ACT_{i:02d}" for i in range(1, 25)]
TOPK = 10
SAFE_ACTION = "PRIVACY_MASK"


def gold_action(ctx: ContextSignals, scenario_id: str, turn_id: int = 0) -> str:
    if ctx.privacy_context or ctx.in_meeting:
        return "PRIVACY_MASK"
    if ctx.noise_db > 65:
        return "ASK_REPEAT"
    if ctx.net_quality == "off":
        return "OFFLINE_DEFER"
    if ctx.hands_busy:
        return "HANDS_FREE_MODE"
    if scenario_id == "C5_unknown_interlocutor":
        return "SHORT_REPLY" if turn_id % 2 == 0 else "VERBOSE_EXPLAIN"
    return "VERBOSE_EXPLAIN"


def baseline_naive(ctx: ContextSignals) -> str:
    return "DIRECT_CONFIRM" if ctx.net_quality != "off" else "OFFLINE_DEFER"


def baseline_react_like(ctx: ContextSignals) -> str:
    if ctx.privacy_context or ctx.in_meeting:
        return "PRIVACY_MASK"
    if ctx.noise_db > 65:
        return "ASK_REPEAT"
    if ctx.net_quality == "off":
        return "OFFLINE_DEFER"
    if ctx.hands_busy:
        return "HANDS_FREE_MODE"
    return "SHORT_REPLY"
