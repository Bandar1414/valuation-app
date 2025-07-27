import os
import subprocess
from datetime import datetime

# الانتقال إلى مجلد المشروع
project_folder = r"C:\Users\USER\Videos\New folder"
os.chdir(project_folder)

def auto_commit_push():
    try:
        # إضافة كل الملفات (حتى غير المتتبعة)
        subprocess.run(["git", "add", "."], check=True)

        # تنفيذ الـ commit
        subprocess.run(["git", "commit", "-m", f"تحديث تلقائي {datetime.now()}"], check=True)

        # تنفيذ الـ push
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print("✅ تم رفع كافة الملفات بنجاح إلى GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ أثناء تنفيذ Git: {e}")
    except Exception as ex:
        print(f"⚠️ حدث خطأ غير متوقع: {ex}")

if __name__ == "__main__":
    auto_commit_push()
