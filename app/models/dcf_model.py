def calculate_dcf(fcf_list, discount_rate, growth_rate, terminal_year=5):
    """
    حساب نموذج التدفقات النقدية المخصومة (DCF)
    """
    if not fcf_list or discount_rate is None or growth_rate is None:
        return None
    
    try:
        # حساب القيمة الحالية للتدفقات النقدية
        pv_cash_flows = 0
        for year, fcf in enumerate(fcf_list[:terminal_year], 1):
            pv_cash_flows += fcf / ((1 + discount_rate) ** year)
        
        # حساب القيمة النهائية
        terminal_value = (fcf_list[-1] * (1 + growth_rate)) / (discount_rate - growth_rate)
        pv_terminal = terminal_value / ((1 + discount_rate) ** terminal_year)
        
        total_value = pv_cash_flows + pv_terminal
        return round(total_value, 2)
    except:
        return None

# دالة calculate الجديدة (بدون تغيير الدالة الأصلية)
def calculate(net_income, shares_outstanding, growth_rate, discount_rate):
    """
    واجهة متوافقة مع النظام الحالي
    """
    try:
        if None in [net_income, shares_outstanding, growth_rate, discount_rate]:
            return None
            
        eps = net_income / shares_outstanding
        return calculate_gordon(eps, growth_rate, discount_rate)  # نستخدم نفس منطق جوردون للتوافق
    except Exception as e:
        print(f"Error in DCF calculate: {str(e)}")
        return None