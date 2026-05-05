from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class ContextSignals:
    noise_db: float
    asr_conf: float
    net_quality: str
    privacy_context: bool
    hands_busy: bool
    in_meeting: bool
    token_budget: int
    latency_budget_ms: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ContextSignals":
        return cls(**d)


@dataclass
class PartnerModel:
    formality: float = 0.5
    verbosity_pref: float = 0.5
    directness_pref: float = 0.5
    history_window_size: int = 5
    update_rate: float = 0.2
    last_updates: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PartnerModel":
        return cls(**d)


@dataclass
class SharedState:
    active_task: Optional[str] = None
    slots: Dict[str, Any] = field(default_factory=dict)
    commitments: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    last_success: Optional[str] = None
    last_failure: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SharedState":
        return cls(**d)


@dataclass
class PolicyState:
    active_policy: Optional[str] = None
    hysteresis_remaining: int = 0
    cooldown_remaining: int = 0
    switch_count: int = 0
    privacy_events: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PolicyState":
        return cls(**d)


@dataclass
class AgentConfig:
    profiler_enabled: bool = True
    common_ground_enabled: bool = True
    policies_enabled: bool = True
    tom_enabled: bool = True
    cf_enabled: bool = True
    p_cf: float = 0.06

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AgentConfig":
        return cls(**d)
