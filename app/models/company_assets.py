def calculate_asset_valuation(assets, liabilities):
    """
    نموذج تقييم الأصول = الأصول - الالتزامات
    """
    if assets is None or liabilities is None:
        return None

    value = assets - liabilities
    return round(value, 2)
