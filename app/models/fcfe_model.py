def calculate_fcfe(fcfe, cost_of_equity=0.10, growth_rate=0.05, years=5):
    """
    نموذج FCFE: التدفقات النقدية الحرة للمساهمين
    """
    if fcfe is None or cost_of_equity is None:
        return None

    projected_fcfe = []
    current_fcfe = fcfe

    for _ in range(years):
        current_fcfe *= (1 + growth_rate)
        projected_fcfe.append(current_fcfe)

    discounted_fcfe = [
        f / ((1 + cost_of_equity) ** (i + 1)) for i, f in enumerate(projected_fcfe)
    ]

    total_value = sum(discounted_fcfe)
    return round(total_value, 2)
