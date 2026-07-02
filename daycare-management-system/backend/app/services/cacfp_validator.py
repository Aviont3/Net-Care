"""
USDA CACFP Meal Pattern Validator
==================================
Validates logged meal food_components dicts against official USDA CACFP
meal pattern requirements for child care centers.

Reference: 7 CFR Part 226 / USDA FNS CACFP meal pattern (2017 update)
"""
from datetime import date
from typing import Optional


# ---------------------------------------------------------------------------
# Meal pattern requirements
# ---------------------------------------------------------------------------

# For breakfast, lunch, and supper the dict maps component key -> True/False
# or True/str (truthy value means the component was served).
# For snack, any 2 of the 5 components satisfy the requirement.

MEAL_REQUIREMENTS: dict = {
    "breakfast": {
        "required": ["milk", "fruit_or_vegetable", "grains"],
        "min_components": 3,
    },
    "lunch": {
        "required": ["milk", "meat_alternate", "vegetable", "fruit", "grains"],
        "min_components": 5,
    },
    "supper": {
        "required": ["milk", "meat_alternate", "vegetable", "fruit", "grains"],
        "min_components": 5,
    },
    "snack": {
        "required_any_two_of": ["milk", "meat_alternate", "vegetable", "fruit", "grains"],
        "min_components": 2,
    },
}

# Per USDA rules, juice/fruit + milk is NOT a reimbursable snack combo on its own.
SNACK_RESTRICTIONS = [
    {
        "forbidden_combo": frozenset({"milk", "fruit"}),
        "note": "Milk and juice/fruit cannot be the only two snack components per USDA rules.",
    }
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_meal(
    meal_type: str,
    food_components: dict,
    child_dob: Optional[date] = None,
) -> dict:
    """
    Validate a meal against USDA CACFP meal pattern requirements.

    Args:
        meal_type: One of 'breakfast', 'lunch', 'supper', 'snack'.
        food_components: Dict mapping component name to a truthy value (bool or
            description string) when served, or None/False when not served.
            Expected keys: milk, grains, fruit, vegetable, meat_alternate.
        child_dob: (reserved) Future use for age-based serving-size validation.

    Returns:
        {
            "compliant": bool,
            "notes": str,           # empty string when compliant
            "missing_components": list[str],
        }
    """
    if meal_type not in MEAL_REQUIREMENTS:
        return {
            "compliant": False,
            "notes": f"Invalid meal type: '{meal_type}'. Must be one of: {', '.join(MEAL_REQUIREMENTS)}.",
            "missing_components": [],
        }

    requirements = MEAL_REQUIREMENTS[meal_type]
    # Normalise: treat any truthy value (True, non-empty string) as "present"
    present = {k for k, v in food_components.items() if v}

    if meal_type == "snack":
        return _validate_snack(present, requirements)
    else:
        return _validate_full_meal(present, requirements)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_snack(present: set, requirements: dict) -> dict:
    valid = [c for c in present if c in requirements["required_any_two_of"]]

    if len(valid) < requirements["min_components"]:
        return {
            "compliant": False,
            "notes": (
                f"Snack requires at least {requirements['min_components']} components "
                f"from: {', '.join(requirements['required_any_two_of'])}. "
                f"Found {len(valid)}: {', '.join(valid) or 'none'}."
            ),
            "missing_components": [],
        }

    # Restriction check: milk + fruit/juice only is not reimbursable
    valid_set = frozenset(valid)
    for restriction in SNACK_RESTRICTIONS:
        if valid_set == restriction["forbidden_combo"]:
            return {
                "compliant": False,
                "notes": restriction["note"],
                "missing_components": [],
            }

    return {"compliant": True, "notes": "", "missing_components": []}


def _validate_full_meal(present: set, requirements: dict) -> dict:
    missing = []

    for req in requirements["required"]:
        if req == "fruit_or_vegetable":
            if "fruit" not in present and "vegetable" not in present:
                missing.append("fruit or vegetable")
        elif req not in present:
            missing.append(req)

    if missing:
        return {
            "compliant": False,
            "notes": f"Missing required component(s): {', '.join(missing)}.",
            "missing_components": missing,
        }

    return {"compliant": True, "notes": "", "missing_components": []}
