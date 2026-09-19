CLASS_MAPPING = {
    0: "BENIGN",
    1: "DDoS",
}


def get_class_name(prediction: int) -> str:
    """
    Convert the Random Forest numeric prediction
    into the original CIC-IDS2017 class name.
    """

    if prediction not in CLASS_MAPPING:
        raise ValueError(
            f"Unknown model prediction: {prediction}"
        )

    return CLASS_MAPPING[prediction]