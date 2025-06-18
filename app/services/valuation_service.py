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
    try:
        if b is None or float(b) == 0:
            return None
        return round(float(a) / float(b), 2)
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


# ======== الكود الخاص بالـ Blueprint والروات ========

from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
import pandas as pd
import locale
from app.data_service import load_data
from app.services.valuation_service import evaluate_all_models
from app.plotting import generate_plot

main_blueprint = Blueprint('main', __name__)

try:
    locale.setlocale(locale.LC_NUMERIC, 'ar_SA.UTF-8')
except:
    locale.setlocale(locale.LC_NUMERIC, '')

def try_float(value):
    try:
        if pd.isna(value) or value in [None, '']:
            return None
        return float(str(value).replace(',', '').strip())
    except (ValueError, TypeError):
        return None

def format_currency(value, unit='ر.س'):
    if value is None or pd.isna(value):
        return 'غير متاح'
    try:
        num = float(value)
        prefix = "-" if num < 0 else ""
        suffix = " (خسارة)" if num < 0 else ""
        abs_num = abs(num)
        
        if abs_num >= 1_000_000_000_000:
            formatted = f"{prefix}{locale.format_string('%.2f', abs_num / 1_000_000_000_000, grouping=True)} تريليون {unit}{suffix}"
        elif abs_num >= 1_000_000_000:
            formatted = f"{prefix}{locale.format_string('%.2f', abs_num / 1_000_000_000, grouping=True)} مليار {unit}{suffix}"
        elif abs_num >= 1_000_000:
            formatted = f"{prefix}{locale.format_string('%.2f', abs_num / 1_000_000, grouping=True)} مليون {unit}{suffix}"
        else:
            formatted = f"{prefix}{locale.format_string('%.2f', abs_num, grouping=True)} {unit}{suffix}"
        
        return formatted
    except:
        return 'غير متاح'

def format_number(value, is_million=False):
    if value is None or pd.isna(value):
        return 'غير متاح'
    try:
        num = float(value)
        prefix = "-" if num < 0 else ""
        suffix = " (خسارة)" if num < 0 else ""
        abs_num = abs(num)
        
        if is_million:
            if abs_num >= 1_000_000:
                abs_num = abs_num / 1_000_000
                unit = "تريليون"
            elif abs_num >= 1_000:
                abs_num = abs_num / 1_000
                unit = "مليار"
            else:
                unit = "مليون"
        else:
            unit = ""
            
        if abs_num.is_integer():
            formatted = f"{prefix}{locale.format_string('%d', abs_num, grouping=True)} {unit}{suffix}"
        else:
            formatted = f"{prefix}{locale.format_string('%.2f', abs_num, grouping=True)} {unit}{suffix}"
            
        return formatted.strip()
    except:
        return 'غير متاح'

def find_duplicate_eps(df):
    if "العائد على السهم" not in df.columns:
        return set()
    eps_series = df["العائد على السهم"].dropna()
    duplicates = eps_series[eps_series.duplicated(keep=False)].unique()
    return set(duplicates)

@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    df = load_data()
    if df is None:
        flash("تعذر تحميل بيانات الشركات - يرجى التحقق من ملف البيانات", "danger")
        return render_template('error.html', 
                            message="تعذر تحميل بيانات الشركات",
                            error_details="ملف البيانات غير موجود أو به مشاكل")

    required_fields = [
        "الشركة", "العائد على السهم", "سعر الإغلاق", 
        "القيمه الدفتريه", "صافي الدخل (ر.س بالمليون)",
        "الأسهم المصدره (بالمليون)", "حقوق المساهمين (ر.س بالمليون)"
    ]
    
    missing_columns = [col for col in required_fields if col not in df.columns]
    if missing_columns:
        flash(f"بيانات غير مكتملة - الأعمدة المفقودة: {missing_columns}", "danger")
        return render_template('error.html', 
                            message="بيانات غير مكتملة",
                            error_details=f"الأعمدة المفقودة: {missing_columns}")

    valid_companies = df.dropna(subset=required_fields)
    if valid_companies.empty:
        flash("لا توجد بيانات كافية في ملف البيانات", "warning")
        return render_template('error.html', 
                            message="لا توجد بيانات كافية",
                            error_details="جميع الشركات تحتوي على قيم مفقودة في الحقول المطلوبة")

    companies = sorted(valid_companies["الشركة"].unique())
    selected_company = None
    result = None
    plot_url = None
    company_details = None
    duplicate_eps_values = find_duplicate_eps(df)

    if request.method == 'POST':
        selected_company = request.form.get('company', '').strip()
        if not selected_company:
            flash("يرجى اختيار شركة من القائمة", "warning")
            return render_template('index.html',
                               companies=companies,
                               last_update=datetime.now().strftime("%Y-%m-%d %H:%M"))

        try:
            company_row = df[df["الشركة"].str.strip().str.lower() == selected_company.lower()].iloc[0]
            
            eps_val = try_float(company_row.get("العائد على السهم"))
            is_eps_duplicate = eps_val in duplicate_eps_values if eps_val is not None else False

            company_data = {
                "eps": eps_val,
                "market_price": try_float(company_row.get("سعر الإغلاق")),
                "net_income": try_float(company_row.get("صافي الدخل (ر.س بالمليون)")),
                "shares_outstanding": try_float(company_row.get("الأسهم المصدره (بالمليون)")),
                "equity": try_float(company_row.get("حقوق المساهمين (ر.س بالمليون)")),
                "book_value": try_float(company_row.get("القيمه الدفتريه")),
            }

            market_cap = None
            if company_data['market_price'] and company_data['shares_outstanding']:
                market_cap = company_data['market_price'] * company_data['shares_outstanding']

            company_details = {
                "الشركة": selected_company,
                "سعر الإغلاق": company_data['market_price'],
                "عدد الأسهم - نص": company_data['shares_outstanding'],
                "القيمة السوقية (ر.س بالمليون) - نص": market_cap,
                "صافي الدخل (ر.س بالمليون) - نص": company_data['net_income'],
                "حقوق المساهمين (ر.س بالمليون) - نص": company_data['equity'],
                "العائد على السهم": eps_val,
                "is_eps_duplicate": is_eps_duplicate,
                "القيمه الدفتريه": company_data['book_value'],
                "السعر / القيمه الدفتريه": safe_divide(company_data['market_price'], company_data['book_value'])
            }

            user_inputs = {
                "selected_models": request.form.getlist('models'),
                "gordon_growth": try_float(request.form.get('gordon_growth_rate', 0.05)),
                "gordon_discount": try_float(request.form.get('gordon_discount_rate', 0.10)),
            }
            
            result = evaluate_all_models(company_data, user_inputs)
            print(f"نتائج التقييم: {result}")

            if result and 'models' in result:
                plot_url = generate_plot(
                    {k: v['القيمة العادلة'] for k, v in result['models'].items() if v['القيمة العادلة'] is not None},
                    f"مقارنة نماذج التقييم لشركة {selected_company}"
                )

        except IndexError:
            flash(f"الشركة '{selected_company}' غير موجودة في قاعدة البيانات", "danger")
        except Exception as e:
            print(f"Error processing company data: {str(e)}")
            flash("حدث خطأ غير متوقع أثناء معالجة البيانات", "danger")

    return render_template('index.html',
                         companies=companies,
                         selected_company=selected_company,
                         result=result,
                         plot_url=plot_url,
                         company_details=company_details,
                         last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
                         format_currency=format_currency,
                         format_number=format_number)

def safe_divide(a, b):
    try:
        if b is None or float(b) == 0:
            return None
        return round(float(a) / float(b), 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None