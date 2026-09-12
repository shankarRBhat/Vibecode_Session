from dataclasses import dataclass


@dataclass(frozen=True)
class EtaInput:
    preparation_minutes: int
    restaurant_to_customer_km: float
    active_order_count: int
    partner_to_restaurant_km: float
    traffic_factor: float = 1.0
    historical_delivery_minutes: int = 30


def estimate_delivery_minutes(data: EtaInput) -> int:
    travel_minutes = (data.restaurant_to_customer_km + data.partner_to_restaurant_km) * 4.0
    traffic_adjustment = max(1.0, data.traffic_factor)
    workload_buffer = min(20.0, max(0, data.active_order_count) * 2.0)
    historical_signal = max(0.0, data.historical_delivery_minutes * 0.15)
    estimate = data.preparation_minutes + (travel_minutes * traffic_adjustment) + workload_buffer + historical_signal
    return max(1, round(estimate))
