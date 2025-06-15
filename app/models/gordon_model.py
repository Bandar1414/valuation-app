def calculate_gordon(eps, growth_rate, discount_rate):
    """
    نموذج جوردون المعدل مع معالجة أفضل للأخطاء
    """
    try:
        # التحقق من القيم الأساسية
        if None in [eps, growth_rate, discount_rate]:
            return None
            
        # ضمان أن معدل النمو أقل من معدل الخصم
        safe_growth = min(growth_rate, discount_rate - 0.01)
        
        # الحساب مع حدود أمان
        fair_value = eps * (1 + safe_growth) / (max(0.01, discount_rate - safe_growth))
        return round(fair_value, 2)
        
    except Exception as e:
        print(f"Error in Gordon model: {str(e)}")
        return None

# دالة calculate الجديدة (بدون تغيير الدالة الأصلية)
def calculate(eps, growth_rate, discount_rate):
    """
    واجهة متوافقة مع النظام الحالي
    """
    return calculate_gordon(eps, growth_rate, discount_rate)