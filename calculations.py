from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


REQUIRED_TARIFF_COLUMNS = {"origin", "destination", "tariff", "product"}
REQUIRED_EXCHANGE_COLUMNS = {"origin", "currency", "rates"}


COUNTRY_LABELS = {
    "ID": "ID - Indonesia",
    "MY": "MY - Malaysia",
    "PH": "PH - Philippines",
    "EU": "EU - European Union",
    "UK": "UK - United Kingdom",
}


class DataValidationError(Exception):
    pass



def _read_csv(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise DataValidationError(f"Missing data file: {file_path}")

    return pd.read_csv(file_path)



def load_tariffs() -> pd.DataFrame:
    file_path = DATA_DIR / "tariffs.csv"
    df = _read_csv(file_path)
    df.columns = [column.strip().lower() for column in df.columns]

    missing_columns = REQUIRED_TARIFF_COLUMNS - set(df.columns)
    if missing_columns:
        raise DataValidationError(
            f"tariffs.csv is missing required columns: {', '.join(sorted(missing_columns))}"
        )

    df["origin"] = df["origin"].astype(str).str.strip().str.upper()
    df["destination"] = df["destination"].astype(str).str.strip().str.upper()
    df["product"] = df["product"].astype(str).str.strip()
    df["tariff"] = pd.to_numeric(df["tariff"], errors="raise")

    duplicated_rows = df.duplicated(subset=["origin", "destination", "product"], keep=False)
    if duplicated_rows.any():
        duplicates = df.loc[duplicated_rows, ["origin", "destination", "product"]]
        raise DataValidationError(
            "Duplicate origin/destination/product combinations found in tariffs.csv:\n"
            f"{duplicates.to_string(index=False)}"
        )

    return df.sort_values(["origin", "destination", "product"]).reset_index(drop=True)



def load_exchange_rates() -> pd.DataFrame:
    file_path = DATA_DIR / "exchange_rates.csv"
    df = _read_csv(file_path)
    df.columns = [column.strip().lower() for column in df.columns]

    missing_columns = REQUIRED_EXCHANGE_COLUMNS - set(df.columns)
    if missing_columns:
        raise DataValidationError(
            f"exchange_rates.csv is missing required columns: {', '.join(sorted(missing_columns))}"
        )

    df["origin"] = df["origin"].astype(str).str.strip().str.upper()
    df["currency"] = df["currency"].astype(str).str.strip().str.upper()
    df["rates"] = pd.to_numeric(df["rates"], errors="raise")

    duplicated_rows = df.duplicated(subset=["origin"], keep=False)
    if duplicated_rows.any():
        duplicates = df.loc[duplicated_rows, ["origin", "currency"]]
        raise DataValidationError(
            "Duplicate destination currency rows found in exchange_rates.csv:\n"
            f"{duplicates.to_string(index=False)}"
        )

    return df.sort_values(["origin"]).reset_index(drop=True)



def get_origin_options(tariffs_df: pd.DataFrame) -> list[str]:
    return sorted(tariffs_df["origin"].unique().tolist())



def get_destination_options(tariffs_df: pd.DataFrame, origin: str) -> list[str]:
    filtered_df = tariffs_df.loc[tariffs_df["origin"] == origin]
    return sorted(filtered_df["destination"].unique().tolist())



def get_product_options(tariffs_df: pd.DataFrame, origin: str, destination: str) -> list[str]:
    filtered_df = tariffs_df.loc[
        (tariffs_df["origin"] == origin) & (tariffs_df["destination"] == destination)
    ]
    return filtered_df["product"].tolist()



def get_country_label(code: str) -> str:
    return COUNTRY_LABELS.get(code, code)



def get_tariff_record(tariffs_df: pd.DataFrame, origin: str, destination: str, product: str) -> pd.Series:
    record = tariffs_df.loc[
        (tariffs_df["origin"] == origin)
        & (tariffs_df["destination"] == destination)
        & (tariffs_df["product"] == product)
    ]

    if record.empty:
        raise DataValidationError(
            f"No tariff found for origin={origin}, destination={destination}, product={product}"
        )

    return record.iloc[0]



def get_exchange_rate(exchange_df: pd.DataFrame, destination: str) -> tuple[float, str]:
    record = exchange_df.loc[exchange_df["origin"] == destination]

    if record.empty:
        raise DataValidationError(f"No exchange rate found for destination={destination}")

    return float(record.iloc[0]["rates"]), str(record.iloc[0]["currency"])
