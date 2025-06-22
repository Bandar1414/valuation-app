def calculate(pe_ratio, net_income, shares_outstanding):
    """
    تقييم نسبي باستخدام مكرر الربحية (P/E).
    """
    try:
        if not pe_ratio or not net_income or not shares_outstanding:
            return None

        eps = net_income / shares_outstanding
        fair_value = eps * pe_ratio

        return round(fair_value, 2)
    except Exception:
        return None
