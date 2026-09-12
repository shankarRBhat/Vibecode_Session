from dataclasses import dataclass


@dataclass(frozen=True)
class DeliveryPartnerCandidate:
    partner_id: str
    distance_km: float
    active_order_count: int
    rating: float
    acceptance_rate: float
    available: bool = True


@dataclass(frozen=True)
class AssignmentResult:
    partner_id: str
    score: float
    reason: str


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def matching_score(candidate: DeliveryPartnerCandidate) -> float:
    distance_score = 1 - _clamp(candidate.distance_km / 10)
    availability_score = 1.0 if candidate.available else 0.0
    workload_score = 1 - _clamp(candidate.active_order_count / 5)
    performance_score = (_clamp(candidate.rating / 5) * 0.6) + (_clamp(candidate.acceptance_rate) * 0.4)
    return (distance_score * 0.35) + (availability_score * 0.2) + (workload_score * 0.2) + (performance_score * 0.25)


def assign_best_partner(candidates: list[DeliveryPartnerCandidate]) -> AssignmentResult | None:
    eligible = [candidate for candidate in candidates if candidate.available]
    if not eligible:
        return None
    selected = max(eligible, key=matching_score)
    score = matching_score(selected)
    return AssignmentResult(
        partner_id=selected.partner_id,
        score=round(score, 4),
        reason=f"Selected using distance, availability, workload, rating, and acceptance rate (score {score:.2f})",
    )
