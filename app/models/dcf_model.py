def calculate_dcf(fcf_list, discount_rate, growth_rate, terminal_year=5):
    """
    حساب نموذج التدفقات النقدية المخصومة (DCF)
    """
    if not fcf_list or discount_rate is None or growth_rate is None:
        return None

    try:
        # حساب القيمة الحالية للتدفقات النقدية المتوقعة
        pv_cash_flows = 0
        for year, fcf in enumerate(fcf_list[:terminal_year], 1):
            pv_cash_flows += fcf / ((1 + discount_rate) ** year)

        # حساب القيمة النهائية (Terminal Value)
        terminal_value = (fcf_list[-1] * (1 + growth_rate)) / (discount_rate - growth_rate)
        pv_terminal = terminal_value / ((1 + discount_rate) ** terminal_year)

        total_value = pv_cash_flows + pv_terminal
        return round(total_value, 2)
    except:
        return None


def calculate(net_income, shares_outstanding, growth_rate=0.05, discount_rate=0.10, years=5):
    """
    حساب القيمة العادلة باستخدام نموذج DCF مبسط
    يفترض أن صافي الدخل يعبر عن التدفق النقدي الحر (FCF)
    """
    try:
        if None in [net_income, shares_outstanding, growth_rate, discount_rate, years]:
            return None

        # توليد قائمة التدفقات النقدية المستقبلية المتوقعة
        fcf_list = [net_income * ((1 + growth_rate) ** i) for i in range(1, years + 1)]

        total_value = calculate_dcf(
            fcf_list=fcf_list,
            discount_rate=discount_rate,
            growth_rate=growth_rate,
            terminal_year=years
        )

        if total_value is None:
            return None

        # حساب القيمة العادلة للسهم
        fair_value_per_share = total_value / shares_outstanding
        return round(fair_value_per_share, 2)
    except Exception as e:
        print(f"Error in DCF calculate: {str(e)}")
        return None
