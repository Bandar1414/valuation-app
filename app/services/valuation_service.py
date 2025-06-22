from app.models import (
    gordon_model,
    dcf_model,
    residual_income,
    relative_valuation
)
import pandas as pd

def try_float(value):
    try:
        if pd.isna(value) or value in [None, '']:
            return None
        return float(str(value).replace(',', '').strip())
    except (ValueError, TypeError):
        return None

def safe_divide(a, b):
    try:
        if b is None or float(b) == 0:
            return None
        return round(float(a) / float(b), 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def safe_diff_pct(fair_value, market_price):
    try:
        fair_value = float(fair_value)
        market_price = float(market_price)
        return round(((fair_value - market_price) / market_price) * 100, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def evaluate_all_models(company_data, user_inputs):
    results = {}
    market_price = company_data.get('market_price')
    selected_models = user_inputs.get('selected_models', [])

    try:
        if 'gordon' in selected_models:
            value = gordon_model.calculate(
                eps=company_data['eps'],
                growth_rate=user_inputs.get('gordon_growth', 5.0),       # نسبة مئوية صحيحة
                discount_rate=user_inputs.get('gordon_discount', 10.0),  # نسبة مئوية صحيحة
                dividends=company_data.get('dividends')                  # ← إضافة هذه السطر لتمرير التوزيعات إذا توفرت
            )
            results['جوردون'] = {
                'القيمة العادلة': value,
                'الفرق (%)': safe_diff_pct(value, market_price),
                'مكرر مستنتج': safe_divide(market_price, value)
            }
    except Exception as e:
        results['جوردون'] = {'القيمة العادلة': None, 'خطأ': str(e)}

    try:
        if 'dcf' in selected_models:
            value = dcf_model.evaluate_dcf_model(
                net_income=company_data['net_income'],
                shares_outstanding=company_data['shares_outstanding'],
                growth_rate=user_inputs.get('dcf_growth', 5.0),         # نسبة مئوية صحيحة
                discount_rate=user_inputs.get('dcf_discount', 10.0),     # نسبة مئوية صحيحة
                years=int(user_inputs.get('dcf_terminal_year', 5)),
                manual_fcf=try_float(user_inputs.get('dcf_fcf'))
            )
            results['DCF'] = {
                'القيمة العادلة': value,
                'الفرق (%)': safe_diff_pct(value, market_price),
                'مكرر مستنتج': safe_divide(market_price, value)
            }
    except Exception as e:
        results['DCF'] = {'القيمة العادلة': None, 'خطأ': str(e)}

    try:
        if 'residual' in selected_models:
            cost_of_equity = try_float(user_inputs.get('ri_cost_of_equity'))
            discount_rate_to_use = cost_of_equity if cost_of_equity is not None else try_float(user_inputs.get('ri_discount', 10.0))

            value = residual_income.evaluate_residual_income_model(
                net_income=company_data['net_income'],
                shares_outstanding=company_data['shares_outstanding'],
                equity=company_data['equity'],
                growth_rate=user_inputs.get('ri_growth', 5.0),         # نسبة مئوية صحيحة
                discount_rate=discount_rate_to_use,                    # نسبة مئوية صحيحة
                cost_of_equity=cost_of_equity                          # نسبة مئوية صحيحة أو None
            )
            results['الدخل المتبقي'] = {
                'القيمة العادلة': value,
                'الفرق (%)': safe_diff_pct(value, market_price),
                'مكرر مستنتج': safe_divide(market_price, value)
            }
    except Exception as e:
        results['الدخل المتبقي'] = {'القيمة العادلة': None, 'خطأ': str(e)}

    try:
        if 'relative' in selected_models:
            pe_ratio = try_float(user_inputs.get('relative_pe_ratio')) or 15
            value = relative_valuation.calculate(
                pe_ratio=pe_ratio,
                net_income=company_data['net_income'],
                shares_outstanding=company_data['shares_outstanding']
            )
            results['التقييم النسبي'] = {
                'القيمة العادلة': value,
                'الفرق (%)': safe_diff_pct(value, market_price),
                'مكرر مستنتج': safe_divide(market_price, value),
                'مكرر المستخدم': pe_ratio
            }
    except Exception as e:
        results['التقييم النسبي'] = {'القيمة العادلة': None, 'خطأ': str(e)}

    return {
        'models': results,
        'metadata': {
            'company_data': company_data,
            'user_inputs': {k: v for k, v in user_inputs.items() if not isinstance(v, (list, dict))}
        }
    }

# يمكن استخدام هذا الاسم أيضاً في المشروع
calculate_valuations = evaluate_all_models
