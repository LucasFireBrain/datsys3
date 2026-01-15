# Reference price list: Región anatómica + Complejidad

PRICES = {
    "Ángulo Mandibular": {
        "A": 600_000,
        "B": 680_000,
        "C": 900_000,
        "D": 1_080_000,
    },
    "Cigomático": {
        "A": 480_000,
        "B": 580_000,
        "C": 680_000,
        "D": 840_000,
    },
    "Infraorbitario": {
        "A": 480_000,
        "B": 580_000,
        "C": 680_000,
        "D": 840_000,
    },
    "Injerto Facial": {
        "A": 650_000,
        "B": 780_000,
        "C": 980_000,
        "D": 1_170_000,
    },
    "Mentón": {
        "A": 600_000,
        "B": 720_000,
        "C": 900_000,
        "D": 1_080_000,
    },
    "Paranasales": {
        "A": 400_000,
        "B": 500_000,
        "C": 600_000,
        "D": 700_000,
    },
    "Piso de Órbita": {
        "A": 630_000,
        "B": 750_000,
        "C": 945_000,
        "D": 1_130_000,
    },
    "Reborde Infraorbitario": {
        "A": 700_000,
        "B": 840_000,
        "C": 1_050_000,
        "D": 1_250_000,
    },
    "Supraorbital": {
        "A": 840_000,
        "B": 1_000_000,
        "C": 1_260_000,
        "D": 1_500_000,
    },
    "Personalizado": {
        "A": 600_000,
        "B": 780_000,
        "C": 980_000,
        "D": 1_280_000,
    },
}


def list_regions():
    return list(PRICES.keys())


def get_price(region: str, complexity: str) -> int:
    complexity = complexity.upper()
    if region not in PRICES:
        raise ValueError(f"Unknown region: {region}")
    if complexity not in PRICES[region]:
        raise ValueError(f"Invalid complexity: {complexity}")
    return PRICES[region][complexity]
