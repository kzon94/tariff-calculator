import streamlit as st

from utils.loaders import (
    get_available_destinations,
    get_available_origins,
    get_available_products,
    get_destination_currency,
    get_exchange_rate,
    get_tariff_rate,
    load_exchange_rates,
    load_tariffs,
)
from utils.calculations import calculate_customs_duty_per_ton


st.set_page_config(page_title="Tariff Calculator", layout="centered")

st.title("Tariff Calculator")

COUNTRY_LABELS = {
    "ID": "ID - Indonesia",
    "MY": "MY - Malaysia",
    "PH": "PH - Philippines",
    "EU": "EU - European Union",
    "UK": "UK - United Kingdom",
}


# LOAD DATA
tariffs_df = load_tariffs()
exchange_df = load_exchange_rates()


# SELECT ORIGIN
origins = get_available_origins(tariffs_df)

selected_origin = st.selectbox(
    "Country of origin",
    options=origins,
    format_func=lambda x: COUNTRY_LABELS.get(x, x),
)


# SELECT DESTINATION
destinations = get_available_destinations(tariffs_df, selected_origin)

selected_destination = st.selectbox(
    "Destination",
    options=destinations,
    format_func=lambda x: COUNTRY_LABELS.get(x, x),
)


# SELECT PRODUCT
products = get_available_products(
    tariffs_df,
    selected_origin,
    selected_destination,
)

selected_product = st.selectbox("Product", options=products)


# INPUTS
goods_value = st.number_input("Goods value (USD/t)", min_value=0.0, value=0.0)
freight_value = st.number_input("Freight value (USD/t)", min_value=0.0, value=0.0)


# CALCULATE
if st.button("Calculate"):

    tariff_rate = get_tariff_rate(
        tariffs_df,
        selected_origin,
        selected_destination,
        selected_product,
    )

    exchange_rate = get_exchange_rate(exchange_df, selected_destination)

    currency = get_destination_currency(exchange_df, selected_destination)

    result = calculate_customs_duty_per_ton(
        goods_value,
        freight_value,
        exchange_rate,
        tariff_rate,
    )

    st.success(f"Tariff per ton: {result:.2f} {currency}/t")
