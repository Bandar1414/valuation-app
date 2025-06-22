def evaluate_residual_income_model(
    net_income,
    shares_outstanding,
    equity,
    growth_rate=None,
    discount_rate=None,
    market_price=None,
    cost_of_equity=None
):
    """
    حساب القيمة العادلة باستخدام نموذج الدخل المتبقي (Residual Income Model)
    """
    try:
        print("\n✨ بدء التقييم باستخدام نموذج الدخل المتبقي ✨")
        
        # تعيين القيم الافتراضية إذا لم يتم تقديمها
        growth_rate = float(growth_rate) if growth_rate is not None else 5.0
        discount_rate = float(discount_rate) if discount_rate is not None else 10.0
        
        # تحويل النسب المئوية إلى أعداد عشرية
        growth_rate_decimal = float(growth_rate) / 100.0
        discount_rate_decimal = float(discount_rate) / 100.0
        cost_of_equity_decimal = float(cost_of_equity) / 100.0 if cost_of_equity is not None else discount_rate_decimal
        
        # تحقق من أن معدل الخصم > معدل النمو
        if discount_rate_decimal <= growth_rate_decimal:
            raise ValueError("معدل الخصم يجب أن يكون أكبر من معدل النمو")
        
        # عدم تحويل القيم إلى ملايين (افتراض أنها مدخلة بالمليون بالفعل)
        net_income_m = float(net_income)
        shares_outstanding_m = float(shares_outstanding)
        equity_m = float(equity)
        
        print(f"\n📊 البيانات الأساسية (بالمليون):")
        print(f"- صافي الدخل: {net_income_m:.2f}M")
        print(f"- الأسهم القائمة: {shares_outstanding_m:.2f}M")
        print(f"- حقوق المساهمين: {equity_m:.2f}M")
        print(f"- معدل النمو: {growth_rate:.2f}%")
        print(f"- معدل الخصم: {discount_rate:.2f}%")
        if cost_of_equity is not None:
            print(f"- تكلفة حقوق الملكية: {float(cost_of_equity):.2f}%")
        
        # حساب تكلفة حقوق الملكية بالدخل المتبقي
        equity_charge = equity_m * cost_of_equity_decimal
        residual_income = net_income_m - equity_charge
        
        print(f"\n💡 حساب الدخل المتبقي للسنة الحالية:")
        print(f"- تكلفة حقوق الملكية ({cost_of_equity_decimal*100:.1f}% من {equity_m:.2f}M): {equity_charge:.2f}M")
        print(f"- الدخل المتبقي: {residual_income:.2f}M")
        
        # حساب القيمة الحالية للدخل المتبقي المستقبلي
        pv_residual_income = residual_income / (discount_rate_decimal - growth_rate_decimal)
        
        # القيمة الدفترية + القيمة الحالية للدخل المتبقي
        equity_value = equity_m + pv_residual_income
        
        # حساب القيمة العادلة للسهم
        fair_value_per_share = equity_value / shares_outstanding_m
        
        print("\n💎 نتائج التقييم:")
        print(f"- القيمة الدفترية: {equity_m:.2f}M")
        print(f"- القيمة الحالية للدخل المتبقي: {pv_residual_income:.2f}M")
        print(f"- القيمة العادلة للسهم: {fair_value_per_share:.2f} ريال")
        
        if market_price:
            market_price = float(market_price)
            margin = ((fair_value_per_share - market_price) / market_price) * 100
            print(f"\n🔍 مقارنة بالسوق:")
            print(f"- سعر السوق: {market_price:.2f} ريال")
            print(f"- الفرق النسبي: {margin:.2f}%")
        
        return round(fair_value_per_share, 2)
        
    except ZeroDivisionError:
        print("\n❌ خطأ: معدل الخصم يجب أن يكون أكبر من معدل النمو")
        return None
    except ValueError as ve:
        print(f"\n❌ خطأ في القيم المدخلة: {str(ve)}")
        return None
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع في التقييم: {str(e)}")
        return None