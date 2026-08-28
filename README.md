# Rukn-Sa

مستودع تحليل وتحسين محتوى موقع [ركن التطور - السعودية](https://www.rukn-eltatawer.com/sa).

## آخر تنفيذ (14 أغسطس 2026)

- تصحيح 45 رقم هاتف خاطئ/وهمي
- نشر مسودتي تنظيف الباحة
- إعادة كتابة 35 صفحة مدينة هزيلة (~900 كلمة)
- تحديث 9 مقالات محاور + 12 صفحة خدمات

التفاصيل: [`reports/work-log-2026-08-14.md`](reports/work-log-2026-08-14.md)

## سكربتات

```bash
export WP_USER='cursor'
export WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx'
python3 scripts/rewrite_thin_city_pages.py
```


## مقالات احترافية (3500+ كلمة)

- [كشف تسربات المياه في الرياض](https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh/)
- [عزل الأسطح في الرياض](https://www.rukn-eltatawer.com/sa/roof-insulation-riyadh/)
- المعيار: [`templates/professional-article-prompt.md`](templates/professional-article-prompt.md)
