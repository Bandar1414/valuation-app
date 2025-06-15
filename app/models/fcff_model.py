def calculate_fcff(fcff, wacc=0.10, growth_rate=0.05, terminal_growth=0.02, years=5):
    """
    نموذج FCFF: التدفقات النقدية الحرة للشركة
    """
    if fcff is None or wacc is None:
        return None

    projected_fcff = []
    current_fcff = fcff

    for _ in range(years):
        current_fcff *= (1 + growth_rate)
        projected_fcff.append(current_fcff)

    discounted_fcff = [
        f / ((1 + wacc) ** (i + 1)) for i, f in enumerate(projected_fcff)
    ]

    terminal_value = projected_fcff[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    terminal_value_discounted = terminal_value / ((1 + wacc) ** years)

    total_value = sum(discounted_fcff) + terminal_value_discounted
    return round(total_value, 2)
