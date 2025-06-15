def calculate_greenfield(initial_investment, growth_rate, discount_rate, years=5):
    """
    نموذج جرينفيلد (Greenfield Model) لتقييم الاستثمار الجديد
    - initial_investment: قيمة الاستثمار المبدئي (مليون ر.س)
    - growth_rate: معدل النمو المتوقع سنويًا (بنسبة عشرية، مثلاً 0.05 لـ 5%)
    - discount_rate: معدل الخصم (بنسبة عشرية، مثلاً 0.10 لـ 10%)
    - years: عدد سنوات التقييم (افتراضي 5 سنوات)

    يعيد القيمة العادلة الحالية للاستثمار مع نموه المستقبلي.
    """

    if discount_rate <= growth_rate:
        raise ValueError("معدل الخصم يجب أن يكون أكبر من معدل النمو")

    npv = 0
    for t in range(1, years + 1):
        cash_flow = initial_investment * ((1 + growth_rate) ** t)
        npv += cash_flow / ((1 + discount_rate) ** t)

    return round(npv, 2)
