from flask import Flask, render_template, request
import pandas as pd
import os
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "stocks_data.xlsx")

# تحميل البيانات
def load_data():
    try:
        df = pd.read_excel(EXCEL_PATH, header=2)
        df = df.dropna(subset=["الشركة"])
        return df
    except Exception as e:
        print(f"خطأ في تحميل البيانات: {e}")
        return None

# رسم بياني مع دعم الخط العربي
def generate_plot(values_dict, title):
    plt.figure(figsize=(10, 5))
    bars = plt.bar(values_dict.keys(), values_dict.values(), color='skyblue')
    plt.title(title, fontsize=16, fontname='Cairo')
    plt.xticks(rotation=25, fontname='Cairo')
    plt.yticks(fontname='Cairo')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # إضافة قيم على الأعمدة
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height, 
                f'{height:.2f}', 
                ha='center', va='bottom', 
                fontname='Cairo')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    return plot_data

# نموذج جوردون للنمو
def gordon_model(eps, growth, discount):
    if growth >= discount:
        return None
    return round(eps * (1 + growth) / (discount - growth), 2)

# نموذج مضاعف الربحية
def pe_target_model(eps, pe_target):
    return round(eps * pe_target, 2)

# نموذج التدفقات النقدية المخصومة (DCF)
def dcf_model(fcf_list, discount_rate, growth_rate, terminal_year):
    """
    fcf_list: قائمة التدفقات النقدية الحرة للسنوات المستقبلية (قائمة أعداد)
    discount_rate: معدل الخصم (مثلاً 10%)
    growth_rate: معدل النمو المستدام بعد فترة التقييم
    terminal_year: سنة بداية القيمة المتبقية (بعد آخر سنة من fcf_list)
    """
    npv = 0
    for t, fcf in enumerate(fcf_list, start=1):
        npv += fcf / ((1 + discount_rate) ** t)

    # حساب القيمة المتبقية (Terminal Value) باستخدام نموذج جوردون على التدفق النقدي للسنة الأخيرة
    terminal_value = fcf_list[-1] * (1 + growth_rate) / (discount_rate - growth_rate)
    terminal_value_discounted = terminal_value / ((1 + discount_rate) ** terminal_year)

    total_value = npv + terminal_value_discounted
    return round(total_value, 2)

# نموذج Greenfield (تقديري بناءً على الأصول)
def greenfield_model(book_value, growth, years=5):
    return round(book_value * ((1 + growth) ** years), 2)

# نموذج التدفقات النقدية (Cash Flow Model)
def cash_flow_model(fcf, shares_outstanding, discount_rate, growth_rate, years=5):
    """
    حساب القيمة العادلة بناءً على التدفقات النقدية الحرة
    """
    try:
        # تقدير التدفقات النقدية لسنوات مع معدل النمو
        fcf_list = [fcf * ((1 + growth_rate) ** i) for i in range(1, years+1)]
        
        # حساب القيمة باستخدام نموذج DCF
        fair_value = dcf_model(fcf_list, discount_rate, growth_rate, years)
        
        # حساب القيمة لكل سهم
        if shares_outstanding > 0:
            return round(fair_value / shares_outstanding, 2)
        return None
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    df = load_data()
    if df is None:
        return render_template('error.html', message="تعذر تحميل بيانات الشركات")

    # قائمة الشركات مع إزالة التكرار
    companies = sorted(df["الشركة"].dropna().unique().tolist())

    selected_company = request.form.get('company') if request.method == 'POST' else None
    
    # قيم افتراضية للمدخلات
    default_values = {
        'gordon_growth': 0.05,
        'gordon_discount': 0.10,
        'pe_target': 18,
        'cf_growth': 0.05,
        'cf_discount': 0.10,
        'free_cash_flow': None
    }
    
    # الحصول على القيم من النموذج إذا كانت موجودة
    input_values = {
        'gordon_growth': float(request.form.get('gordon_growth', default_values['gordon_growth'])),
        'gordon_discount': float(request.form.get('gordon_discount', default_values['gordon_discount'])),
        'pe_target': float(request.form.get('pe_target', default_values['pe_target'])),
        'cf_growth': float(request.form.get('cf_growth', default_values['cf_growth'])),
        'cf_discount': float(request.form.get('cf_discount', default_values['cf_discount'])),
        'free_cash_flow': request.form.get('free_cash_flow')
    }
    
    result = {}
    plot_url = None
    company_details = None
    valuation_inputs = default_values.copy()
    valuation_inputs.update(input_values)

    if selected_company:
        company_data = df[df["الشركة"] == selected_company].iloc[0]
        
        # تفاصيل الشركة الأساسية
        company_details = {
            "الشركة": selected_company,
            "سعر الإغلاق": company_data.get("سعر الإغلاق"),
            "الأسهم المصدره (بالمليون)": company_data.get("الأسهم المصدره (بالمليون)"),
            "صافي الدخل (ر.س بالمليون)": company_data.get("صافي الدخل (ر.س بالمليون)"),
            "حقوق المساهمين (ر.س بالمليون)": company_data.get("حقوق المساهمين (ر.س بالمليون)"),
            "القيمة السوقية (ر.س بالمليون)": company_data.get("القيمة السوقية (ر.س بالمليون)"),
            "العائد على السهم": company_data.get("العائد على السهم"),
            "القيمه الدفتريه": company_data.get("القيمه الدفتريه"),
            "السعر / القيمه الدفتريه": company_data.get("السعر / القيمه الدفتريه"),
            "EBIT": company_data.get("EBIT")
        }

        # سحب القيم الأساسية
        eps = company_data.get("العائد على السهم")
        price = company_data.get("سعر الإغلاق")
        book = company_data.get("القيمه الدفتريه")
        net_income = company_data.get("صافي الدخل (ر.س بالمليون)")
        shares_outstanding = company_data.get("الأسهم المصدره (بالمليون)")
        
        try:
            eps = float(eps) if pd.notna(eps) else None
            price = float(price) if pd.notna(price) else None
            book = float(book) if pd.notna(book) else None
            net_income = float(net_income) if pd.notna(net_income) else None
            shares_outstanding = float(shares_outstanding) if pd.notna(shares_outstanding) else None

            # حساب التدفق النقدي الحر إذا لم يتم تقديمه
            if input_values['free_cash_flow']:
                free_cash_flow = float(input_values['free_cash_flow'])
            else:
                # تقدير افتراضي إذا لم يتم تقديم التدفق النقدي الحر
                free_cash_flow = net_income * 0.8 if net_income else None
            
            # حساب نماذج التقييم
            fair_gordon = gordon_model(eps, 
                                     valuation_inputs['gordon_growth'], 
                                     valuation_inputs['gordon_discount']) if eps else None
                                     
            fair_pe = pe_target_model(eps, valuation_inputs['pe_target']) if eps else None
            
            fair_cf = cash_flow_model(free_cash_flow, 
                                    shares_outstanding, 
                                    valuation_inputs['cf_discount'], 
                                    valuation_inputs['cf_growth']) if free_cash_flow and shares_outstanding else None
                                    
            fair_greenfield = greenfield_model(book, 
                                             valuation_inputs['gordon_growth']) if book else None

            # تحديد النموذج المستخدم (DCF أو Greenfield)
            model_used = "التدفقات النقدية" if fair_cf else ("Greenfield" if fair_greenfield else "لا توجد بيانات")

            # حساب الفروقات بالنسبة للسعر الحالي
            def diff_pct(fv): 
                return round((fv - price) / price * 100, 2) if fv and price else None
            
            def pe_implied(fv): 
                return round(price / fv, 2) if fv and price else None

            result = {
                "السعر الحالي": price,
                "ربحية السهم (EPS)": eps,
                "القيمة العادلة - جوردون": fair_gordon,
                "القيمة العادلة - مضاعف الربحية": fair_pe,
                f"القيمة العادلة - {model_used}": fair_cf or fair_greenfield,
                "الفرق - جوردون (%)": diff_pct(fair_gordon),
                "الفرق - مضاعف الربحية (%)": diff_pct(fair_pe),
                f"الفرق - {model_used} (%)": diff_pct(fair_cf or fair_greenfield),
                "مكرر مستنتج - جوردون": pe_implied(fair_gordon),
                "مكرر مستنتج - مضاعف الربحية": pe_implied(fair_pe),
                f"مكرر مستنتج - {model_used}": pe_implied(fair_cf or fair_greenfield),
            }

            # تحضير بيانات الرسم البياني مع تسميات عربية
            values = {
                "السعر الحالي": price or 0,
                "جوردون": fair_gordon or 0,
                "مضاعف الربحية": fair_pe or 0,
                model_used: (fair_cf or fair_greenfield) or 0
            }
            plot_url = generate_plot(values, f"مقارنة نماذج التقييم لشركة {selected_company}")

        except Exception as e:
            print(f"Error in calculations: {str(e)}")
            return render_template('error.html', message=f"خطأ في حساب النماذج: {e}")

    return render_template('index.html', 
                         companies=companies, 
                         selected_company=selected_company, 
                         result=result, 
                         plot_url=plot_url,
                         company_details=company_details,
                         inputs=valuation_inputs,
                         last_update=datetime.now().strftime("%Y-%m-%d %H:%M"))

if __name__ == "__main__":
    app.run(debug=True)