# إصلاح فهرسة جوجل لموقع /sa

**التاريخ:** 29 أغسطس 2026  
**الموقع:** https://www.rukn-eltatawer.com/sa  
**الفرع:** `cursor/google-indexing-robots-sitemap-81c2`

---

## المشكلة الجذرية

`/sa/robots.txt` كان يعلن خريطة الموقع الخطأ:

```
Sitemap: https://www.rukn-eltatawer.com/sitemap_index.xml   ← موقع الإمارات/الجذر
```

بينما مقالات السعودية موجودة في:

```
https://www.rukn-eltatawer.com/sa/sitemap_index.xml
```

هذا يضعف اكتشاف جوجل لمقالات `/sa/`.

---

## ما تم إصلاحه على الموقع الحي

### 1) robots.txt ✅
الملف الفعلي `/home1/.../public_html/sa/robots.txt` أصبح:

```
Sitemap: https://www.rukn-eltatawer.com/sa/sitemap_index.xml
```

مع الإبقاء على Allow/Disallow الآمنة.

### 2) Snippet حماية دائم ✅
`Rukn SA Google Indexing Fix (robots + schema)` (#8):
- يفرض محتوى robots الصحيح عبر الفلتر
- يثبت `areaServed: Saudi Arabia` + geo الرياض + الهاتف في JSON-LD

### 3) خريطة خدمات CPT ✅
`services-sitemap.xml` ظهر في فهرس الخرائط بعد تفعيل `pt_services_sitemap`.

الخرائط الحالية:
- `post-sitemap.xml`
- `page-sitemap.xml`
- `services-sitemap.xml`
- `category-sitemap.xml`

### 4) إصلاح `#9289` ✅
إزالة روابط `966XXXXXXXXX` واستبدالها بالواتساب الصحيح.

### 5) areaServed ✅
تحقق: موجود في JSON-LD للرئيسية.

---

## ما لا يمكن إكماله من هنا (يحتاجك)

### أ) Google Search Console (إلزامي)
1. أضف خاصية للرابط: `https://www.rukn-eltatawer.com/sa`
2. فعّل التحقق (HTML tag / DNS / الملف)
3. ارفع الخريطة: `https://www.rukn-eltatawer.com/sa/sitemap_index.xml`
4. من فحص العنوان: اطلب فهرسة للصفحات المهمة:
   - الرئيسية
   - `/water-leak-detection-riyadh/`
   - `/roof-insulation-riyadh/`
   - أهم صفحات المدن
5. راقب تقرير «الصفحات» / «لماذا لم يتم الفهرسة؟»

### ب) الموقع الرئيسي (الإمارات) — لا نملك صلاحية REST عليه
يفضّل يدوياً:
1. إضافة في `https://www.rukn-eltatawer.com/robots.txt` سطراً إضافياً:
   `Sitemap: https://www.rukn-eltatawer.com/sa/sitemap_index.xml`
2. وضع رابط واضح من الرئيسية إلى `/sa/` (نسخة السعودية)
3. عند الإمكان: hreflang بين النسختين

### ج) ملاحظة عن Google Ping
`google.com/ping?sitemap=` رجّع 404 لأن جوجل أوقف خدمة الـ ping؛ الاعتماد الآن على GSC فقط.

---

## تحقق سريع بعد الإصلاح

| فحص | النتيجة |
|------|---------|
| `/sa/robots.txt` → خريطة السعودية | ✅ |
| `areaServed` | ✅ |
| `services-sitemap.xml` | ✅ |
| `#9289` بدون XXXX | ✅ |
| صفحات بمeta `index,follow` | ✅ (سابقاً) |

---

## ماذا بعد؟
حتى مع الإصلاح التقني، الظهور في نتائج البحث يحتاج أيام/أسابيع + جودة محتوى + GSC.  
الأولوية التالية للمحتوى: إغناء صفحات المدن القصيرة + صور بارزة.
