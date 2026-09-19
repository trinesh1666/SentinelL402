import re
from typing import Dict

import pandas as pd

from app.ml.feature_processor import get_required_features


def canonical_name(name: str) -> str:
    """
    Convert a feature name into a normalized form.

    Example:
        " Destination Port " -> "destinationport"
        "Flow Bytes/s" -> "flowbytess"
    """

    return re.sub(
        r"[^a-z0-9]+",
        "",
        str(name).lower()
    )


def build_column_mapping(
    dataframe: pd.DataFrame
) -> Dict[str, str]:
    """
    Match Random Forest feature names
    to CIC-IDS2017 CSV column names.
    """

    csv_columns = list(dataframe.columns)

    canonical_csv_columns = {
        canonical_name(column): column
        for column in csv_columns
    }

    required_features = get_required_features()

    mapping = {}

    missing_features = []

    for feature in required_features:

        canonical_feature = canonical_name(feature)

        if canonical_feature in canonical_csv_columns:

            mapping[feature] = canonical_csv_columns[
                canonical_feature
            ]

        else:

            missing_features.append(feature)

    if missing_features:

        raise ValueError(
            "The following required ML features "
            "were not found in the CSV:\n\n"
            + "\n".join(missing_features)
        )

    return mapping


def dataframe_to_features(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Convert CIC-IDS2017 dataframe into the
    exact 78-feature dataframe expected
    by the Random Forest model.
    """

    mapping = build_column_mapping(
        dataframe
    )

    required_features = get_required_features()

    result = pd.DataFrame()

    for feature in required_features:

        csv_column = mapping[feature]

        result[feature] = pd.to_numeric(
            dataframe[csv_column],
            errors="coerce"
        )

    result = result.replace(
        [float("inf"), float("-inf")],
        float("nan")
    )

    result = result.fillna(0)

    return result