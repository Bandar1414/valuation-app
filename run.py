from app import create_app

import matplotlib
matplotlib.use("Agg")  # مهم للسيرفرات بدون واجهة رسومية
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Arial"]

from app.visitor_tracker import get_visitor_count

print("📈 عدد الزوار الآن:", get_visitor_count())

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
