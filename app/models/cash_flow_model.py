def calculate_cash_flow_value(cash_flows, discount_rate=0.10, growth_rate=0.05, years=5):
    """
    تقييم التدفقات النقدية المباشرة (بافتراض نمو ثابت)
    """
    if not cash_flows or discount_rate is None:
        return None

    last_cash_flow = cash_flows[-1]

    projected_flows = [last_cash_flow * (1 + growth_rate) ** i for i in range(1, years + 1)]
    discounted = [cf / (1 + discount_rate) ** i for i, cf in enumerate(projected_flows, start=1)]

    return round(sum(discounted), 2)
