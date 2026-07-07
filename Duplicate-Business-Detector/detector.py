import pandas as pd
from rapidfuzz import fuzz
import re


def normalize_phone(phone):
    """Remove spaces, dashes and special characters from phone numbers."""
    return re.sub(r"\D", "", str(phone))


def get_recommendation(name_score, address_score, phone_match):

    if name_score >= 95 and phone_match:
        return "Safe to Merge", "High"

    elif name_score >= 85 and (phone_match or address_score >= 85):
        return "Review Manually", "Medium"

    else:
        return "Not a Duplicate", "Low"


def detect_duplicates(csv_path):

    # Read CSV
    df = pd.read_csv(csv_path)

    # Check empty CSV
    if df.empty:
        raise Exception("The uploaded CSV is empty.")

    # Remove completely blank rows
    df.dropna(how="all", inplace=True)

    # Replace NaN values
    df.fillna("", inplace=True)

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    # Dictionary of lowercase column names
    columns = {col.lower(): col for col in df.columns}

    # Possible business name columns
    business_options = [
        "businessname",
        "business name",
        "business_name",
        "company",
        "company name",
        "name"
    ]

    # Possible phone columns
    phone_options = [
        "phone",
        "phone number",
        "mobile",
        "mobile number",
        "contact",
        "contact number"
    ]

    # Possible address columns
    address_options = [
        "address",
        "location",
        "business address"
    ]

    business_col = None
    phone_col = None
    address_col = None

    # Detect Business column
    for option in business_options:
        if option in columns:
            business_col = columns[option]
            break

    # Detect Phone column
    for option in phone_options:
        if option in columns:
            phone_col = columns[option]
            break

    # Detect Address column
    for option in address_options:
        if option in columns:
            address_col = columns[option]
            break

    # Required columns check
    if business_col is None:
        raise Exception("Business Name column not found.")

    if phone_col is None:
        raise Exception("Phone column not found.")

    if address_col is None:
        raise Exception("Address column not found.")

    duplicates = []

    threshold = 85

    total_records = len(df)

    for i in range(total_records):

        for j in range(i + 1, total_records):

            name1 = str(df.loc[i, business_col]).strip()
            name2 = str(df.loc[j, business_col]).strip()

            phone1 = normalize_phone(df.loc[i, phone_col])
            phone2 = normalize_phone(df.loc[j, phone_col])

            address1 = str(df.loc[i, address_col]).strip()
            address2 = str(df.loc[j, address_col]).strip()

            # Skip blank business names
            if name1 == "" or name2 == "":
                continue

            # Similarity scores
            name_score = fuzz.ratio(
                name1.lower(),
                name2.lower()
            )

            address_score = fuzz.ratio(
                address1.lower(),
                address2.lower()
            )

            phone_match = (
                phone1 != ""
                and phone1 == phone2
            )

            if (
                name_score >= threshold
                or
                (phone_match and address_score >= 80)
            ):

                recommendation, confidence = get_recommendation(
                    name_score,
                    address_score,
                    phone_match
                )

                duplicates.append({

                    "business1": name1,

                    "business2": name2,

                    "name_score": round(name_score, 2),

                    "address_score": round(address_score, 2),

                    "phone_match": "Yes" if phone_match else "No",

                    "recommendation": recommendation,

                    "confidence": confidence

                })

    # Generate report
    report = pd.DataFrame(duplicates)

    report.to_csv(
        "duplicate_report.csv",
        index=False
    )

    stats = {

        "total": total_records,

        "duplicates": len(duplicates),

        "unique": total_records - len(duplicates),

        "threshold": threshold

    }

    return duplicates, stats