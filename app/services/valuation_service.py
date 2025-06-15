from app.models import (
    gordon_model,
    dcf_model,
    ddm_model,
    fcff_model,
    fcfe_model,
    residual_income,
    company_assets,
    relative_valuation
)

def safe_divide(a, b):
    """قسمة آمنة مع التعامل مع الأخطاء"""
    try:
        return round(float(a) / float(b), 2) if b and float(b) != 0 else None
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def safe_diff_pct(fair_value, market_price):
    """حساب الفرق النسبي بأمان"""
    try:
        fair_value = float(fair_value)
        market_price = float(market_price)
        return round(((fair_value - market_price) / market_price) * 100, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def validate_model_inputs(data, required_fields):
    """التحقق من صحة بيانات الإدخال للنموذج"""
    return all(data.get(field) is not None for field in required_fields)

def evaluate_all_models(company_data, user_inputs):
    results = {}
    market_price = company_data.get('market_price')
    selected_models = user_inputs.get('selected_models', [])

    # نموذج جوردون
    if 'gordon' in selected_models:
        try:
            required = ['eps', 'market_price']
            if validate_model_inputs(company_data, required):
                value = gordon_model.calculate(
                    eps=company_data['eps'],
                    growth_rate=user_inputs.get('gordon_growth', 0.05),
                    discount_rate=user_inputs.get('gordon_discount', 0.10)
                )
                results['جوردون'] = {
                    'القيمة العادلة': value,
                    'الفرق (%)': safe_diff_pct(value, market_price),
                    'مكرر مستنتج': safe_divide(market_price, value)
                }
            else:
                results['جوردون'] = {
                    'القيمة العادلة': None,
                    'الفرق (%)': None,
                    'مكرر مستنتج': None,
                    'ملاحظة': 'بيانات ناقصة'
                }
        except Exception as e:
            print(f"Error in Gordon model: {str(e)}")
            results['جوردون'] = {
                'القيمة العادلة': None,
                'الفرق (%)': None,
                'مكرر مستنتج': None,
                'خطأ': str(e)
            }

    # نموذج DCF
    if 'dcf' in selected_models:
        try:
            required = ['market_price', 'net_income', 'shares_outstanding']
            if validate_model_inputs(company_data, required):
                value = dcf_model.calculate(
                    net_income=company_data['net_income'],
                    shares_outstanding=company_data['shares_outstanding'],
                    discount_rate=user_inputs.get('dcf_discount', 0.10),
                    growth_rate=user_inputs.get('dcf_growth', 0.05),
                    years=user_inputs.get('dcf_terminal_year', 5)
                )
                results['DCF'] = {
                    'القيمة العادلة': value,
                    'الفرق (%)': safe_diff_pct(value, market_price),
                    'مكرر مستنتج': safe_divide(market_price, value)
                }
            else:
                results['DCF'] = {
                    'القيمة العادلة': None,
                    'الفرق (%)': None,
                    'مكرر مستنتج': None,
                    'ملاحظة': 'بيانات ناقصة'
                }
        except Exception as e:
            print(f"Error in DCF model: {str(e)}")
            results['DCF'] = {
                'القيمة العادلة': None,
                'الفرق (%)': None,
                'مكرر مستنتج': None,
                'خطأ': str(e)
            }

    # ... باقي النماذج بنفس النمط ...

    return {
        'models': results,
        'metadata': {
            'company_data': company_data,
            'user_inputs': {k: v for k, v in user_inputs.items() if not isinstance(v, (list, dict))}
        }
    }

# للحفاظ على التوافق مع الأكواد القديمة
calculate_valuations = evaluate_all_models