from app import create_app
import matplotlib
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial']  # أو أي خط متاح
from app.visitor_tracker import get_visitor_count
print("📈 عدد الزوار الآن:", get_visitor_count())

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
