from __future__ import annotations


def calculate_customs_duty_per_ton(
    goods_value_usd_per_ton: float,
    freight_value_usd_per_ton: float,
    exchange_rate: float,
    tariff_rate: float,
) -> float:
    base_value_usd_per_ton = goods_value_usd_per_ton + freight_value_usd_per_ton
    base_value_destination_currency = base_value_usd_per_ton * exchange_rate
    duty_per_ton = base_value_destination_currency * tariff_rate
    return round(duty_per_ton, 2)


def calculate_base_value_usd_per_ton(
    goods_value_usd_per_ton: float,
    freight_value_usd_per_ton: float,
) -> float:
    return goods_value_usd_per_ton + freight_value_usd_per_ton


def convert_usd_to_destination_currency(
    value_usd: float,
    exchange_rate: float,
) -> float:
    return value_usd * exchange_rate