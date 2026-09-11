import json


def normalize_validation_number(value):
    """
    Convert financial values into numbers before validation.

    Examples:
        "3,49" -> 3.49
        "126,27" -> 126.27
        "10%" -> 10.0
        25 -> 25
        None -> None
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        value = value.strip()
        value = value.replace("%", "")
        value = value.replace(",", ".")

        try:
            return float(value)
        except ValueError:
            return None

    return None


def validate_invoice_items(items: list[dict]) -> list[dict]:
    """
    Validate that quantity × unit price approximately equals
    net value for each invoice item.
    """

    checks = []

    for index, item in enumerate(items, start=1):

        quantity = normalize_validation_number(
            item.get("quantity")
        )

        unit_price = normalize_validation_number(
            item.get("unit_price")
        )

        net_value = normalize_validation_number(
            item.get("net_value")
        )

        if quantity is None or unit_price is None or net_value is None:

            checks.append({
                "check": (
                    f"Line item {index}: "
                    "quantity × unit price = net value"
                ),
                "formula": "quantity × unit_price",
                "inputs": {
                    "quantity": quantity,
                    "unit_price": unit_price
                },
                "calculated_value": None,
                "reported_value": net_value,
                "variance": None,
                "status": "NOT_APPLICABLE"
            })

            continue

        calculated_value = quantity * unit_price

        variance = calculated_value - net_value

        passed = abs(variance) <= 0.01

        checks.append({
            "check": (
                f"Line item {index}: "
                "quantity × unit price = net value"
            ),
            "formula": "quantity × unit_price",
            "inputs": {
                "quantity": quantity,
                "unit_price": unit_price
            },
            "calculated_value": round(calculated_value, 2),
            "reported_value": round(net_value, 2),
            "variance": round(variance, 2),
            "status": "PASS" if passed else "FAIL"
        })

    return checks


def validate_invoice_net_total(
    items: list[dict],
    reported_net_total
) -> dict:
    """
    Validate that the sum of invoice line-item net values
    approximately equals the reported net total.
    """

    reported_net_total = normalize_validation_number(
        reported_net_total
    )

    if reported_net_total is None:

        return {
            "check": "Sum of line item net values = net total",
            "formula": "sum(item.net_value)",
            "inputs": {
                "line_item_net_values": []
            },
            "calculated_value": None,
            "reported_value": None,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }

    net_values = []

    for item in items:

        net_value = normalize_validation_number(
            item.get("net_value")
        )

        if net_value is not None:
            net_values.append(net_value)

    if not net_values:

        return {
            "check": "Sum of line item net values = net total",
            "formula": "sum(item.net_value)",
            "inputs": {
                "line_item_net_values": []
            },
            "calculated_value": None,
            "reported_value": reported_net_total,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }

    calculated_value = sum(net_values)

    variance = calculated_value - reported_net_total

    passed = abs(variance) <= 0.01

    return {
        "check": "Sum of line item net values = net total",
        "formula": "sum(item.net_value)",
        "inputs": {
            "line_item_net_values": net_values
        },
        "calculated_value": round(calculated_value, 2),
        "reported_value": round(reported_net_total, 2),
        "variance": round(variance, 2),
        "status": "PASS" if passed else "FAIL"
    }


def validate_invoice_vat(
    net_total,
    vat_rate,
    reported_vat_total
) -> dict:
    """
    Validate that net total × VAT rate approximately equals
    the reported VAT total.
    """

    net_total = normalize_validation_number(net_total)

    vat_rate = normalize_validation_number(vat_rate)

    reported_vat_total = normalize_validation_number(
        reported_vat_total
    )

    if (
        net_total is None
        or vat_rate is None
        or reported_vat_total is None
    ):

        return {
            "check": "Net total × VAT rate = VAT total",
            "formula": "net_total × vat_rate",
            "inputs": {
                "net_total": net_total,
                "vat_rate": vat_rate
            },
            "calculated_value": None,
            "reported_value": reported_vat_total,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }

    calculated_value = net_total * (vat_rate / 100)

    variance = calculated_value - reported_vat_total

    passed = abs(variance) <= 0.01

    return {
        "check": "Net total × VAT rate = VAT total",
        "formula": "net_total × vat_rate",
        "inputs": {
            "net_total": net_total,
            "vat_rate": vat_rate
        },
        "calculated_value": round(calculated_value, 2),
        "reported_value": round(reported_vat_total, 2),
        "variance": round(variance, 2),
        "status": "PASS" if passed else "FAIL"
    }


def validate_invoice_gross_total(
    net_total,
    vat_total,
    reported_gross_total
) -> dict:
    """
    Validate that net total + VAT total approximately equals
    the reported gross total.
    """

    net_total = normalize_validation_number(net_total)

    vat_total = normalize_validation_number(vat_total)

    reported_gross_total = normalize_validation_number(
        reported_gross_total
    )

    if (
        net_total is None
        or vat_total is None
        or reported_gross_total is None
    ):

        return {
            "check": "Net total + VAT total = gross total",
            "formula": "net_total + vat_total",
            "inputs": {
                "net_total": net_total,
                "vat_total": vat_total
            },
            "calculated_value": None,
            "reported_value": reported_gross_total,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }

    calculated_value = net_total + vat_total

    variance = calculated_value - reported_gross_total

    passed = abs(variance) <= 0.01

    return {
        "check": "Net total + VAT total = gross total",
        "formula": "net_total + vat_total",
        "inputs": {
            "net_total": net_total,
            "vat_total": vat_total
        },
        "calculated_value": round(calculated_value, 2),
        "reported_value": round(reported_gross_total, 2),
        "variance": round(variance, 2),
        "status": "PASS" if passed else "FAIL"
    }


def validate_balance_sheet(
    capital_and_liabilities_total,
    assets_total
) -> dict:
    """
    Validate that total capital and liabilities
    approximately equals total assets.
    """

    if (
        capital_and_liabilities_total is None
        or assets_total is None
    ):

        return {
            "check": "Capital and Liabilities = Assets",
            "formula": "capital_and_liabilities_total",
            "inputs": {
                "capital_and_liabilities_total":
                    capital_and_liabilities_total,
                "assets_total": assets_total
            },
            "calculated_value": None,
            "reported_value": assets_total,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }

    if (
        isinstance(capital_and_liabilities_total, list)
        and isinstance(assets_total, list)
    ):

        results = []

        for index, (liabilities, assets) in enumerate(
            zip(
                capital_and_liabilities_total,
                assets_total
            )
        ):

            liabilities = normalize_validation_number(
                liabilities
            )

            assets = normalize_validation_number(
                assets
            )

            if liabilities is None or assets is None:

                results.append({
                    "period_index": index,
                    "check": "Capital and Liabilities = Assets",
                    "formula": "capital_and_liabilities_total",
                    "inputs": {
                        "capital_and_liabilities_total":
                            liabilities,
                        "assets_total":
                            assets
                    },
                    "calculated_value": None,
                    "reported_value": assets,
                    "variance": None,
                    "status": "NOT_APPLICABLE"
                })

                continue

            variance = liabilities - assets

            passed = abs(variance) <= 0.01

            results.append({
                "period_index": index,
                "check": "Capital and Liabilities = Assets",
                "formula": "capital_and_liabilities_total",
                "inputs": {
                    "capital_and_liabilities_total":
                        liabilities,
                    "assets_total":
                        assets
                },
                "calculated_value": round(
                    liabilities,
                    2
                ),
                "reported_value": round(
                    assets,
                    2
                ),
                "variance": round(
                    variance,
                    2
                ),
                "status": "PASS" if passed else "FAIL"
            })

        return results

    capital_and_liabilities_total = normalize_validation_number(
        capital_and_liabilities_total
    )

    assets_total = normalize_validation_number(
        assets_total
    )

    if (
        capital_and_liabilities_total is None
        or assets_total is None
    ):

        return {
            "check": "Capital and Liabilities = Assets",
            "formula": "capital_and_liabilities_total",
            "inputs": {
                "capital_and_liabilities_total":
                    capital_and_liabilities_total,
                "assets_total":
                    assets_total
            },
            "calculated_value": None,
            "reported_value": assets_total,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }

    variance = (
        capital_and_liabilities_total
        - assets_total
    )

    passed = abs(variance) <= 0.01

    return {
        "check": "Capital and Liabilities = Assets",
        "formula": "capital_and_liabilities_total",
        "inputs": {
            "capital_and_liabilities_total":
                capital_and_liabilities_total,
            "assets_total":
                assets_total
        },
        "calculated_value": round(
            capital_and_liabilities_total,
            2
        ),
        "reported_value": round(
            assets_total,
            2
        ),
        "variance": round(
            variance,
            2
        ),
        "status": "PASS" if passed else "FAIL"
    }


def validate_profit_and_loss(period: dict) -> list[dict]:
    """
    Validate the main financial relationships
    in one Profit & Loss period.
    """

    checks = []

    if not isinstance(period, dict):
        return [{
            "check": "Profit & Loss validation",
            "formula": "period-based financial validation",
            "inputs": {},
            "calculated_value": None,
            "reported_value": None,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }]

    income = period.get("income", {})

    expenditure = period.get(
        "expenditure",
        {}
    )

    profit = period.get(
        "profit",
        {}
    )

    if not isinstance(income, dict):
        income = {}

    if not isinstance(expenditure, dict):
        expenditure = {}

    if not isinstance(profit, dict):
        profit = {}

    interest_earned = normalize_validation_number(
        income.get("interest_earned")
    )

    other_income = normalize_validation_number(
        income.get("other_income")
    )

    total_income = normalize_validation_number(
        income.get("total_income")
    )

    if (
        interest_earned is not None
        and other_income is not None
        and total_income is not None
    ):

        calculated = (
            interest_earned
            + other_income
        )

        variance = calculated - total_income

        checks.append({
            "check":
                "Interest Earned + Other Income = Total Income",
            "formula":
                "interest_earned + other_income",
            "inputs": {
                "interest_earned": interest_earned,
                "other_income": other_income
            },
            "calculated_value": round(
                calculated,
                2
            ),
            "reported_value": round(
                total_income,
                2
            ),
            "variance": round(
                variance,
                2
            ),
            "status":
                "PASS"
                if abs(variance) <= 0.01
                else "FAIL"
        })

    interest_expended = normalize_validation_number(
        expenditure.get("interest_expended")
    )

    operating_expenses = normalize_validation_number(
        expenditure.get("operating_expenses")
    )

    provisions = normalize_validation_number(
        expenditure.get(
            "provisions_and_contingencies"
        )
    )

    total_expenditure = normalize_validation_number(
        expenditure.get("total_expenditure")
    )

    if (
        interest_expended is not None
        and operating_expenses is not None
        and provisions is not None
        and total_expenditure is not None
    ):

        calculated = (
            interest_expended
            + operating_expenses
            + provisions
        )

        variance = calculated - total_expenditure

        checks.append({
            "check":
                "Interest Expended + Operating Expenses + "
                "Provisions and Contingencies = Total Expenditure",
            "formula":
                "interest_expended + operating_expenses + "
                "provisions_and_contingencies",
            "inputs": {
                "interest_expended": interest_expended,
                "operating_expenses": operating_expenses,
                "provisions_and_contingencies": provisions
            },
            "calculated_value": round(
                calculated,
                2
            ),
            "reported_value": round(
                total_expenditure,
                2
            ),
            "variance": round(
                variance,
                2
            ),
            "status":
                "PASS"
                if abs(variance) <= 0.01
                else "FAIL"
        })

    net_profit_before_minority = normalize_validation_number(
        profit.get(
            "consolidated_net_profit_before_minority_interest"
        )
    )

    if (
        total_income is not None
        and total_expenditure is not None
        and net_profit_before_minority is not None
    ):

        calculated = (
            total_income
            - total_expenditure
        )

        variance = calculated - net_profit_before_minority

        checks.append({
            "check":
                "Total Income - Total Expenditure = "
                "Consolidated Net Profit Before Minority Interest",
            "formula":
                "total_income - total_expenditure",
            "inputs": {
                "total_income": total_income,
                "total_expenditure": total_expenditure
            },
            "calculated_value": round(
                calculated,
                2
            ),
            "reported_value": round(
                net_profit_before_minority,
                2
            ),
            "variance": round(
                variance,
                2
            ),
            "status":
                "PASS"
                if abs(variance) <= 0.01
                else "FAIL"
        })

    minority_interest = normalize_validation_number(
        profit.get("minority_interest")
    )

    net_profit_group = normalize_validation_number(
        profit.get(
            "net_profit_attributable_to_group"
        )
    )

    if (
        net_profit_before_minority is not None
        and minority_interest is not None
        and net_profit_group is not None
    ):

        calculated = (
            net_profit_before_minority
            - minority_interest
        )

        variance = calculated - net_profit_group

        checks.append({
            "check":
                "Net Profit Before Minority Interest - "
                "Minority Interest = Net Profit Attributable to Group",
            "formula":
                "net_profit_before_minority_interest - minority_interest",
            "inputs": {
                "net_profit_before_minority_interest":
                    net_profit_before_minority,
                "minority_interest":
                    minority_interest
            },
            "calculated_value": round(
                calculated,
                2
            ),
            "reported_value": round(
                net_profit_group,
                2
            ),
            "variance": round(
                variance,
                2
            ),
            "status":
                "PASS"
                if abs(variance) <= 0.01
                else "FAIL"
        })

    return checks


def validate_cash_flow(period: dict) -> list[dict]:
    """
    Validate the main financial relationships
    in one Cash Flow statement period.
    """

    checks = []

    if not isinstance(period, dict):
        return [{
            "check": "Cash Flow validation",
            "formula": "period-based financial validation",
            "inputs": {},
            "calculated_value": None,
            "reported_value": None,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }]

    operating = period.get(
        "operating_activities",
        {}
    )

    investing = period.get(
        "investing_activities",
        {}
    )

    financing = period.get(
        "financing_activities",
        {}
    )

    if not isinstance(operating, dict):
        operating = {}

    if not isinstance(investing, dict):
        investing = {}

    if not isinstance(financing, dict):
        financing = {}

    operating_cash = normalize_validation_number(
        operating.get(
            "net_cash_from_operating_activities"
        )
    )

    investing_cash = normalize_validation_number(
        investing.get(
            "net_cash_from_investing_activities"
        )
    )

    financing_cash = normalize_validation_number(
        financing.get(
            "net_cash_from_financing_activities"
        )
    )

    fx_adjustment = normalize_validation_number(
        period.get(
            "foreign_exchange_adjustment"
        )
    )

    reported_net_increase = normalize_validation_number(
        period.get(
            "net_increase_in_cash"
        )
    )

    if (
        operating_cash is not None
        and investing_cash is not None
        and financing_cash is not None
        and fx_adjustment is not None
        and reported_net_increase is not None
    ):

        calculated = (
            operating_cash
            + investing_cash
            + financing_cash
            + fx_adjustment
        )

        variance = calculated - reported_net_increase

        checks.append({
            "check":
                "Operating + Investing + Financing + "
                "FX Adjustment = Net Increase in Cash",
            "formula":
                "operating + investing + financing + fx_adjustment",
            "inputs": {
                "operating": operating_cash,
                "investing": investing_cash,
                "financing": financing_cash,
                "fx_adjustment": fx_adjustment
            },
            "calculated_value": round(
                calculated,
                2
            ),
            "reported_value": round(
                reported_net_increase,
                2
            ),
            "variance": round(
                variance,
                2
            ),
            "status":
                "PASS"
                if abs(variance) <= 0.01
                else "FAIL"
        })

    opening_cash = normalize_validation_number(
        period.get(
            "opening_cash_and_cash_equivalents"
        )
    )

    closing_cash = normalize_validation_number(
        period.get(
            "closing_cash_and_cash_equivalents"
        )
    )

    if (
        opening_cash is not None
        and reported_net_increase is not None
        and closing_cash is not None
    ):

        calculated = (
            opening_cash
            + reported_net_increase
        )

        variance = calculated - closing_cash

        checks.append({
            "check":
                "Opening Cash + Net Increase in Cash = Closing Cash",
            "formula":
                "opening_cash + net_increase_in_cash",
            "inputs": {
                "opening_cash": opening_cash,
                "net_increase_in_cash":
                    reported_net_increase
            },
            "calculated_value": round(
                calculated,
                2
            ),
            "reported_value": round(
                closing_cash,
                2
            ),
            "variance": round(
                variance,
                2
            ),
            "status":
                "PASS"
                if abs(variance) <= 0.01
                else "FAIL"
        })

    return checks


def validate_invoice(extracted_data: dict) -> list[dict]:
    """
    Run all invoice validation checks using the
    complete extracted invoice data.
    """

    items = extracted_data.get(
        "items",
        []
    )

    if not isinstance(items, list):
        items = []

    vat_rate = extracted_data.get("vat_rate")
    net_total = extracted_data.get("net_total")
    vat_total = extracted_data.get("vat_total")
    gross_total = extracted_data.get("gross_total")

    # Evidence-wrapped fields may contain:
    # {"value": ..., "page": ..., "evidence": ...}

    if isinstance(vat_rate, dict):
        vat_rate = vat_rate.get("value")

    if isinstance(net_total, dict):
        net_total = net_total.get("value")

    if isinstance(vat_total, dict):
        vat_total = vat_total.get("value")

    if isinstance(gross_total, dict):
        gross_total = gross_total.get("value")

    checks = []

    checks.extend(
        validate_invoice_items(items)
    )

    checks.append(
        validate_invoice_net_total(
            items,
            net_total
        )
    )

    checks.append(
        validate_invoice_vat(
            net_total,
            vat_rate,
            vat_total
        )
    )

    checks.append(
        validate_invoice_gross_total(
            net_total,
            vat_total,
            gross_total
        )
    )

    return checks


def validate_balance_sheet_document(
    extracted_data: dict
) -> list[dict]:
    """
    Run Balance Sheet validation using the extracted
    Balance Sheet data.

    The extraction service may return Balance Sheet data
    in either:

    1. A period-based structure:
       extracted_data["periods"][0]

    2. A top-level structure:
       extracted_data["capital_and_liabilities"]
       extracted_data["assets"]

    This validator supports both structures.
    """

    periods = extracted_data.get("periods")

    # Gemini may sometimes return the periods field
    # as a JSON string instead of a Python list.
    if isinstance(periods, str):
        try:
            periods = json.loads(periods)
        except json.JSONDecodeError:
            periods = None

    # Make sure periods is actually a list.
    if periods is not None and not isinstance(periods, list):
        periods = None

    # ---------------------------------------------------------
    # Case 1: Period-based extraction
    # ---------------------------------------------------------

    if periods:

        checks = []

        for index, period in enumerate(
            periods,
            start=1
        ):

            # Prevent "'str' object has no attribute get"
            # if Gemini returns an invalid period.
            if not isinstance(period, dict):
                checks.append({
                    "period_index": index,
                    "check": "Capital and Liabilities = Assets",
                    "formula":
                        "capital_and_liabilities_total = assets_total",
                    "inputs": {
                        "capital_and_liabilities_total": None,
                        "assets_total": None
                    },
                    "calculated_value": None,
                    "reported_value": None,
                    "variance": None,
                    "status": "NOT_APPLICABLE"
                })

                continue

            capital_and_liabilities = period.get(
                "capital_and_liabilities",
                {}
            )

            assets = period.get(
                "assets",
                {}
            )

            if not isinstance(
                capital_and_liabilities,
                dict
            ):
                capital_and_liabilities = {}

            if not isinstance(
                assets,
                dict
            ):
                assets = {}

            capital_and_liabilities_total = (
                capital_and_liabilities.get("total")
            )

            assets_total = assets.get("total")

            # Evidence-wrapped values
            if isinstance(
                capital_and_liabilities_total,
                dict
            ):
                capital_and_liabilities_total = (
                    capital_and_liabilities_total.get(
                        "value"
                    )
                )

            if isinstance(
                assets_total,
                dict
            ):
                assets_total = assets_total.get(
                    "value"
                )

            # Normalize
            capital_and_liabilities_total = (
                normalize_validation_number(
                    capital_and_liabilities_total
                )
            )

            assets_total = normalize_validation_number(
                assets_total
            )

            if (
                capital_and_liabilities_total is None
                or assets_total is None
            ):

                checks.append({
                    "period_index": index,
                    "check":
                        "Capital and Liabilities = Assets",
                    "formula":
                        "capital_and_liabilities_total "
                        "= assets_total",
                    "inputs": {
                        "capital_and_liabilities_total":
                            capital_and_liabilities_total,
                        "assets_total":
                            assets_total
                    },
                    "calculated_value": None,
                    "reported_value": assets_total,
                    "variance": None,
                    "status": "NOT_APPLICABLE"
                })

                continue

            variance = (
                capital_and_liabilities_total
                - assets_total
            )

            passed = abs(variance) <= 0.01

            checks.append({
                "period_index": index,
                "check":
                    "Capital and Liabilities = Assets",
                "formula":
                    "capital_and_liabilities_total "
                    "= assets_total",
                "inputs": {
                    "capital_and_liabilities_total":
                        capital_and_liabilities_total,
                    "assets_total":
                        assets_total
                },
                "calculated_value": round(
                    capital_and_liabilities_total,
                    2
                ),
                "reported_value": round(
                    assets_total,
                    2
                ),
                "variance": round(
                    variance,
                    2
                ),
                "status":
                    "PASS"
                    if passed
                    else "FAIL"
            })

        return checks

    # ---------------------------------------------------------
    # Case 2: Top-level extraction
    # ---------------------------------------------------------

    capital_and_liabilities = extracted_data.get(
        "capital_and_liabilities"
    )

    assets = extracted_data.get(
        "assets"
    )

    if not isinstance(
        capital_and_liabilities,
        dict
    ):
        capital_and_liabilities = None

    if not isinstance(
        assets,
        dict
    ):
        assets = None

    if not capital_and_liabilities or not assets:

        return [{
            "check":
                "Capital and Liabilities = Assets",
            "formula":
                "capital_and_liabilities_total "
                "= assets_total",
            "inputs": {
                "capital_and_liabilities_total":
                    None,
                "assets_total":
                    None
            },
            "calculated_value": None,
            "reported_value": None,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }]

    # ---------------------------------------------------------
    # Extract totals
    # ---------------------------------------------------------

    capital_and_liabilities_total = (
        capital_and_liabilities.get("total")
    )

    assets_total = assets.get("total")

    # Evidence-wrapped values
    if isinstance(
        capital_and_liabilities_total,
        dict
    ):
        capital_and_liabilities_total = (
            capital_and_liabilities_total.get(
                "value"
            )
        )

    if isinstance(
        assets_total,
        dict
    ):
        assets_total = assets_total.get(
            "value"
        )

    # ---------------------------------------------------------
    # Normalize totals
    # ---------------------------------------------------------

    capital_and_liabilities_total = (
        normalize_validation_number(
            capital_and_liabilities_total
        )
    )

    assets_total = normalize_validation_number(
        assets_total
    )

    # ---------------------------------------------------------
    # Missing totals
    # ---------------------------------------------------------

    if (
        capital_and_liabilities_total is None
        or assets_total is None
    ):

        return [{
            "check":
                "Capital and Liabilities = Assets",
            "formula":
                "capital_and_liabilities_total "
                "= assets_total",
            "inputs": {
                "capital_and_liabilities_total":
                    capital_and_liabilities_total,
                "assets_total":
                    assets_total
            },
            "calculated_value": None,
            "reported_value": assets_total,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }]

    # ---------------------------------------------------------
    # Calculate variance
    # ---------------------------------------------------------

    variance = (
        capital_and_liabilities_total
        - assets_total
    )

    passed = abs(variance) <= 0.01

    # ---------------------------------------------------------
    # Return validation result
    # ---------------------------------------------------------

    return [{
        "check":
            "Capital and Liabilities = Assets",
        "formula":
            "capital_and_liabilities_total "
            "= assets_total",
        "inputs": {
            "capital_and_liabilities_total":
                capital_and_liabilities_total,
            "assets_total":
                assets_total
        },
        "calculated_value": round(
            capital_and_liabilities_total,
            2
        ),
        "reported_value": round(
            assets_total,
            2
        ),
        "variance": round(
            variance,
            2
        ),
        "status":
            "PASS"
            if passed
            else "FAIL"
    }]


def validate_profit_and_loss_document(
    extracted_data: dict
) -> list[dict]:
    """
    Run Profit & Loss validation for each
    extracted period.
    """

    periods = extracted_data.get("periods")

    # Gemini may return periods as a JSON string.
    if isinstance(periods, str):
        try:
            periods = json.loads(periods)
        except json.JSONDecodeError:
            periods = None

    if not isinstance(periods, list):
        periods = []

    if not periods:

        return [{
            "check":
                "Profit & Loss validation",
            "formula":
                "period-based financial validation",
            "inputs": {},
            "calculated_value": None,
            "reported_value": None,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }]

    checks = []

    for period in periods:

        if not isinstance(period, dict):
            continue

        checks.extend(
            validate_profit_and_loss(period)
        )

    return checks


def validate_cash_flow_document(
    extracted_data: dict
) -> list[dict]:
    """
    Run Cash Flow validation for each
    extracted period.
    """

    periods = extracted_data.get("periods")

    # Gemini may return periods as a JSON string.
    if isinstance(periods, str):
        try:
            periods = json.loads(periods)
        except json.JSONDecodeError:
            periods = None

    if not isinstance(periods, list):
        periods = []

    if not periods:

        return [{
            "check":
                "Cash Flow validation",
            "formula":
                "period-based financial validation",
            "inputs": {},
            "calculated_value": None,
            "reported_value": None,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }]

    checks = []

    for period in periods:

        if not isinstance(period, dict):
            continue

        checks.extend(
            validate_cash_flow(period)
        )

    return checks


def validate_document(
    document_type: str,
    extracted_data: dict
) -> list[dict]:
    """
    Run the appropriate financial validation
    based on the document type.
    """

    if not isinstance(extracted_data, dict):
        return [{
            "check":
                "Financial validation",
            "formula":
                "valid extracted document structure",
            "inputs": {},
            "calculated_value": None,
            "reported_value": None,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }]

    if document_type == "invoice":
        return validate_invoice(
            extracted_data
        )

    if document_type == "balance_sheet":
        return validate_balance_sheet_document(
            extracted_data
        )

    if document_type == "profit_and_loss":
        return validate_profit_and_loss_document(
            extracted_data
        )

    if document_type == "cash_flow_statement":
        return validate_cash_flow_document(
            extracted_data
        )

    return [{
        "check":
            "Document type validation",
        "formula":
            "supported document type",
        "inputs": {
            "document_type":
                document_type
        },
        "calculated_value": None,
        "reported_value": None,
        "variance": None,
        "status": "NOT_APPLICABLE"
    }]