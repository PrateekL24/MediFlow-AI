import re


def clean_text(value: str) -> str:
    """Clean and normalize user input."""

    return " ".join(
        value.strip().lower().split()
    )


def parse_phone(value: str):
    """
    Extract and validate a 10-digit Indian mobile number.

    Examples:
    9999999999
    +91 9999999999
    99999-99999

    Returns:
        phone string if valid
        None otherwise
    """

    digits = re.sub(r"\D", "", value)

    # Remove India country code
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]

    if len(digits) != 10:
        return None

    if not digits.startswith(("6", "7", "8", "9")):
        return None

    return digits


def parse_age(value: str):
    """
    Extract a valid age from user input.

    Examples:
    28
    28 years
    I am 28
    """

    match = re.search(r"\b(\d{1,3})\b", value)

    if not match:
        return None

    age = int(match.group(1))

    if age < 1 or age > 120:
        return None

    return age


def parse_selection(value: str, patients: list):
    """
    Identify a patient from a user's selection.

    Supports:

    1
    1 - Prateek
    Prateek
    I am Prateek

    Returns:
        selected patient
        None if no unambiguous match
    """

    text = clean_text(value)

    # ---------------------------------------
    # Try numeric selection
    # ---------------------------------------

    match = re.match(r"^\s*(\d+)", text)

    if match:

        index = int(match.group(1)) - 1

        if 0 <= index < len(patients):
            return patients[index]

        return None

    # ---------------------------------------
    # Try name matching
    # ---------------------------------------

    matches = []

    for patient in patients:

        first_name = clean_text(
            patient.get("first_name", "")
        )

        last_name = clean_text(
            patient.get("last_name", "")
        )

        full_name = clean_text(
            f"{first_name} {last_name}"
        )

        if first_name and first_name in text:
            matches.append(patient)

        elif full_name and full_name in text:
            matches.append(patient)

    # Only accept an unambiguous match
    if len(matches) == 1:
        return matches[0]

    return None

def parse_registration_input(value: str):
    """
    Extract registration details from a natural user response.

    Examples:
        Raj, 30
        Raj 30
        My name is Raj and I am 30
        I am Raj, age 30

    Returns:
        {
            "first_name": "...",
            "age": 30
        }
    """

    import re

    text = value.strip()

    result = {}

    # ---------------------------------------
    # Extract age
    # ---------------------------------------

    age_match = re.search(
        r"\b(?:age\s*)?(\d{1,3})\s*(?:years?|yrs?)?\b",
        text,
        re.IGNORECASE
    )

    if age_match:

        age = int(age_match.group(1))

        if 1 <= age <= 120:
            result["age"] = age

    # ---------------------------------------
    # Extract first name
    # ---------------------------------------

    name_match = re.search(
        r"(?:my name is|i am|i'm|name is)\s+([A-Za-z]+)",
        text,
        re.IGNORECASE
    )

    if name_match:

        result["first_name"] = name_match.group(1)

    # ---------------------------------------
    # Handle simple format:
    # Raj, 30
    # Raj 30
    # ---------------------------------------

    if "first_name" not in result:

        simple_match = re.match(
            r"^\s*([A-Za-z]+)\s*(?:,|\s)\s*\d{1,3}",
            text
        )

        if simple_match:

            result["first_name"] = (
                simple_match.group(1)
            )

    return result