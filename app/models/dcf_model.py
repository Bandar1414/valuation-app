import math

def evaluate_dcf_model(
    net_income,
    shares_outstanding,
    growth_rate=5.0,
    discount_rate=10.0,
    years=5,
    manual_fcf=None,
    debt=0,
    cash=0,
    market_price=None
):
    try:
        print("✨ بدء التقييم الدقيق لنموذج DCF ✨")

        # تصحيح تلقائي للنسب
        def fix_rate(rate):
            rate = float(rate)
            return rate / 100 if rate > 1 else rate

        growth_rate = fix_rate(growth_rate)
        discount_rate = fix_rate(discount_rate)
        years = int(years)

        # لا تحويل إلى مليون لأن القيم أصلًا بالمليون من المصدر
        net_income_m = float(net_income)
        shares_m = float(shares_outstanding)
        debt_m = float(debt)
        cash_m = float(cash)

        print(f"🔍 البيانات المحولة: NI={net_income_m:.2f}M, الأسهم={shares_m:.2f}M")

        if shares_m <= 0:
            raise ValueError("عدد الأسهم يجب أن يكون موجباً")

        # حساب FCF
        if manual_fcf is not None:
            base_fcf = float(manual_fcf)
        elif net_income_m <= 0:
            print("⚠️ استخدام 30% من حقوق المساهمين كتدفق نقدي")
            equity = abs(net_income_m)
            base_fcf = equity * 0.3
        else:
            base_fcf = net_income_m * 1.0

        print(f"📊 التدفق النقدي الحر: {base_fcf:.2f}M")

        # التدفقات المستقبلية
        fcf_list = [base_fcf * ((1 + growth_rate) ** year) for year in range(1, years + 1)]
        print(f"📈 التدفقات لـ {years} سنوات: {[f'{x:,.2f}M' for x in fcf_list]}")

        present_values = [fcf / ((1 + discount_rate) ** i) for i, fcf in enumerate(fcf_list, 1)]

        terminal_growth = growth_rate * 0.5
        terminal_value = (fcf_list[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        terminal_value_discounted = terminal_value / ((1 + discount_rate) ** years)

        enterprise_value = sum(present_values) + terminal_value_discounted
        equity_value = enterprise_value - debt_m + cash_m

        fair_value = equity_value / shares_m

        print(f"💎 القيمة العادلة: {fair_value:.2f} (السوق: {market_price if market_price else 'غير معروف'})")
        print(f"🔢 المعطيات: النمو={growth_rate*100:.1f}%, الخصم={discount_rate*100:.1f}%, السنوات={years}")

        return round(fair_value, 2)

    except ZeroDivisionError:
        print("❌ خطأ: معدل الخصم يجب أن يكون أكبر من معدل النمو")
        return None
    except ValueError as ve:
        print(f"❌ خطأ في القيم: {str(ve)}")
        return None
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        return None
