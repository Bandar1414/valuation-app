from weasyprint import HTML

html = "<h1>تقرير تجريبي</h1><p>هذا اختبار PDF من WeasyPrint</p>"
HTML(string=html).write_pdf("test_output.pdf")
