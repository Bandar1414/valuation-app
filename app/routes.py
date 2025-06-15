from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
import pandas as pd
import locale
from app.data_service import load_data
from app.services.valuation_service import evaluate_all_models
from app.plotting import generate_plot

main_blueprint = Blueprint('main', __name__)

# إعداد التنسيق المحلي للأرقام
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
    """تنسيق القيم المالية مع وحدة العملة"""
    if value is None or pd.isna(value):
        return 'غير متاح'
    try:
        num = float(value)
        if abs(num) >= 1_000_000_000:
            return f"{locale.format_string('%.2f', num / 1_000_000_000, grouping=True)} مليار {unit}"
        elif abs(num) >= 1_000_000:
            return f"{locale.format_string('%.2f', num / 1_000_000, grouping=True)} مليون {unit}"
        else:
            return f"{locale.format_string('%.2f', num, grouping=True)} {unit}"
    except:
        return 'غير متاح'

def format_number(value, is_million=False):
    """تنسيق الأرقام العادية مع إمكانية التحويل للمليون"""
    if value is None or pd.isna(value):
        return 'غير متاح'
    try:
        num = float(value)
        if is_million and num < 1000:
            num *= 1_000_000
        if num.is_integer():
            return locale.format_string("%d", num, grouping=True)
        return locale.format_string("%.2f", num, grouping=True)
    except:
        return 'غير متاح'

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
    result = None  # تغيير القيمة الافتراضية إلى None
    plot_url = None
    company_details = None

    if request.method == 'POST':
        selected_company = request.form.get('company', '').strip()
        if not selected_company:
            flash("يرجى اختيار شركة من القائمة", "warning")
            return render_template('index.html',
                               companies=companies,
                               last_update=datetime.now().strftime("%Y-%m-%d %H:%M"))

        try:
            company_row = df[df["الشركة"].str.strip().str.lower() == selected_company.lower()].iloc[0]
            
            company_data = {
                "eps": try_float(company_row.get("العائد على السهم")),
                "market_price": try_float(company_row.get("سعر الإغلاق")),
                "net_income": try_float(company_row.get("صافي الدخل (ر.س بالمليون)")),
                "shares_outstanding": try_float(company_row.get("الأسهم المصدره (بالمليون)")),
                "equity": try_float(company_row.get("حقوق المساهمين (ر.س بالمليون)")),
                "book_value": try_float(company_row.get("القيمه الدفتريه")),
            }

            # حساب القيمة السوقية
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
                "العائد على السهم": company_data['eps'],
                "القيمه الدفتريه": company_data['book_value'],
                "السعر / القيمه الدفتريه": safe_divide(company_data['market_price'], company_data['book_value'])
            }

            user_inputs = {
                "selected_models": request.form.getlist('models'),
                "gordon_growth": try_float(request.form.get('gordon_growth_rate', 0.05)),
                "gordon_discount": try_float(request.form.get('gordon_discount_rate', 0.10)),
            }
            
            result = evaluate_all_models(company_data, user_inputs)
            print(f"نتائج التقييم: {result}")  # Debug

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
        return round(float(a) / float(b), 2) if b and float(b) != 0 else None
    except (ValueError, TypeError, ZeroDivisionError):
        return None