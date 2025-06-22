def calculate(eps, growth_rate, discount_rate, dividends=None):
    """
    نموذج جوردون لحساب القيمة العادلة للسهم.
    - إذا لم تُعطَ توزيعات أرباح، يتم احتسابها من ربحية السهم بنسبة 65%.
    - جميع المدخلات يجب أن تكون أرقام فعلية.
    """
    try:
        # تحويل المدخلات
        eps = float(eps)
        growth_rate = float(growth_rate) / 100  # تحويل إلى نسبة عشرية
        discount_rate = float(discount_rate) / 100

        # إذا لم تُعطَ توزيعات الأرباح، احسبها من ربحية السهم × 65%
        if dividends is None:
            dividends = eps * 0.65
        else:
            dividends = float(dividends)

        # تحقق من أن الخصم أكبر من النمو لتفادي القسمة على صفر
        if discount_rate <= growth_rate:
            return None

        fair_value = dividends / (discount_rate - growth_rate)
        return round(fair_value, 2)
    except Exception as e:
        print(f"خطأ في حساب نموذج جوردون: {e}")
        return None
