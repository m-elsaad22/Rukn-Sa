# تهيئة الفهرسة: إزالة التكرار + إغناء فريد + حماية تقنية

**التاريخ:** 3 سبتمبر 2026  
**الفرع:** `cursor/dedupe-index-ready-81c2`  
**الموقع:** https://www.rukn-eltatawer.com/sa

## التشخيص قبل الإصلاح
- آلاف المسودات/المقالات كانت شبه قالب واحد مع جمل مشتركة عبر مدن كثيرة.
- نشر سريع لكمية متشابهة يضر الفهرسة (Discovered/Crawled — currently not indexed).
- صفحات EN كانت ضعيفة الحجم.

## ما تم
1. **محرك تفرّد محلي** (`scripts/index_ready_dedupe_all.py`) لكل مقال حسب (المدينة + نوع الخدمة) مع أحياء/مناخ/حالات وروابط داخلية للمحاور.
2. إعادة كتابة: طابور 48 ساعة → كل المنشور → بقية future القالبي.
3. **إبطاء الجدولة** للبعيد من ~10 دقائق إلى ~45 دقيقة لتقليل ضغط الزحف الضار.
4. Snippet `#14` `Rukn SA Index Ready Hardening`: تثبيت Sitemap `/sa` + فرض `index,follow`.
5. تقوية 3 صفحات EN الأساسية (~450–500 كلمة) مع ربط عربي/داخلي — بدون إنشاء مئات EN ضعيفة.

## التحقق الحي (بعد المعالجة)
| مؤشر | النتيجة |
|------|---------|
| publish / future / draft | 183 / 1576 / **0** |
| قالب «دليل شامل 2026» | **0** |
| علامة محرك التفرّد | **1658** |
| عربي ≥900 كلمة | **1756** من 1759 |
| thin (عربي&lt;900 و EN&lt;250) | **0** |
| هاتف خاطئ / placeholders | **0** |
| Snippets نشطة | #5 #7 #8 #11 #12 #14 |

## صفحات EN
- https://www.rukn-eltatawer.com/sa/en-water-leak-detection-riyadh/ (~498 كلمة)
- https://www.rukn-eltatawer.com/sa/en-roof-waterproofing-riyadh/ (~447 كلمة)
- https://www.rukn-eltatawer.com/sa/en-home-cleaning-riyadh/ (~454 كلمة)

## لماذا هذا أسرع للفهرسة بدون ضرر؟
- جوجل يفهرس المحتوى **المتمايز** أسرع من آلاف النسخ المتشابهة.
- تقليل معدل النشر المتشابه يقلل احتمال تجاهل الصفحات.
- `index,follow` + sitemap `/sa` الصحيح يسهّلان الاكتشاف.

## ما لن نفعله (لأنه يضر)
- إنشاء مئات صفحات EN ضعيفة لكل مقال عربي (doorway risk).
- إعادة إطلاق 1600 نسخة متطابقة دفعة واحدة.

## مطلوب يدوياً (خارج صلاحية الـ API)
1. أضف في `robots.txt` الجذري (غير `/sa`):
   `Sitemap: https://www.rukn-eltatawer.com/sa/sitemap_index.xml`
   (حالياً الجذر يذكر فقط sitemap الإمارات و `/qa`).
2. في GSC اطلب فهرسة يدوياً لـ 15–20 رابط أولوية فقط:

```
https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh/
https://www.rukn-eltatawer.com/sa/roof-insulation-riyadh/
https://www.rukn-eltatawer.com/sa/en-water-leak-detection-riyadh/
https://www.rukn-eltatawer.com/sa/en-roof-waterproofing-riyadh/
https://www.rukn-eltatawer.com/sa/en-home-cleaning-riyadh/
https://www.rukn-eltatawer.com/sa/water-leak-detection-mecca/
https://www.rukn-eltatawer.com/sa/water-pipe-leak-detection-jeddah/
https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-jeddah/
https://www.rukn-eltatawer.com/sa/split-ac-maintenance-jeddah/
https://www.rukn-eltatawer.com/sa/ac-duct-maintenance-jeddah/
https://www.rukn-eltatawer.com/sa/central-ac-maintenance-jeddah/
https://www.rukn-eltatawer.com/sa/ac-periodic-maintenance-contracts-jeddah/
https://www.rukn-eltatawer.com/sa/steam-disinfection-mecca/
https://www.rukn-eltatawer.com/sa/ozone-disinfection-mecca/
https://www.rukn-eltatawer.com/sa/tanzif-sijjad-wamaukit-bilriyadh/
```

## ملاحظة صدق
لا يمكن ضمان ترتيب فوري؛ الفهرسة تعتمد على زحف جوجل والمنافسة. ما تم يجعل الصفحات **مؤهلة** للفهرسة (فريدة، قابلة للفهرسة، بدون قوالب/هواتف تالفة) بأقل ضرر ممكن.
