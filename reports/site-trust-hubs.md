# إصلاح ثقة الموقع وصفحات الخدمات — /sa

سكربتات تُنفَّذ على الموقع الحي `https://www.rukn-eltatawer.com/sa` عبر REST + Code Snippets.

## الترتيب

1. `scripts/live_snippets.py` — توحيد NAP، حذف رقم مصر من الخيارات/التذييل، عدّادات صادقة، حماية HTML.
2. `scripts/fix_cities_taxonomy.py` — دمج الرياض المكرر وإعادة تصنيف منشورات «السعودية».
3. `scripts/rewrite_service_hubs.py` — تقوية 12 صفحة خدمة CPT.
4. `scripts/fix_core_pages.py` — صفحات المدن والأسعار + تنظيف صياغة من نحن/اتصل/خدماتنا.
5. `scripts/expand_money_pages.py` — توسيع صفحات تجارية محددة (مدن كبرى × خدمات عالية النية).
6. `scripts/assign_featured_images.py` — ربط صور المكتبة حسب نوع الخدمة لا صور المجاري/المسابح العشوائية.

التشغيل: `python3 scripts/run_site_fixes.py`

لا تُختلق أسعار بالريال ولا تقييمات ولا أرقام عملاء. الرقم المعتمد: 0568060309 / واتساب 966568060309.
