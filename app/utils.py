def format_currency(value, unit='ر.س'):
    """تنسيق القيم المالية بشكل أنيق"""
    if value is None:
        return f"غير متاح {unit}"
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return f"غير متاح {unit}"
    
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f} مليار {unit}"
    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.2f} مليون {unit}"
    else:
        return f"{value:,.2f} {unit}"

def validate_inputs(data):
    """التحقق من صحة المدخلات"""
    required = ['company', 'models']
    missing = [field for field in required if field not in data or not data[field]]
    return len(missing) == 0, missing