import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from io import BytesIO
import base64

def generate_plot(values_dict, title):
    # إعداد الرسم البياني
    plt.style.use('seaborn')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # ألوان للرسم البياني
    colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', 
              '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac']
    
    # إنشاء الأعمدة
    bars = ax.bar(values_dict.keys(), values_dict.values(), color=colors)
    
    # إضافة العناوين والتنسيق
    ax.set_title(title, fontsize=16, fontname='Cairo', pad=20)
    ax.set_ylabel('القيمة العادلة (ر.س)', fontname='Cairo')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # تنسيق المحاور
    plt.xticks(fontname='Cairo', rotation=25, ha='right')
    plt.yticks(fontname='Cairo')
    
    # إضافة القيم على الأعمدة
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', 
                ha='center', va='bottom', 
                fontname='Cairo',
                fontsize=10,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
    
    # ضبط الهوامش
    plt.tight_layout()
    
    # تحويل الرسم إلى صورة base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return plot_data