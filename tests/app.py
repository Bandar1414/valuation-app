from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import math
from decimal import Decimal, getcontext

app = Flask(__name__)

# المسار إلى ملف الإكسل (تأكد أنه صحيح)
EXCEL_PATH = r"C:\Users\USER\Videos\New folder\tests\stocks_data.xlsx"

# ضبط دقة الحسابات العشرية
getcontext().prec = 10

def evaluate_dcf_model(net_income, shares_outstanding, growth_rate=5.0, discount_rate=10.0, years=5,
                      manual_fcf=None, debt=0, cash=0, market_price=None, equity=None, 
                      operating_cash_flow=None, capital_expenditures=None):
    try:
        logs = []
        logs.append("✨ بدء التقييم الدقيق لنموذج DCF (الإصدار المحسن)")
        
        # تحويل القيم إلى Decimal للحسابات الدقيقة
        def to_decimal(value):
            try:
                return Decimal(str(float(value))) if value not in [None, ''] else Decimal(0)
            except:
                return Decimal(0)
        
        # تحويل النسب
        growth_rate = to_decimal(growth_rate) / Decimal(100)
        discount_rate = to_decimal(discount_rate) / Decimal(100)
        years = int(years)
        
        # تحويل من مليون إلى رقم فعلي
        conversion = Decimal('1_000_000')
        net_income = to_decimal(net_income) * conversion
        shares_outstanding = to_decimal(shares_outstanding) * conversion
        equity = to_decimal(equity) * conversion if equity else Decimal(0)
        debt = to_decimal(debt) * conversion if debt else Decimal(0)
        cash = to_decimal(cash) * conversion if cash else Decimal(0)
        operating_cash_flow = to_decimal(operating_cash_flow) * conversion if operating_cash_flow else None
        capital_expenditures = to_decimal(capital_expenditures) * conversion if capital_expenditures else None
        
        logs.append(f"📊 القيم المدخلة (بالريال):")
        logs.append(f"- صافي الدخل: {net_income:,.2f}")
        logs.append(f"- الأسهم القائمة: {shares_outstanding:,.2f}")
        logs.append(f"- حقوق المساهمين: {equity:,.2f}")
        logs.append(f"- الدين: {debt:,.2f}")
        logs.append(f"- النقدية: {cash:,.2f}")
        
        # حساب Free Cash Flow بطريقة أكثر دقة
        if manual_fcf is not None:
            base_fcf = to_decimal(manual_fcf) * conversion
            logs.append(f"✅ FCF مدخل يدويًا: {base_fcf:,.2f}")
        elif operating_cash_flow is not None and capital_expenditures is not None:
            base_fcf = operating_cash_flow - capital_expenditures
            logs.append(f"💰 FCF محسوب (التدفق النقدي التشغيلي - مصروفات الاستثمار): {base_fcf:,.2f}")
        elif net_income > 0:
            base_fcf = net_income * Decimal('1.0')  # افتراض أن 85% من صافي الدخل يصبح FCF
            logs.append(f"💡 احتساب FCF = 100% من صافي الدخل = {base_fcf:,.2f}")
        else:
            base_fcf = equity * Decimal('0.1')  # 10% من حقوق المساهمين
            logs.append(f"⚠️ صافي الدخل ≤ 0، استخدام 10% من حقوق المساهمين كـ FCF: {base_fcf:,.2f}")
        
        # جعل معدل النمو ثابتًا عند القيمة المدخلة (5% افتراضيًا)
        if growth_rate > Decimal('0.15'):
            growth_rate = Decimal('0.15')
            logs.append("⚠️ تم تعديل معدل النمو ليكون أكثر تحفظًا (15% كحد أقصى)")
        
        # حساب التدفقات النقدية المستقبلية بمعدل نمو ثابت
        fcf_list = []
        for year in range(1, years + 1):
            fcf = base_fcf * (Decimal(1) + growth_rate) ** Decimal(year)
            fcf_list.append(fcf)
            logs.append(f"📈 السنة {year}: FCF = {fcf:,.2f} (معدل النمو: {growth_rate*100:.2f}%)")
        
        # حساب القيمة الحالية للتدفقات النقدية
        present_values = []
        for i, fcf in enumerate(fcf_list, 1):
            pv = fcf / (Decimal(1) + discount_rate) ** Decimal(i)
            present_values.append(pv)
            logs.append(f"📉 القيمة الحالية للسنة {i}: {pv:,.2f}")
        
        # حساب القيمة النهائية (Terminal Value) بمعدل نمو دائم 2.5%
        terminal_growth = Decimal('0.05')  # 2.5% نمو دائم
        last_fcf = fcf_list[-1]
        terminal_value = (last_fcf * (Decimal(1) + terminal_growth)) / (discount_rate - terminal_growth)
        terminal_value_discounted = terminal_value / (Decimal(1) + discount_rate) ** Decimal(years)
        
        logs.append(f"🏁 القيمة النهائية بعد {years} سنوات:")
        logs.append(f"- معدل النمو الدائم: {terminal_growth*100:.2f}%")
        logs.append(f"- القيمة النهائية: {terminal_value:,.2f}")
        logs.append(f"- القيمة الحالية للقيمة النهائية: {terminal_value_discounted:,.2f}")
        
        # حساب القيمة الإجمالية
        enterprise_value = sum(present_values) + terminal_value_discounted
        equity_value = enterprise_value - debt + cash
        fair_value = equity_value / shares_outstanding
        
        logs.append(f"📊 نتائج التقييم:")
        logs.append(f"- قيمة المنشأة (Enterprise Value): {enterprise_value:,.2f}")
        logs.append(f"- قيمة حقوق الملكية (Equity Value): {equity_value:,.2f}")
        logs.append(f"- القيمة العادلة للسهم: {fair_value:.2f} ريال")
        
        # تحليل الحساسية
        if market_price:
            market_price = to_decimal(market_price)
            margin_of_safety = (fair_value - market_price) / fair_value * Decimal(100)
            logs.append(f"🔍 تحليل الحساسية:")
            logs.append(f"- سعر السوق الحالي: {market_price:.2f} ريال")
            logs.append(f"- هامش الأمان: {margin_of_safety:.2f}%")
            
            if margin_of_safety > Decimal('30'):
                logs.append("💡 الاستثناء: هامش أمان عالي (>30%) - فرصة استثمارية جيدة")
            elif margin_of_safety < Decimal('-10'):
                logs.append("⚠️ تحذير: السهم مقيم بأعلى من قيمته العادلة (>10%)")
        
        return float(round(fair_value, 2)), logs

    except Exception as e:
        import traceback
        logs.append(f"❌ خطأ أثناء التقييم: {str(e)}")
        logs.append(f"🔧 تفاصيل الخطأ: {traceback.format_exc()}")
        return None, logs

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        df = pd.read_excel(EXCEL_PATH, skiprows=2)  # تخطي رؤوس الأعمدة
        selected_company = None
        fair_value = None
        logs = []
        
        if request.method == 'POST':
            selected_company = request.form['company']
            row = df[df['الشركة'] == selected_company].iloc[0]
            
            fair_value, logs = evaluate_dcf_model(
                net_income=row.get('صافي الدخل (ر.س بالمليون)', 0),
                shares_outstanding=row.get('الأسهم المصدره (بالمليون)', 1),
                market_price=row.get('سعر الإغلاق', None),
                equity=row.get('حقوق المساهمين (ر.س بالمليون)', 0),
                debt=row.get('الدين', 0),
                cash=row.get('النقدية', 0),
                operating_cash_flow=row.get('التدفق النقدي التشغيلي', None),
                capital_expenditures=row.get('مصروفات الاستثمار', None),
                growth_rate=request.form.get('growth_rate', 5.0),
                discount_rate=request.form.get('discount_rate', 10.0),
                years=request.form.get('years', 5)
            )
        
        companies = df['الشركة'].dropna().unique().tolist()
        return render_template("index.html", 
                             companies=companies, 
                             selected=selected_company, 
                             fair_value=fair_value, 
                             logs=logs)
    
    except Exception as e:
        return render_template("error.html", error=str(e))

if __name__ == '__main__':
    app.run(debug=True)