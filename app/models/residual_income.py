def calculate_residual_income(net_income, equity, growth_rate=0.05, discount_rate=0.10, years=5):
    """
    نموذج الدخل المتبقي (Residual Income)
    """
    if net_income is None or equity is None or discount_rate is None:
        return None

    ri_values = []
    current_ri = net_income - (equity * discount_rate)

    for year in range(1, years + 1):
        ri_values.append(current_ri / ((1 + discount_rate) ** year))
        current_ri *= (1 + growth_rate)

    total_value = equity + sum(ri_values)
    return round(total_value, 2)
