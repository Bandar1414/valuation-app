def calculate_pe_valuation(earnings, shares_outstanding, market_price):
    """
    نموذج تقييم بسيط باستخدام مضاعف السعر إلى الربحية (P/E)
    """
    if not earnings or not shares_outstanding:
        return None

    try:
        eps = earnings / shares_outstanding
        pe_ratio = market_price / eps if eps else None
        fair_value = eps * pe_ratio if pe_ratio else None
        return round(fair_value, 2) if fair_value else None
    except:
        return None
