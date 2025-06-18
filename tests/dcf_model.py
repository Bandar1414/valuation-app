import numpy as np

def calculate_dcf(fcf_list, discount_rate, terminal_growth=0.02, terminal_year=5):
    """
    حساب DCF مع ضبط نهائي للمعاملات
    """
    try:
        if discount_rate <= terminal_growth:
            raise ValueError("معدل الخصم يجب أن يكون أكبر من معدل النمو النهائي")
            
        years = np.arange(1, terminal_year + 1)
        pv_explicit = np.sum(fcf_list / (1 + discount_rate) ** years)
        
        terminal_value = (fcf_list[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / (1 + discount_rate) ** terminal_year
        
        return pv_explicit + pv_terminal
        
    except Exception as e:
        print(f"❌ خطأ في حساب DCF: {str(e)}")
        return None


def calculate_fair_value(net_income, shares_outstanding, 
                        growth_rate=0.05, discount_rate=0.10,
                        years=5, fcf_conversion=0.75):
    """
    النسخة النهائية المؤكدة مع معادلة مبسطة
    """
    try:
        if net_income <= 0 or shares_outstanding <= 0:
            raise ValueError("بيانات الإدخال يجب أن تكون موجبة")
            
        if growth_rate >= discount_rate:
            raise ValueError("معدل النمو يجب أن يكون أقل من معدل الخصم")
        
        # حساب التدفق النقدي الحر الأساسي
        base_fcf = net_income * fcf_conversion
        
        # توليد التدفقات النقدية المتوقعة
        fcf_list = np.array([base_fcf * ((1 + growth_rate) ** year) for year in range(1, years+1)])
        
        # حساب قيمة الشركة
        enterprise_value = calculate_dcf(
            fcf_list=fcf_list,
            discount_rate=discount_rate,
            terminal_year=years
        )
        
        if enterprise_value is None:
            raise ValueError("تعذر حساب قيمة الشركة")
            
        return round(enterprise_value / shares_outstanding, 2)
        
    except Exception as e:
        print(f"⚠️ {str(e)}")
        return None