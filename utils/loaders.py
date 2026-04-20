from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

REQUIRED_TARIFF_COLUMNS = {"origin", "destination", "tariff", "product"}
REQUIRED_EXCHANGE_COLUMNS = {"origin", "currency", "rates"}


def load_tariffs(file_path: Path | None = None) -> pd.DataFrame:
    path = file_path or DATA_DIR / "tariffs.csv"
    df = pd.read_csv(path)

    df.columns = [column.strip().lower() for column in df.columns]
    _validate_required_columns(df, REQUIRED_TARIFF_COLUMNS, "tariffs.csv")

    df["origin"] = df["origin"].astype(str).str.strip().str.upper()
    df["destination"] = df["destination"].astype(str).str.strip().str.upper()
    df["product"] = df["product"].astype(str).str.strip()
    df["tariff"] = pd.to_numeric(df["tariff"], errors="coerce")

    if df["tariff"].isna().any():
        raise ValueError("Invalid tariff values found in tariffs.csv.")

    duplicated_rows = df.duplicated(subset=["origin", "destination", "product"], keep=False)
    if duplicated_rows.any():
        duplicates = df.loc[duplicated_rows, ["origin", "destination", "product"]]
        raise ValueError(
            "Duplicate origin-destination-product combinations found in tariffs.csv:\n"
            f"{duplicates.to_string(index=False)}"
        )

    return df.sort_values(["origin", "destination", "product"]).reset_index(drop=True)


def load_exchange_rates(file_path: Path | None = None) -> pd.DataFrame:
    path = file_path or DATA_DIR / "exchange_rates.csv"
    df = pd.read_csv(path)

    df.columns = [column.strip().lower() for column in df.columns]
    _validate_required_columns(df, REQUIRED_EXCHANGE_COLUMNS, "exchange_rates.csv")

    df["origin"] = df["origin"].astype(str).str.strip().str.upper()
    df["currency"] = df["currency"].astype(str).str.strip().str.upper()
    df["rates"] = pd.to_numeric(df["rates"], errors="coerce")

    if df["rates"].isna().any():
        raise ValueError("Invalid exchange rate values found in exchange_rates.csv.")

    duplicated_rows = df.duplicated(subset=["origin"], keep=False)
    if duplicated_rows.any():
        duplicates = df.loc[duplicated_rows, ["origin", "currency"]]
        raise ValueError(
            "Duplicate origin values found in exchange_rates.csv:\n"
            f"{duplicates.to_string(index=False)}"
        )

    return df.sort_values(["origin"]).reset_index(drop=True)


def get_available_origins(tariffs_df: pd.DataFrame) -> list[str]:
    return sorted(tariffs_df["origin"].dropna().unique().tolist())


def get_available_destinations(tariffs_df: pd.DataFrame, origin: str) -> list[str]:
    filtered = tariffs_df.loc[tariffs_df["origin"] == origin, "destination"]
    return sorted(filtered.dropna().unique().tolist())


def get_available_products(tariffs_df: pd.DataFrame, origin: str, destination: str) -> list[str]:
    filtered = tariffs_df.loc[
        (tariffs_df["origin"] == origin) & (tariffs_df["destination"] == destination),
        "product",
    ]
    return sorted(filtered.dropna().unique().tolist())


def get_tariff_rate(tariffs_df: pd.DataFrame, origin: str, destination: str, product: str) -> float:
    match = tariffs_df.loc[
        (tariffs_df["origin"] == origin)
        & (tariffs_df["destination"] == destination)
        & (tariffs_df["product"] == product),
        "tariff",
    ]

    if match.empty:
        raise ValueError(
            f"No tariff found for origin='{origin}', destination='{destination}', product='{product}'."
        )

    return float(match.iloc[0])


def get_destination_currency(exchange_df: pd.DataFrame, destination: str) -> str:
    match = exchange_df.loc[exchange_df["origin"] == destination, "currency"]

    if match.empty:
        raise ValueError(f"No currency found for destination '{destination}'.")

    return str(match.iloc[0])


def get_exchange_rate(exchange_df: pd.DataFrame, destination: str) -> float:
    match = exchange_df.loc[exchange_df["origin"] == destination, "rates"]

    if match.empty:
        raise ValueError(f"No exchange rate found for destination '{destination}'.")

    return float(match.iloc[0])


def _validate_required_columns(df: pd.DataFrame, required_columns: set[str], file_name: str) -> None:
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns in {file_name}: {missing}")