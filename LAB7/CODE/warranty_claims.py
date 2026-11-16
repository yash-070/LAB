
import math


def parse_claim(text):
    # Validate input type
    if not isinstance(text, str):
        return ("", 0.0)

    # Ensure exactly one colon is present
    parts = text.split(':')

    if len(parts) != 2:
        return ("", 0.0)

    plan, months = parts
    plan = plan.strip()

    # Plan name cannot be empty
    if not plan:
        return ("", 0.0)

    # Validate months
    try:
        months = float(months.strip())
    except (ValueError, OverflowError):
        return ("", 0.0)

    # Reject negative, infinite and NaN values
    if not math.isfinite(months) or months < 0:
        return ("", 0.0)

    return plan.title(), months


def age_average(ages_csv):
    # Validate input type
    if not isinstance(ages_csv, str):
        return 0

    if not ages_csv.strip():
        return 0

    # Convert CSV values into integers
    try:
        values = [int(r.strip()) for r in ages_csv.split(',')]
    except (ValueError, OverflowError):
        return 0

    # Reject negative ages
    if not values or any(age < 0 for age in values):
        return 0

    return sum(values) // len(values)


def payable_charge(text):
    # Validate input type
    if not isinstance(text, str):
        return 0.0

    # Ensure exactly one separator
    parts = text.split('|')

    if len(parts) != 2:
        return 0.0

    charge, discount = parts

    # Convert values to floating-point numbers
    try:
        charge = float(charge.strip())
        discount = float(discount.strip())
    except (ValueError, OverflowError):
        return 0.0

    # Reject negative and non-finite values
    if not math.isfinite(charge) or not math.isfinite(discount):
        return 0.0

    if charge < 0 or discount < 0:
        return 0.0

    # Calculate payable amount
    total = charge * 1.18 - discount

    if not math.isfinite(total):
        return 0.0

    return max(total, 0.0)


def main():
    print("==== Running parse_claim ====")
    user_input = input("Enter plan:age in months (e.g. standard:30): ")
    result = parse_claim(user_input)
    print("Plan and Age:", result)

    print("\n==== Running age_average ====")
    user_input = input("Enter product ages as CSV (e.g. 12,24,36): ")
    result = age_average(user_input)
    print("Average Age:", result)

    print("\n==== Running payable_charge ====")
    user_input = input("Enter charge|discount (e.g. 1500|200): ")
    result = payable_charge(user_input)
    print("Payable Charge:", result)


if __name__ == "__main__":
    main()
