import base64
import json
from flask import Blueprint, render_template, request, flash, send_file, current_app, redirect, url_for
from datetime import datetime
import pandas as pd
import locale
from app.data_service import load_data
from app.services.valuation_service import evaluate_all_models
from app.plotting import generate_plot
from weasyprint import HTML
import os
import tempfile
from app.visitor_tracker import count_unique_visitor
from app.visitor_tracker import get_visitor_count
print("📈 عدد الزوار:", get_visitor_count())


main_blueprint = Blueprint('main', __name__)

@main_blueprint.before_request
def track_visitors():
    count_unique_visitor()

@main_blueprint.route('/download_pdf', methods=['POST'])
def download_pdf():
    try:
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'logo.png')
        logo_base64 = None

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        selected_company = request.form.get('company', '')
        company_details = json.loads(request.form.get('company_details', '{}'))
        initial_inputs = json.loads(request.form.get('initial_inputs', '{}'))
        result = json.loads(request.form.get('result', '{}'))
        last_update = datetime.now().strftime('%Y-%m-%d %H:%M')

        rendered = render_template(
            'valuation_pdf_report.html',
            selected_company=selected_company,
            company_details=company_details,
            last_update=last_update,
            initial_inputs=initial_inputs,
            result=result,
            format_currency=format_currency,
            format_number=format_number,
            logo_base64=logo_base64
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            pdf_path = tmp_pdf.name

        HTML(string=rendered, base_url=request.root_url).write_pdf(pdf_path)

        response = send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'تقرير_تقييم_{selected_company}.pdf',
            mimetype='application/pdf'
        )

        @response.call_on_close
        def remove_file():
            try:
                os.remove(pdf_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting temp file: {e}")

        return response

    except Exception as e:
        current_app.logger.error(f"PDF Generation Error: {str(e)}")
        flash("حدث خطأ أثناء إنشاء ملف PDF", "danger")
        return redirect(request.referrer or url_for('main.index'))

# إعداد اللغة
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
        if abs(num) >= 1_000_000_000_000:
            return f"{locale.format_string('%.2f', num / 1_000_000_000_000, grouping=True)} ترليون {unit}"
        elif abs(num) >= 1_000_000_000:
            return f"{locale.format_string('%.2f', num / 1_000_000_000, grouping=True)} مليار {unit}"
        elif abs(num) >= 1_000_000:
            return f"{locale.format_string('%.2f', num / 1_000_000, grouping=True)} مليون {unit}"
        else:
            return f"{locale.format_string('%.2f', num, grouping=True)} {unit}"
    except:
        return 'غير متاح'

def format_number(value, is_million=False):
    if value is None or pd.isna(value):
        return 'غير متاح'
    try:
        num = float(value)
        if is_million and num < 1000:
            num *= 1_000_000

        if abs(num) >= 1_000_000_000_000:
            return f"{locale.format_string('%.2f', num / 1_000_000_000_000, grouping=True)} ترليون"
        elif abs(num) >= 1_000_000_000:
            return f"{locale.format_string('%.2f', num / 1_000_000_000, grouping=True)} مليار"
        elif abs(num) >= 1_000_000:
            return f"{locale.format_string('%.2f', num / 1_000_000, grouping=True)} مليون"
        elif num.is_integer():
            return locale.format_string("%d", num, grouping=True)
        return locale.format_string("%.2f", num, grouping=True)
    except:
        return 'غير متاح'

def safe_divide(a, b):
    try:
        return round(float(a) / float(b), 2) if b and float(b) != 0 else None
    except (ValueError, TypeError, ZeroDivisionError):
        return None

@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    df = load_data()
    if df is None:
        flash("تعذر تحميل بيانات الشركات - يرجى التحقق من ملف البيانات", "danger")
        return render_template('error.html', message="تعذر تحميل بيانات الشركات", error_details="ملف البيانات غير موجود أو به مشاكل")

    required_fields = ["الشركة", "العائد على السهم", "سعر الإغلاق", "القيمه الدفتريه", "صافي الدخل (ر.س بالمليون)", "الأسهم المصدره (بالمليون)", "حقوق المساهمين (ر.س بالمليون)"]
    missing_columns = [col for col in required_fields if col not in df.columns]
    if missing_columns:
        flash(f"بيانات غير مكتملة - الأعمدة المفقودة: {missing_columns}", "danger")
        return render_template('error.html', message="بيانات غير مكتملة", error_details=f"الأعمدة المفقودة: {missing_columns}")

    valid_companies = df.dropna(subset=required_fields)
    if valid_companies.empty:
        flash("لا توجد بيانات كافية في ملف البيانات", "warning")
        return render_template('error.html', message="لا توجد بيانات كافية", error_details="جميع الشركات تحتوي على قيم مفقودة في الحقول المطلوبة")

    companies = sorted(valid_companies["الشركة"].unique())
    selected_company = None
    result = None
    plot_url = None
    company_details = None

    if request.method == 'POST':
        selected_company = request.form.get('company', '').strip()
        if not selected_company:
            flash("يرجى اختيار شركة من القائمة", "warning")
            return render_template('index.html', companies=companies, last_update=datetime.now().strftime("%Y-%m-%d %H:%M"))

        try:
            company_row = df[df["الشركة"].str.strip().str.lower() == selected_company.lower()].iloc[0]
            
            manual_inputs = {
                'net_income': try_float(request.form.get('manual_net_income')),
                'shares_outstanding': try_float(request.form.get('manual_shares_outstanding')),
                'equity': try_float(request.form.get('manual_equity')),
                'eps': try_float(request.form.get('manual_eps')),
                'book_value': try_float(request.form.get('manual_book_value'))
            }

            manual_dividends = try_float(request.form.get('manual_dividends'))

            company_data = {
                "eps": manual_inputs['eps'] if manual_inputs['eps'] is not None else try_float(company_row.get("العائد على السهم")),
                "market_price": try_float(company_row.get("سعر الإغلاق")),
                "net_income": manual_inputs['net_income'] if manual_inputs['net_income'] is not None else try_float(company_row.get("صافي الدخل (ر.س بالمليون)")),
                "shares_outstanding": manual_inputs['shares_outstanding'] if manual_inputs['shares_outstanding'] is not None else try_float(company_row.get("الأسهم المصدره (بالمليون)")),
                "equity": manual_inputs['equity'] if manual_inputs['equity'] is not None else try_float(company_row.get("حقوق المساهمين (ر.س بالمليون)")),
                "book_value": manual_inputs['book_value'] if manual_inputs['book_value'] is not None else try_float(company_row.get("القيمه الدفتريه")),
                "dividends": manual_dividends
            }

            valuation_data = company_data.copy()

            user_inputs = {
                "selected_models": request.form.getlist('models'),
                "dcf_growth": try_float(request.form.get('dcf_growth_rate')) or 5,
                "dcf_discount": try_float(request.form.get('dcf_discount_rate')) or 10,
                "gordon_growth": try_float(request.form.get('gordon_growth_rate')) or 5,
                "gordon_discount": try_float(request.form.get('gordon_discount_rate')) or 10,
                "ri_growth": try_float(request.form.get('ri_growth')) or 5,
                "ri_discount": try_float(request.form.get('ri_discount')) or 10,
                "ri_cost_of_equity": try_float(request.form.get('ri_cost_of_equity')),
                "relative_pe_ratio": try_float(request.form.get('relative_pe_ratio')) or 15,
            }

            result = evaluate_all_models(valuation_data, user_inputs)

            if result and 'models' in result:
                plot_url = generate_plot(
                    {k: v['القيمة العادلة'] for k, v in result['models'].items() if v['القيمة العادلة'] is not None},
                    f"مقارنة نماذج التقييم لشركة {selected_company}"
                )

            market_cap = company_data['market_price'] * company_data['shares_outstanding'] if company_data['market_price'] and company_data['shares_outstanding'] else None

            company_details = {
                "الشركة": selected_company,
                "سعر الإغلاق": company_data['market_price'],
                "عدد الأسهم - نص": company_data['shares_outstanding'] * 1_000_000 if company_data['shares_outstanding'] else None,
                "القيمة السوقية (ر.س بالمليون) - نص": market_cap * 1_000_000 if market_cap else None,
                "صافي الدخل (ر.س بالمليون) - نص": company_data['net_income'] * 1_000_000 if company_data['net_income'] else None,
                "حقوق المساهمين (ر.س بالمليون) - نص": company_data['equity'] * 1_000_000 if company_data['equity'] else None,
                "العائد على السهم": company_data['eps'],
                "القيمه الدفتريه": company_data['book_value'],
                "السعر / القيمه الدفتريه": safe_divide(company_data['market_price'], company_data['book_value'])
            }

        except IndexError:
            flash(f"الشركة '{selected_company}' غير موجودة في قاعدة البيانات", "danger")
        except Exception as e:
            print(f"Error processing company data: {str(e)}")
            flash("حدث خطأ غير متوقع أثناء معالجة البيانات", "danger")

    return render_template(
        'index.html',
        companies=companies,
        selected_company=selected_company,
        result=result,
        plot_url=plot_url,
        company_details=company_details,
        last_update=datetime.now().strftime("%Y-%m-%d %H:%M"),
        format_currency=format_currency,
        format_number=format_number,
        initial_inputs=request.form if request.method == 'POST' else {}
    )
