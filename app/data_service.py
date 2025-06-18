import pandas as pd
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
EXCEL_PATH = os.path.join(PROJECT_DIR, "stocks_data.xlsx")

def validate_data(df):
    """التحقق من وجود الأعمدة الأساسية والبيانات المطلوبة"""
    required_columns = [
        "الشركة",
        "سعر الإغلاق",
        "الأسهم المصدره (بالمليون)",
        "صافي الدخل (ر.س بالمليون)",
        "حقوق المساهمين (ر.س بالمليون)",
        "العائد على السهم",
        "القيمه الدفتريه"
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"الأعمدة المفقودة في ملف البيانات: {missing_columns}")
        return False
    
    if df.empty:
        print("ملف البيانات فارغ")
        return False
        
    return True

def clean_numeric_data(df, column):
    """تنظيف وتحويل الأعمدة الرقمية مع الاحتفاظ بالقيم السالبة"""
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

def add_s_suffix_for_duplicate_profits(df):
    """إضافة 'مكرر' لصافي الدخل المكرر"""
    col = 'صافي الدخل (ر.س بالمليون)'
    if col in df.columns:
        duplicated_values = df[col][df[col].duplicated(keep=False) & df[col].notna()].unique()
        
        for val in duplicated_values:
            mask = df[col] == val
            df.loc[mask, col] = df.loc[mask, col].astype(str) + " (مكرر)"
    return df

def load_data():
    """تحميل وتنظيف بيانات الشركات من ملف Excel"""
    try:
        df = pd.read_excel(EXCEL_PATH, header=2)
        
        if "الشركة" not in df.columns:
            print("عمود 'الشركة' غير موجود في ملف البيانات")
            return None
            
        df = df.dropna(subset=["الشركة"])
        
        numeric_cols = [
            'سعر الإغلاق', 'الأسهم المصدره (بالمليون)', 'صافي الدخل (ر.س بالمليون)',
            'حقوق المساهمين (ر.س بالمليون)', 'القيمة السوقية (ر.س بالمليون)',
            'العائد على السهم', 'القيمه الدفتريه', 'السعر / القيمه الدفتريه', 'EBIT'
        ]
        
        for col in numeric_cols:
            df = clean_numeric_data(df, col)
        
        df = add_s_suffix_for_duplicate_profits(df)
        
        if not validate_data(df):
            print("تحذير: ملف البيانات يحتوي على مشاكل في الهيكل أو البيانات")
            
        if 'القيمة السوقية (ر.س بالمليون)' not in df.columns:
            if all(col in df.columns for col in ['سعر الإغلاق', 'الأسهم المصدره (بالمليون)']):
                df['القيمة السوقية (ر.س بالمليون)'] = df['سعر الإغلاق'] * df['الأسهم المصدره (بالمليون)']
        
        print(f"تم تحميل بيانات {len(df)} شركة بنجاح")
        return df
        
    except FileNotFoundError:
        print(f"ملف البيانات غير موجود في المسار: {EXCEL_PATH}")
        return None
    except Exception as e:
        print(f"حدث خطأ غير متوقع أثناء تحميل البيانات: {str(e)}")
        return None

def inspect_data(df):
    """فحص جودة البيانات"""
    if df is None:
        print("لا توجد بيانات لفحصها")
        return
    
    print("\n=== ملخص البيانات ===")
    print(f"عدد الشركات: {len(df)}")
    print("\nالأعمدة المتاحة:")
    print(df.columns.tolist())
    
    print("\nالقيم المفقودة لكل عمود:")
    print(df.isnull().sum())
    
    print("\nعينة من البيانات:")
    print(df.head(3).to_dict('records'))