def calculate_ddm(eps, growth_rate=0.05, discount_rate=0.10, payout_ratio=0.6):
    """
    نموذج توزيعات الأرباح (DDM)
    - D = EPS * نسبة التوزيع
    """
    if eps is None or discount_rate is None:
        return None

    dividend = eps * payout_ratio
    try:
        value = dividend * (1 + growth_rate) / (discount_rate - growth_rate)
        return round(value, 2)
    except ZeroDivisionError:
        return None
