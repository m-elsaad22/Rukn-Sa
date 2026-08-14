# Rukn-Sa

مستودع تحليل وتحسين محتوى موقع [ركن التطور - السعودية](https://www.rukn-eltatawer.com/sa).

## التقارير

- [تقرير تدقيق المحتوى — 14 أغسطس 2026](reports/content-audit-2026-08-14.md)
- بيانات مفصّلة: [`data/articles-audit.csv`](data/articles-audit.csv) · [`data/audit-summary.json`](data/audit-summary.json)

## إعادة تشغيل التدقيق

```bash
export WP_USER='cursor'
export WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx'
python3 scripts/audit_content.py
```
