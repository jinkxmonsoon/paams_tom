from typing import Tuple
from .schemas import ContextSignals, PolicyState


def _trigger(ctx: ContextSignals):
    if ctx.privacy_context or ctx.in_meeting:
        return "privacy_masking", "privacy or meeting"
    if ctx.noise_db > 65:
        return "short_reply", "high noise"
    if ctx.net_quality in {"poor", "off"}:
        return "offload_gating", "network constrained"
    return None, "no trigger"


def apply_policy(ctx: ContextSignals, state: PolicyState) -> Tuple[str, str]:
    desired, reason = _trigger(ctx)
    prev = state.active_policy

    if state.hysteresis_remaining > 0 and prev is not None:
        chosen = prev
        reason = f"hysteresis hold ({prev})"
    else:
        chosen = desired
        if desired is not None and prev == desired and state.cooldown_remaining > 0:
            chosen = prev
            reason = f"cooldown continuing ({prev})"

    if chosen != prev:
        state.switch_count += 1
        if prev is not None and chosen is None:
            state.cooldown_remaining = 3
        state.hysteresis_remaining = 2 if chosen is not None else 0
    else:
        state.hysteresis_remaining = max(0, state.hysteresis_remaining - 1)

    state.cooldown_remaining = max(0, state.cooldown_remaining - 1)
    state.active_policy = chosen

    if state.active_policy == "privacy_masking":
        state.privacy_events += 1
    return chosen, reason
