import streamlit as st

st.set_page_config(page_title="Tariff Calculator")

st.write("App starting...")

# IMPORTS
try:
    from utils.loaders import load_tariffs, load_exchange_rates
    st.write("Imports OK")
except Exception as e:
    st.error(f"IMPORT ERROR: {e}")
    st.stop()

# LOAD DATA
try:
    tariffs_df = load_tariffs()
    st.write("Tariffs loaded")
    st.write(tariffs_df.head())

    exchange_df = load_exchange_rates()
    st.write("Exchange loaded")
    st.write(exchange_df.head())

except Exception as e:
    st.error(f"DATA ERROR: {e}")
    st.stop()

st.success("Everything loaded correctly")
