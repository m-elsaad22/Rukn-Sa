# Phase 3 — إعادة كتابة مقالات عدم تطابق النية (`/sa/`)

- التشغيل: `20260922T024538Z`
- الوضع: APPLY (كتابة ووردبريس)
- المصدر: كتالوج فريد لكل سلَج (Cloud Agent LLM) لا استبدال اسم مدينة
- واتساب: `https://wa.me/971586634710` — لا أرقام tel
- المقالات المؤهلة في هذه المرحلة: **38** (شحن سيارات 8، شحن داخلي 8، شحن أثاث 7، دكت 7، غسيل مكيفات 8)

## النطاق وما لم يُعاد كتابته

باقي مقالات /sa/ بعد مرحلة 2 (إزالة القوالب من 1635 مقالاً) تُعامل KEEP: ليست ضمن مجموعة عدم تطابق النية (38). لا حذف. أزواج التعارض داخل المدينة مسجّلة في cannibal-plan.csv (54 مسودة + redirects.csv للاستيراد اليدوي في Rank Math).

لا نشر لتصنيفات السيارات/الأعمال/القانون الناقصة من CSV. لا اختراع أسعار أو تقييمات أو فروع أو رخص.

## عدد الكلمات

القالب القديم تجاوز 1700 كلمة لأنه كان يكرر شقق/فلل/رخام/موسم ذروة على عنوان خدمة أخرى. بعد التصحيح النية تطابق العنوان وبصمات H2 فريدة وcosine < 0.90 بين الـ 38. عدد الكلمات الحالي ~360–1100 لأن الحشو غير المتعلق بالخدمة حُذف ولم يُستبدل بعبارات مخترعة (أسعار، فروع، رخص، تقييمات). إطالة كل صفحة إلى 1000 كلمة بنفس الجمل المعاد تدويرها كانت ستعيد مشكلة القالب.

## جدول المقالات

| URL | المشاكل السابقة | ماذا تغيّر | ماذا أُضيف | كلمات | روابط داخلية | صفحات مشابهة | القرار | ملاحظات |
|---|---|---|---|---|---|---|---|---|
| https://www.rukn-eltatawer.com/sa/car-shipping-jeddah/ | النص السابق يتحدث عن تشطيب وشقق؛ صورة سباكة داخل مقال سيارات | إعادة كتابة كاملة حول نقل المركبات والميناء وأحياء جدة | مسار ما بعد الخروج من جدة؛ حدود خدمة الميناء؛ روابط لشحن الأثاث والشحن الداخلي؛ قائمة رسالة واتساب؛ اعتذار عن القبو الضيق والميناء غير الجاهز | 1092 | `furniture-shipping-jeddah`, `domestic-shipping-jeddah` | `car-shipping-riyadh`, `car-shipping-mecca`, `domestic-shipping-jeddah` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/car-shipping-riyadh/ | نية منزل/عقار على عنوان سيارات | محتوى جديد عن محور الرياض والمسارات الداخلية | توثيق تحت الغبار والحرارة؛ حدود الأثاث مقابل المركبة؛ نافذة الدائري؛ رفض ضم بلدات نجد إلى عنوان الرياض | 742 | `furniture-shipping-riyadh`, `domestic-shipping-riyadh` | `car-shipping-jeddah`, `car-shipping-dammam` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/car-shipping-dammam/ | صياغة انتقال منازل | تمييز الصناعي/السكني وفصل الخبر عن الدمام | رابط شحن الخبر؛ ملاحظة الرطوبة دون وعد طلاء؛ فصل القطيف/الظهران؛ إفراغ المقصورة قبل طريق الرياض | 620 | `car-shipping-khobar`, `domestic-shipping-dammam` | `car-shipping-khobar`, `car-shipping-riyadh` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/car-shipping-khobar/ | تكرار نية الدمام/المنازل | زاوية كورنيش الخبر وفصل الظهران | قيود العمائر؛ رابط الدمام؛ قيود أبراج الكورنيش؛ رفض القيادة بالوكالة | 552 | `car-shipping-dammam`, `furniture-shipping-khobar` | `car-shipping-dammam` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/car-shipping-mecca/ | قالب منازل على عنوان سيارات | محتوى مواسم مكة ونقاط الالتقاء دون ادعاء تصاريح | حدود المنطقة المركزية؛ مسارات جدة/الطائف؛ نقاط التقاء خارج الزحام؛ رفض تصاريح مختلقة | 574 | `car-shipping-jeddah`, `car-shipping-taif` | `car-shipping-medina`, `car-shipping-jeddah` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/car-shipping-medina/ | قالب عقار | نقاط الالتقاء والمسافات الطويلة من المدينة | رابط الشحن الداخلي؛ الكلاسيك كاستثناء؛ فصل النطاق المزدحم؛ البطارية بعد الوقوف الطويل | 522 | `domestic-shipping-medina`, `car-shipping-riyadh` | `car-shipping-mecca` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/car-shipping-taif/ | قالب منازل | زاوية الطريق الجبلي والصيف دون اختراع معدات | الهدا كنقطة حساسة؛ رابط أثاث الطائف؛ عقبة الهدا والضباب؛ رفض شحن أدوات المزرعة داخل المقصورة | 511 | `furniture-shipping-taif`, `car-shipping-mecca` | `car-shipping-abha`, `car-shipping-mecca` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/car-shipping-abha/ | قالب منازل | تمييز عسير والضباب ورفض اختراع الفروع | خميس مشيط كمدينة مجاورة؛ رفض الأثاث فوق المركبة؛ فصل خميس مشيط؛ رفض الأثاث فوق المركبة | 494 | `furniture-shipping-abha`, `domestic-shipping-abha` | `car-shipping-taif` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/domestic-shipping-dammam/ | أسئلة الشقق والفلل | إعادة توجيه النية إلى الطرود والبضاعة | حدود المواد الخطرة؛ فصل السيارة/الأثاث؛ بطاقة الصندوق؛ رفض المواد الخطرة والتلف السريع | 591 | `car-shipping-dammam`, `furniture-shipping-dammam` | `domestic-shipping-khobar`, `domestic-shipping-riyadh` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/domestic-shipping-khobar/ | أسئلة فلل | زاوية المكاتب والكورنيش | منع العربات؛ رابط الدمام؛ قيود أبراج المكاتب؛ رفض الأصول الوحيدة بلا نسخة | 453 | `domestic-shipping-dammam`, `car-shipping-khobar` | `domestic-shipping-dammam` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/domestic-shipping-riyadh/ | أسئلة فلل | الحرارة والتجميع داخل العاصمة | رابط شحن السيارات؛ تغليف يتحمل حر الرياض؛ فصل الأثاث عن الطرد | 461 | `car-shipping-riyadh`, `furniture-shipping-riyadh` | `domestic-shipping-jeddah` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/domestic-shipping-jeddah/ | أسئلة فلل | الرطوبة وحدود الميناء | روابط السيارة والأثاث؛ حماية الكرتون من رطوبة جدة؛ فصل الميناء والسيارة | 480 | `car-shipping-jeddah`, `furniture-shipping-jeddah` | `domestic-shipping-mecca` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/domestic-shipping-mecca/ | أسئلة فلل | قيود المواسم ونقطة الاستلام | التمييز عن بريد الحجاج؛ قيود المواسم؛ رفض هوية بريد الحجاج | 406 | `domestic-shipping-jeddah`, `car-shipping-mecca` | `domestic-shipping-medina` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/domestic-shipping-medina/ | أسئلة فلل | المسافة الطويلة والتغليف | رابط سيارات المدينة؛ ضغط الكرتون على الطريق؛ فصل الأثاث | 363 | `car-shipping-medina`, `domestic-shipping-riyadh` | `domestic-shipping-mecca` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/domestic-shipping-taif/ | أسئلة فلل | الاهتزاز الجبلي والزجاج | رفض اختراع مستودع تبريد؛ التوسيد قبل العقبة؛ الإفصاح عن السوائل الزراعية | 373 | `car-shipping-taif`, `furniture-shipping-taif` | `domestic-shipping-abha` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/domestic-shipping-abha/ | أسئلة فلل | الضباب والقرى المجاورة | رفض سلسلة تبريد مختلقة؛ فصل مدن عسير؛ الإفصاح عن العبوات المضغوطة | 380 | `furniture-shipping-abha`, `car-shipping-abha` | `domestic-shipping-taif` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/furniture-shipping-dammam/ | أسئلة فلل على شحن أثاث | تفكيك وتغليف وخشب رطب | الخزائن المدمجة؛ فصل السيارة/الطرود؛ المصعد والفك؛ الرطوبة على الخشب | 462 | `car-shipping-dammam`, `domestic-shipping-dammam` | `furniture-shipping-khobar` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/furniture-shipping-khobar/ | أسئلة فلل | زاوية العمائر والمصعد | رفض مستودع مختلق؛ قيود أبراج الخبر؛ الزجاج في الممرات الضيقة | 428 | `furniture-shipping-dammam`, `domestic-shipping-khobar` | `furniture-shipping-dammam` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/furniture-shipping-riyadh/ | أسئلة فلل | الحرارة والمجمعات | تصريح الحارس؛ النقل داخل المدينة؛ ظل التحميل؛ رفض تركيب الديكور في الوصول | 450 | `car-shipping-riyadh`, `domestic-shipping-riyadh` | `furniture-shipping-jeddah` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/furniture-shipping-jeddah/ | خلط مع تنظيف منازل | الرطوبة الساحلية ورفض التنظيف | التمييز عن تنظيف الكنب؛ تغطية المعدن من الرطوبة؛ فصل المكيف عن العفش | 431 | `car-shipping-jeddah`, `domestic-shipping-jeddah` | `furniture-shipping-riyadh` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/furniture-shipping-taif/ | أسئلة فلل | الربط قبل الهبوط الجبلي | الهدا كنقطة صعبة؛ توسيد العقبة؛ البيوت الموسمية | 407 | `car-shipping-taif`, `domestic-shipping-taif` | `furniture-shipping-abha` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/furniture-shipping-abha/ | أسئلة فلل | الشاحنة والجبل والتوثيق | رفض كسر الجدار؛ مداخل القرى؛ رفض دمج خميس في عنوان أبها | 430 | `car-shipping-abha`, `domestic-shipping-abha` | `furniture-shipping-taif` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/furniture-shipping-medina/ | أسئلة فلل | المسافة الطويلة والتوسيد | سياسة إعادة التركيب؛ توسيد المسافة الطويلة؛ مرونة أوقات الزحام | 388 | `car-shipping-medina`, `domestic-shipping-medina` | `furniture-shipping-riyadh` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/duct-cleaning-dammam/ | رخام/خشب/كنب في مقال دكت | إعادة النية لمجاري الهواء والرطوبة الشرقية | التمييز عن غسيل الوحدة؛ حدود الفتحات المغلقة؛ علامات الغبار الأسود؛ حدود الفتحة المغلقة | 554 | `ac-cleaning-washing-dammam` | `duct-cleaning-khobar`, `ac-cleaning-washing-dammam` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/duct-cleaning-khobar/ | رخام/خشب | زاوية العمائر والملح | الدكت المشترك؛ ملح الكورنيش؛ رفض كسر الرخام للوصول | 464 | `ac-cleaning-washing-khobar`, `duct-cleaning-dammam` | `duct-cleaning-dammam` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/duct-cleaning-riyadh/ | رخام/خشب | غبار العاصمة مقابل السبليت | رفض أرقام جودة هواء مختلقة؛ عدد الفتحات لا مساحة الأرض؛ فصل نقص الغاز | 476 | `ac-cleaning-washing-riyadh` | `duct-cleaning-jeddah` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/duct-cleaning-jeddah/ | رخام/خشب | الرائحة والرطوبة الساحلية | التمييز عن التسربات؛ العفن عند الفتحة مقابل تسرب السقف؛ فصل السبليت بلا دكت | 460 | `ac-cleaning-washing-jeddah` | `duct-cleaning-mecca` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/duct-cleaning-mecca/ | رخام/خشب | الموسم والشقق الاستثمارية | فترة الفراغ بين العقود؛ التشغيل بعد إغلاق مواسمي؛ حدود الشبكة | 420 | `ac-cleaning-washing-mecca` | `duct-cleaning-medina` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/duct-cleaning-medina/ | رخام/خشب | الشفط والغبار الجاف | حدود صيانة الكمبروسر؛ تقليل انتشار الغبار؛ رفض فك الكمبروسر هنا | 421 | `ac-cleaning-washing-medina` | `duct-cleaning-mecca` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/duct-cleaning-taif/ | رخام/خشب | الاستخدام الموسمي | التشغيل بعد الإغلاق؛ التشغيل بعد الإغلاق الطويل؛ البيوت الصيفية | 406 | `ac-cleaning-washing-taif` | `ac-cleaning-washing-taif` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-riyadh/ | رخام/خشب/كنب | غسيل وحدات ظاهرة مقابل الدكت والغاز | حدود الفريون؛ رابط الدكت؛ حدود الفريون؛ إذن السطح | 500 | `duct-cleaning-riyadh` | `ac-cleaning-washing-jeddah`, `duct-cleaning-riyadh` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-jeddah/ | رخام/خشب | الملح الساحلي والتصريف | حدود الصدأ القديم؛ ملح المكثف؛ التصريف دون جلي الأرض | 475 | `duct-cleaning-jeddah` | `ac-cleaning-washing-khobar` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-dammam/ | رخام/خشب | الغبار الصناعي وفصل الخبر | رابط خبر؛ غبار صناعي؛ رفض خلط الجلي | 390 | `duct-cleaning-dammam`, `ac-cleaning-washing-khobar` | `ac-cleaning-washing-khobar` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-khobar/ | رخام/خشب | البلكونة والجيران | مسار ماء الغسيل؛ مسار ماء الغسيل؛ ملح الكورنيش على المكثف | 391 | `duct-cleaning-khobar`, `ac-cleaning-washing-dammam` | `ac-cleaning-washing-jeddah` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-mecca/ | رخام/خشب | فصل الجهاز والمواسم | الشقق الاستثمارية؛ التشغيل بعد إغلاق مواسمي؛ شرط فصل الكهرباء | 416 | `duct-cleaning-mecca` | `ac-cleaning-washing-medina` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-medina/ | رخام/خشب | الفلتر والغبار الجاف | صيانة المالك للفلتر؛ فلتر المالك؛ التصريف الظاهر | 413 | `duct-cleaning-medina` | `ac-cleaning-washing-riyadh` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-taif/ | رخام/خشب | الإغلاق الموسمي والمنحدر | رفض ماركة فلتر مختلقة؛ غبار الإغلاق الموسمي؛ ربط الغسيل بالتشغيل لا بشعار صيف | 415 | `duct-cleaning-taif` | `ac-cleaning-washing-abha` | KEEP | applied Rank Math: ok |
| https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-abha/ | رخام/خشب | الرطوبة الجبلية ورفض الفروع | سلامة الوصول؛ سلامة السطح في الضباب؛ عدم اختراع صفحة دكت لأبها | 466 | `car-shipping-abha` | `ac-cleaning-washing-taif` | KEEP | applied Rank Math: ok |

## Final Similarity Audit

قياس cosine على كيس كلمات 4096-بعد بعد تطبيع أسماء المدن (نفس أسلوب `seo_content_audit.py`). العتبة 0.90.

لا أزواج بـ cosine ≥ 0.90 بين المقالات المعاد كتابتها.

## قرارات KEEP / CONSOLIDATE / DELETE

- **KEEP**: كل الـ 38 بعد إعادة الكتابة — نية مستقلة لكل سلَج.
- **CONSOLIDATE**: لا دمج حذف في هذه المرحلة. خطة التعارض السابقة تبقى مسودات Rank Math.
- **DELETE**: لا شيء. ممنوع حذف الصفحات المتشابهة؛ التقرير فقط.

## تحقق تقني لكل مقال

- لا H1 داخل المحتوى (العنوان من القالب).
- `[post_call]` مرتان.
- صورة بارزة موجودة تُعاد بألت نص يطابق الخدمة (لا plumber.webp).
- واتساب الإمارات حتى يتوفر رقم سعودي.

عيّنة أمامية بعد التفريغ: `/duct-cleaning-dammam/` و`/car-shipping-jeddah/` بلا سؤال الفلل وبلا `0568060309`، مع واتساب `971586634710` والنص الفريد في الجسم. حقول FAQ/NAP للقالب حُدّثت للـ 38. استيراد `redirects.csv` في Rank Math ما زال يدوياً.

