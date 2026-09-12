from app.delivery.assignment import DeliveryPartnerCandidate, assign_best_partner, matching_score
from app.delivery.eta import EtaInput, estimate_delivery_minutes


def test_assignment_considers_more_than_distance() -> None:
    candidates = [
        DeliveryPartnerCandidate("near-busy", distance_km=1, active_order_count=5, rating=3.0, acceptance_rate=0.55),
        DeliveryPartnerCandidate("balanced", distance_km=3, active_order_count=0, rating=4.9, acceptance_rate=0.98),
    ]
    result = assign_best_partner(candidates)
    assert result is not None
    assert result.partner_id == "balanced"
    assert result.score == matching_score(candidates[1])


def test_assignment_returns_none_when_every_partner_is_offline() -> None:
    candidates = [DeliveryPartnerCandidate("offline", 1, 0, 5, 1, available=False)]
    assert assign_best_partner(candidates) is None


def test_eta_increases_with_traffic_and_workload() -> None:
    baseline = estimate_delivery_minutes(EtaInput(15, 3, 0, 1, 1.0, 25))
    delayed = estimate_delivery_minutes(EtaInput(15, 3, 4, 1, 1.8, 25))
    assert delayed > baseline
