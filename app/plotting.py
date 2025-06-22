import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import font_manager
from io import BytesIO
import base64
import os

# تحميل الخط من المسار المحلي داخل المشروع
font_path = os.path.join('fonts', 'Cairo-Regular.ttf')
cairo_font = font_manager.FontProperties(fname=font_path)

def generate_plot(values_dict, title):
    # إعداد الرسم البياني
    plt.style.use('seaborn-v0_8')  # لتجنب خطأ seaborn
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # ألوان مخصصة
    colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', 
              '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac']
    
    # إنشاء الأعمدة
    bars = ax.bar(values_dict.keys(), values_dict.values(), color=colors)
    
    # العناوين والتنسيق
    ax.set_title(title, fontsize=16, fontproperties=cairo_font, pad=20)
    ax.set_ylabel('القيمة العادلة (ر.س)', fontproperties=cairo_font)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # المحاور
    plt.xticks(fontproperties=cairo_font, rotation=25, ha='right')
    plt.yticks(fontproperties=cairo_font)

    # طباعة القيم على الأعمدة
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}',
            ha='center', va='bottom',
            fontproperties=cairo_font,
            fontsize=10,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2')
        )
    
    # هوامش
    plt.tight_layout()

    # حفظ الرسم كصورة base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return plot_data

print("📊 الرسم البياني تم توليده باستخدام خط Cairo")

