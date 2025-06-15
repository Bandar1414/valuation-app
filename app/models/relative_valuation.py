def calculate_relative_valuation(company_data, user_inputs):
    """
    تقييم نسبي باستخدام مضاعفات مثل P/E أو P/B.
    """
    try:
        eps = company_data.get("net_income") / company_data.get("shares_outstanding")
        book_value_per_share = company_data.get("equity") / company_data.get("shares_outstanding")
        market_price = company_data.get("market_price")

        if not eps or not book_value_per_share or not market_price:
            return None

        pe_ratio = market_price / eps if eps else None
        pb_ratio = market_price / book_value_per_share if book_value_per_share else None

        return {
            "P/E": round(pe_ratio, 2) if pe_ratio else None,
            "P/B": round(pb_ratio, 2) if pb_ratio else None,
        }
    except Exception:
        return None
