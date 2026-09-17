# تدقيق سيو تقني ومحتوى — ركن التطور السعودية

تاريخ التوليد: `2026-09-17T02:35:24.287000+00:00`  
المصدر: `https://www.rukn-eltatawer.com/sa`  
المستندات: **1768** (مقالات 1759 / صفحات 9) — متوسط الكلمات 1815 — الوسيط 1801

## ملخص تنفيذي

المشكلة الأساسية ليست نقص الكلمات بل **قالب واحد يُعاد مع استبدال اسم الخدمة والمدينة**. H1 يُرسم من عنوان المقال في القالب (خارج `post_content`) لذلك غياب H1 داخل الجسم ليس خطأً. أسماء المدن تُطبَّع قبل قياس التشابه؛ التشابه يعني نفس الصياغة وليس مجرد تكرار كلمة «الرياض».

| المؤشر | العدد | التفسير |
|---|---|---|
| مقالات خدمات < 1000 كلمة | 0 | كل المقالات المنشورة تتجاوز الحد |
| صفحات هيكلية < 1000 كلمة | 5 | مدونة/أسعار/مدن/اتصال — متوقع لصفحات أدوات |
| إفراط عبارات قالبية | 1718 | «موسم ذروة» + «هل الخدمة للشقق والفلل» على خدمات غير النقل |
| عناقيد هيكل H2 متطابق | 5 تغطي 182 | نفس تسلسل العناوين بعد توحيد المدينة |
| أزواج متشابهة (cosine ≥ 0.90) | 6996 | منها 129 تعارض داخل نفس المدينة |
| مجموعات تكرار/تعارض كلمات | 200 | city-clone أو صفحتان لنفس النية |
| عدم تطابق نية البحث (حقيقي) | 38 | عنوان خدمة والجسم يتحدث عن خدمة أخرى |
| أخطاء/عناصر ناقصة | 3 | صور مفقودة أو نصوص نائبة |
| بدون عنوان (H1 القالب) | 0 | |
| أكثر من H1 داخل المحتوى | 0 | |
| H2 < 3 | 0 | |
| مستندات بعلامة واحدة على الأقل | 1727 | الغالبية بسبب القالب المشترك |
| بدون ملاحظات في الفحوصات الآلية | 41 | |

## جدول النتائج (أولوية + عيّنة)

الأعمدة: عنوان / رابط / كلمات / فئة المشكلة / ملاحظات. القائمة الكاملة في `findings-master.csv`.

| العنوان | الرابط | كلمات | فئة المشكلة | ملاحظات محددة |
| --- | --- | --- | --- | --- |
| المدن | https://www.rukn-eltatawer.com/sa/cities/ | 214 | thin_content | صفحة أدوات/فهرس (214 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| الأسعار | https://www.rukn-eltatawer.com/sa/pricing/ | 324 | thin_content | صفحة أدوات/فهرس (324 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| اتصل بنا | https://www.rukn-eltatawer.com/sa/contact-us/ | 899 | thin_content | صفحة أدوات/فهرس (899 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| خريطة الموقع | https://www.rukn-eltatawer.com/sa/sitemap/ | 935 | thin_content | صفحة أدوات/فهرس (935 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| المدونة | https://www.rukn-eltatawer.com/sa/blog/ | 979 | thin_content | صفحة أدوات/فهرس (979 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| شركة شحن سيارات بجدة | https://www.rukn-eltatawer.com/sa/car-shipping-jeddah/ | 1097 | intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار |
| شركة شحن سيارات بالدمام | https://www.rukn-eltatawer.com/sa/car-shipping-dammam/ | 1723 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالدمام | https://www.rukn-eltatawer.com/sa/domestic-shipping-dammam/ | 1737 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالدمام | https://www.rukn-eltatawer.com/sa/furniture-shipping-dammam/ | 1734 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالدمام | https://www.rukn-eltatawer.com/sa/duct-cleaning-dammam/ | 1857 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن سيارات بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/car-shipping-medina/ | 1811 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/domestic-shipping-medina/ | 1814 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/furniture-shipping-medina/ | 1828 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/duct-cleaning-medina/ | 1940 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن سيارات بمكة المكرمة | https://www.rukn-eltatawer.com/sa/car-shipping-mecca/ | 1777 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بمكة المكرمة | https://www.rukn-eltatawer.com/sa/domestic-shipping-mecca/ | 1794 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بمكة المكرمة | https://www.rukn-eltatawer.com/sa/duct-cleaning-mecca/ | 1938 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن داخلي داخل بجدة | https://www.rukn-eltatawer.com/sa/domestic-shipping-jeddah/ | 1713 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن سيارات بأبها | https://www.rukn-eltatawer.com/sa/car-shipping-abha/ | 1719 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بأبها | https://www.rukn-eltatawer.com/sa/domestic-shipping-abha/ | 1702 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بأبها | https://www.rukn-eltatawer.com/sa/furniture-shipping-abha/ | 1732 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن سيارات بالطائف | https://www.rukn-eltatawer.com/sa/car-shipping-taif/ | 1705 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالطائف | https://www.rukn-eltatawer.com/sa/domestic-shipping-taif/ | 1740 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالطائف | https://www.rukn-eltatawer.com/sa/furniture-shipping-taif/ | 1710 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالطائف | https://www.rukn-eltatawer.com/sa/duct-cleaning-taif/ | 1893 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن أثاث بجدة | https://www.rukn-eltatawer.com/sa/furniture-shipping-jeddah/ | 1741 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بجدة | https://www.rukn-eltatawer.com/sa/duct-cleaning-jeddah/ | 1854 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن سيارات بالخبر | https://www.rukn-eltatawer.com/sa/car-shipping-khobar/ | 1724 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالخبر | https://www.rukn-eltatawer.com/sa/domestic-shipping-khobar/ | 1706 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالخبر | https://www.rukn-eltatawer.com/sa/furniture-shipping-khobar/ | 1714 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالخبر | https://www.rukn-eltatawer.com/sa/duct-cleaning-khobar/ | 1840 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن سيارات بالرياض | https://www.rukn-eltatawer.com/sa/car-shipping-riyadh/ | 1723 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالرياض | https://www.rukn-eltatawer.com/sa/domestic-shipping-riyadh/ | 1752 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالرياض | https://www.rukn-eltatawer.com/sa/furniture-shipping-riyadh/ | 1735 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالرياض | https://www.rukn-eltatawer.com/sa/duct-cleaning-riyadh/ | 1875 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بأبها | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-abha/ | 1802 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالطائف | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-taif/ | 1807 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالخبر | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-khobar/ | 1798 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالدمام | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-dammam/ | 1789 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-medina/ | 1912 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بمكة المكرمة | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-mecca/ | 1860 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بجدة | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-jeddah/ | 1789 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالرياض | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-riyadh/ | 1819 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| تنظيف فلل بالباحة / خدمات احترافية من ركن التطور 2026 | https://www.rukn-eltatawer.com/sa/villa-cleaning-al-baha/ | 2236 | errors_missing | لا صور داخل المحتوى |
| كشف تسربات المياه بالخفجي | https://www.rukn-eltatawer.com/sa/water-leak-detection-khafji/ | 8252 | errors_missing | لا صور داخل المحتوى |
| كشف تسربات المياه في مكة | https://www.rukn-eltatawer.com/sa/water-leak-detection-makkah-center/ | 2081 | errors_missing | لا صور داخل المحتوى |
| شركة دهان شقق بالدمام | https://www.rukn-eltatawer.com/sa/apartment-painting-dammam/ | 1743 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |

## 1) محتوى ضعيف (Thin Content)

حدّ 1000 كلمة يُطبَّق على مقالات الخدمات. الصفحات الهيكلية مدرجة للشفافية وليست أولوية إعادة كتابة.

| العنوان | الرابط | كلمات | فئة المشكلة | ملاحظات محددة |
| --- | --- | --- | --- | --- |
| المدن | https://www.rukn-eltatawer.com/sa/cities/ | 214 | thin_content | صفحة أدوات/فهرس (214 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| الأسعار | https://www.rukn-eltatawer.com/sa/pricing/ | 324 | thin_content | صفحة أدوات/فهرس (324 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| اتصل بنا | https://www.rukn-eltatawer.com/sa/contact-us/ | 899 | thin_content | صفحة أدوات/فهرس (899 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| خريطة الموقع | https://www.rukn-eltatawer.com/sa/sitemap/ | 935 | thin_content | صفحة أدوات/فهرس (935 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |
| المدونة | https://www.rukn-eltatawer.com/sa/blog/ | 979 | thin_content | صفحة أدوات/فهرس (979 كلمة) — الحد 1000 موجّه لمقالات الخدمات لا للصفحات الهيكلية |

## 2) إفراط القوالب (Template / Boilerplate)

**1718 مقالاً** تشترك في عبارات جاهزة (انتقال/موسم ذروة، أسئلة الشقق والفلل، «لا نضع رقماً ثابتاً»، توقيع فريق المحتوى). هذا ضعف قيمة فريدة وليس نقص كلمات.

### عيّنة مقالات القالب

| العنوان | الرابط | كلمات | فئة المشكلة | ملاحظات محددة |
| --- | --- | --- | --- | --- |
| شركة دهان شقق بالدمام | https://www.rukn-eltatawer.com/sa/apartment-painting-dammam/ | 1743 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة عزل ودهان أسطح بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/roof-insulation-painting-medina/ | 1895 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة تركيب وصيانة محطات تحلية المياه بمكة المكرمة | https://www.rukn-eltatawer.com/sa/ro-plants-mecca/ | 1997 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| حداد أبواب ونوافذ بالدمام | https://www.rukn-eltatawer.com/sa/blacksmith-doors-windows-dammam/ | 1741 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| نجار أثاث بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/carpenter-medina/ | 1793 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| فني جبس بورد بالطائف | https://www.rukn-eltatawer.com/sa/gypsum-tech-taif/ | 1740 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| فني تركيب دش بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/sat-dish-tech-medina/ | 1806 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| فني تركيب أقمار صناعية بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/satellite-tech-medina/ | 1852 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| فني أنظمة صوت منزلية بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/home-audio-tech-medina/ | 1847 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| عامل دهانات بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/painter-medina/ | 1851 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة نقل وتركيب مكيفات بالدمام | https://www.rukn-eltatawer.com/sa/ac-relocation-installation-dammam/ | 1811 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة نقل بيانو بالدمام | https://www.rukn-eltatawer.com/sa/piano-moving-dammam/ | 1713 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة مكافحة بق الفراش بالدمام | https://www.rukn-eltatawer.com/sa/bed-bug-control-dammam/ | 2108 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة مكافحة الوزغ (البرص) بالدمام | https://www.rukn-eltatawer.com/sa/lizard-control-dammam/ | 1822 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة مكافحة العقارب بالدمام | https://www.rukn-eltatawer.com/sa/scorpion-control-dammam/ | 1728 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة مكافحة الطيور بالدمام | https://www.rukn-eltatawer.com/sa/bird-control-dammam/ | 1709 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة مكافحة الحشرات الطائرة بالدمام | https://www.rukn-eltatawer.com/sa/flying-pest-control-dammam/ | 1775 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة مكافحة الحشرات الزاحفة بالدمام | https://www.rukn-eltatawer.com/sa/crawling-pest-control-dammam/ | 1820 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة مكافحة البعوض والذباب بالدمام | https://www.rukn-eltatawer.com/sa/mosquito-fly-control-dammam/ | 1777 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |
| شركة مكافحة البراغيث بالدمام | https://www.rukn-eltatawer.com/sa/flea-control-dammam/ | 1717 | boilerplate_overuse | عبارات قالبية متكررة: تجهيزاً مرتباً قبل انتقال أو موسم ذروة / لا نضع رقماً ثابتاً لا يمثّل عقارك / نوضّح ما سيدخل في النطاق وما لن يدخل / حسب الجدولة اليومي… |

_… و1698 صفاً إضافياً في ملف CSV._

### عناقيد هيكل H2 المتطابق (بعد توحيد المدينة)

| حجم العنقود | عيّنة عنوان | رابط عيّنة | تسلسل H2 بعد توحيد المدينة | ملاحظات |
| --- | --- | --- | --- | --- |
| 77 | شركة مكافحة الأفاعي بالدمام | https://www.rukn-eltatawer.com/sa/snake-control-dammam/ | اطلب مكافحة الأفاعي في {CITY} / مكافحة الأفاعي داخل {CITY} / ما هي خدمة مكافحة الأفاعي؟ / مميزات مكافحة الأفاعي في {CITY} / هل مشكلتك تناسب مكافحة الأفاعي؟ /… | 77 مقالاً تشترك في تسلسل العناوين نفسه بعد توحيد اسم المدينة |
| 71 | شركة عزل ودهان أسطح بالدمام | https://www.rukn-eltatawer.com/sa/roof-insulation-painting-dammam/ | اطلب عزل ودهان أسطح في {CITY} / عزل ودهان أسطح داخل {CITY} / ما هي خدمة عزل ودهان أسطح؟ / مميزات عزل ودهان أسطح في {CITY} / هل مشكلتك تناسب عزل ودهان أسطح؟ /… | 71 مقالاً تشترك في تسلسل العناوين نفسه بعد توحيد اسم المدينة |
| 14 | شركة تنظيف منازل بالرياض | https://www.rukn-eltatawer.com/sa/home-cleaning-riyadh/ | نطاق الوصول في {CITY} / علامات تستدعي الخدمة الآن في {CITY} / ما الذي يميز الطلب على تنظيف منازل داخل {CITY}؟ / كيف نعمل خطوة بخطوة؟ / تفاصيل عملية لأصحاب ال… | 14 مقالاً تشترك في تسلسل العناوين نفسه بعد توحيد اسم المدينة |
| 12 | شركة تنظيف شقق بالرياض | https://www.rukn-eltatawer.com/sa/apartment-cleaning-riyadh/ | ما الذي يميز الطلب على تنظيف شقق داخل {CITY}؟ / نطاق الوصول في {CITY} / علامات تستدعي الخدمة الآن في {CITY} / كيف نعمل خطوة بخطوة؟ / تفاصيل عملية لأصحاب المن… | 12 مقالاً تشترك في تسلسل العناوين نفسه بعد توحيد اسم المدينة |
| 8 | شركة تنظيف فلل بالرياض | https://www.rukn-eltatawer.com/sa/villa-cleaning-riyadh/ | علامات تستدعي الخدمة الآن في {CITY} / ما الذي يميز الطلب على تنظيف فلل داخل {CITY}؟ / كيف نعمل خطوة بخطوة؟ / نطاق الوصول في {CITY} / تفاصيل عملية لأصحاب المن… | 8 مقالاً تشترك في تسلسل العناوين نفسه بعد توحيد اسم المدينة |

## 3) محتوى مكرر/متشابه (Duplicate / Cannibalization)

أزواج داخل نفس المدينة (تعارض كلمات): **129**. نسخ المدن (نفس المقال باسم مدينة أخرى): **6548**.

### أكبر المجموعات

| الحجم | عناوين | ملاحظات |
| --- | --- | --- |
| 68 | شركة كشف تسربات المياه بأبها / شركة كشف تسربات المياه بالطائف / شركة كشف تسربات المياه بالخبر / شركة كشف تسربات المياه بالدمام / شركة كشف تسربات المياه بالمد… | مجموعة مقالات شبه متطابقة في الصياغة |
| 33 | شركة تنظيف منازل بالرياض / شركة تنظيف فلل بالرياض / شركة تنظيف شقق بالرياض / شركة تركيب عشب صناعي بالرياض / شركة تركيب عشب صناعي بمكة المكرمة / شركة تركيب عش… | مجموعة مقالات شبه متطابقة في الصياغة |
| 24 | فني جبس بورد بالطائف / شركة ديكورات جبس بورد بأبها / شركة تركيب جبس بورد بأبها / شركة ديكورات جبس بورد بالطائف / شركة تركيب جبس بورد بالطائف / فني جبس بورد ب… | مجموعة مقالات شبه متطابقة في الصياغة |
| 16 | شركة تركيب شبكات ري حديثة بالدمام / شركة تركيب شبكات ري أوتوماتيكية بالدمام / شركة تركيب شبكات ري حديثة بالمدينة المنورة / شركة تركيب شبكات ري أوتوماتيكية با… | مجموعة مقالات شبه متطابقة في الصياغة |
| 16 | شركة سباك منازل بأبها / سباك منازل بأبها / سباك منازل بالطائف / شركة سباك منازل بالطائف / سباك منازل بالخبر / شركة سباك منازل بالخبر / سباك منازل بالدمام / ش… | مجموعة مقالات شبه متطابقة في الصياغة |
| 16 | كهربائي منازل بأبها / كهربائي منازل بالطائف / شركة كهربائي منازل بأبها / شركة كهربائي منازل بالطائف / كهربائي منازل بالخبر / كهربائي منازل بالدمام / شركة كهر… | مجموعة مقالات شبه متطابقة في الصياغة |
| 16 | شركة صيانة لوحات كهرباء بأبها / شركة صيانة كهرباء بأبها / شركة صيانة لوحات كهرباء بالطائف / شركة صيانة كهرباء بالطائف / شركة صيانة لوحات كهرباء بالخبر / شركة… | مجموعة مقالات شبه متطابقة في الصياغة |
| 15 | شركة عزل ودهان أسطح بالمدينة المنورة / شركة عزل ودهان أسطح بالدمام / شركة عزل ودهان أسطح بمكة المكرمة / شركة عزل ودهان أسطح بجدة / شركة عزل ودهان أسطح بأبها … | مجموعة مقالات شبه متطابقة في الصياغة |
| 9 | شركة تنظيف كنب بأبها / شركة تنظيف كنب بالطائف / شركة تنظيف كنب بالخبر / شركة تنظيف كنب بالدمام / شركة تنظيف كنب بالمدينة المنورة / شركة تنظيف كنب بمكة المكرم… | مجموعة مقالات شبه متطابقة في الصياغة |
| 9 | شركة تنظيف فلل بأبها / شركة تنظيف فلل بالطائف / شركة تنظيف فلل بالخبر / شركة تنظيف فلل بالدمام / شركة تنظيف فلل بالمدينة المنورة / شركة تنظيف فلل بمكة المكرم… | مجموعة مقالات شبه متطابقة في الصياغة |
| 9 | شركة تنظيف سجاد بأبها / شركة تنظيف سجاد بالطائف / شركة تنظيف سجاد بالخبر / شركة تنظيف سجاد بالدمام / شركة تنظيف سجاد بالمدينة المنورة / شركة تنظيف سجاد بمكة … | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | شركة دهان شقق بالدمام / شركة دهان شقق بالمدينة المنورة / شركة دهان شقق بمكة المكرمة / شركة دهان شقق بأبها / شركة دهان شقق بالطائف / شركة دهان شقق بجدة / شركة… | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | شركة تركيب وصيانة محطات تحلية المياه بمكة المكرمة / شركة تركيب وصيانة محطات تحلية المياه بالدمام / شركة تركيب وصيانة محطات تحلية المياه بالمدينة المنورة / شر… | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | حداد أبواب ونوافذ بالدمام / حداد أبواب ونوافذ بالمدينة المنورة / حداد أبواب ونوافذ بمكة المكرمة / حداد أبواب ونوافذ بجدة / حداد أبواب ونوافذ بأبها / حداد أبو… | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | نجار أثاث بالمدينة المنورة / نجار أثاث بمكة المكرمة / نجار أثاث بجدة / نجار أثاث بأبها / نجار أثاث بالطائف / نجار أثاث بالخبر / نجار أثاث بالدمام / نجار أثاث… | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | فني تركيب دش بالمدينة المنورة / فني تركيب دش بمكة المكرمة / فني تركيب دش بجدة / فني تركيب دش بأبها / فني تركيب دش بالطائف / فني تركيب دش بالخبر / فني تركيب د… | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | فني تركيب أقمار صناعية بالمدينة المنورة / فني تركيب أقمار صناعية بمكة المكرمة / فني تركيب أقمار صناعية بجدة / فني تركيب أقمار صناعية بأبها / فني تركيب أقمار … | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | فني أنظمة صوت منزلية بالمدينة المنورة / فني أنظمة صوت منزلية بمكة المكرمة / فني أنظمة صوت منزلية بجدة / فني أنظمة صوت منزلية بأبها / فني أنظمة صوت منزلية بال… | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | عامل دهانات بالمدينة المنورة / عامل دهانات بمكة المكرمة / عامل دهانات بجدة / عامل دهانات بأبها / عامل دهانات بالطائف / عامل دهانات بالخبر / عامل دهانات بالدم… | مجموعة مقالات شبه متطابقة في الصياغة |
| 8 | شركة نقل وتركيب مكيفات بالدمام / شركة نقل وتركيب مكيفات بالمدينة المنورة / شركة نقل وتركيب مكيفات بمكة المكرمة / شركة نقل وتركيب مكيفات بجدة / شركة نقل وتركي… | مجموعة مقالات شبه متطابقة في الصياغة |

_… و180 صفاً إضافياً في ملف CSV._

### أعلى تعارض داخل نفس المدينة

| عنوان أ | رابط أ | عنوان ب | رابط ب | cosine | ملاحظات |
| --- | --- | --- | --- | --- | --- |
| كشف تسربات المياه في جنوب جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-south-jeddah/ | كشف تسربات المياه في شرق جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-jeddah/ | 0.9978 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في جنوب جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-south-jeddah/ | كشف تسربات المياه في شمال جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-jeddah/ | 0.9974 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كهربائي منازل بجدة | https://www.rukn-eltatawer.com/sa/home-electrician-jeddah/ | شركة كهربائي منازل بجدة | https://www.rukn-eltatawer.com/sa/home-electrician-elec-jeddah/ | 0.9972 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في شرق الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-riyadh/ | كشف تسربات المياه في شمال الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-riyadh/ | 0.997 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| سباك منازل بمكة المكرمة | https://www.rukn-eltatawer.com/sa/home-plumber-mecca/ | شركة سباك منازل بمكة المكرمة | https://www.rukn-eltatawer.com/sa/home-plumber-elec-mecca/ | 0.9955 | تعارض كلمات مفتاحية داخل نفس المدينة (مكة المكرمة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في شرق جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-jeddah/ | كشف تسربات المياه في شمال جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-jeddah/ | 0.9955 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| سباك منازل بجدة | https://www.rukn-eltatawer.com/sa/home-plumber-jeddah/ | شركة سباك منازل بجدة | https://www.rukn-eltatawer.com/sa/home-plumber-elec-jeddah/ | 0.9952 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في جنوب جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-south-jeddah/ | كشف تسربات المياه في جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-jeddah-center/ | 0.9952 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في شرق الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-riyadh/ | كشف تسربات المياه في وسط الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh-center/ | 0.9952 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| سباك منازل بالطائف | https://www.rukn-eltatawer.com/sa/home-plumber-taif/ | شركة سباك منازل بالطائف | https://www.rukn-eltatawer.com/sa/home-plumber-elec-taif/ | 0.9949 | تعارض كلمات مفتاحية داخل نفس المدينة (الطائف) — صفحتان تتصارعان على نفس النية |
| شركة كشف تسربات المياه بجدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-jeddah/ | كشف تسربات المياه في شمال جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-jeddah/ | 0.9944 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في شرق جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-jeddah/ | كشف تسربات المياه في جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-jeddah-center/ | 0.9942 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كهربائي منازل بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/home-electrician-medina/ | شركة كهربائي منازل بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/home-electrician-elec-medina/ | 0.9938 | تعارض كلمات مفتاحية داخل نفس المدينة (المدينة المنورة) — صفحتان تتصارعان على نفس النية |
| سباك منازل بالرياض | https://www.rukn-eltatawer.com/sa/home-plumber-riyadh/ | شركة سباك منازل بالرياض | https://www.rukn-eltatawer.com/sa/home-plumber-elec-riyadh/ | 0.9936 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في جنوب الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-south-riyadh/ | كشف تسربات المياه في شرق الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-riyadh/ | 0.9935 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| شركة سباك منازل بأبها | https://www.rukn-eltatawer.com/sa/home-plumber-elec-abha/ | سباك منازل بأبها | https://www.rukn-eltatawer.com/sa/home-plumber-abha/ | 0.9933 | تعارض كلمات مفتاحية داخل نفس المدينة (أبها) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في غرب الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-west-riyadh/ | كشف تسربات المياه في شمال الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-riyadh/ | 0.9933 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في شمال الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-riyadh/ | كشف تسربات المياه في وسط الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh-center/ | 0.9931 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في غرب الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-west-riyadh/ | كشف تسربات المياه في شرق الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-riyadh/ | 0.9928 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| كهربائي منازل بمكة المكرمة | https://www.rukn-eltatawer.com/sa/home-electrician-mecca/ | شركة كهربائي منازل بمكة المكرمة | https://www.rukn-eltatawer.com/sa/home-electrician-elec-mecca/ | 0.9927 | تعارض كلمات مفتاحية داخل نفس المدينة (مكة المكرمة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في شمال جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-jeddah/ | كشف تسربات المياه في جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-jeddah-center/ | 0.9927 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كهربائي منازل بالطائف | https://www.rukn-eltatawer.com/sa/home-electrician-taif/ | شركة كهربائي منازل بالطائف | https://www.rukn-eltatawer.com/sa/home-electrician-elec-taif/ | 0.9924 | تعارض كلمات مفتاحية داخل نفس المدينة (الطائف) — صفحتان تتصارعان على نفس النية |
| شركة كشف تسربات المياه بجدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-jeddah/ | كشف تسربات المياه في جنوب جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-south-jeddah/ | 0.9922 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في جنوب الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-south-riyadh/ | كشف تسربات المياه في وسط الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh-center/ | 0.9921 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في غرب الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-west-riyadh/ | كشف تسربات المياه في وسط الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-riyadh-center/ | 0.9921 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |

_… و104 صفاً إضافياً في ملف CSV._

### أعلى الأزواج تشابهاً عموماً

| عنوان أ | رابط أ | عنوان ب | رابط ب | cosine | ملاحظات |
| --- | --- | --- | --- | --- | --- |
| كشف تسربات المياه في رابغ / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-rabigh/ | كشف تسربات المياه في حفر الباطن / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-hafar-al-batin/ | 1.0 | نسخة مدينة شبه مطابقة (رابغ ↔ حفر الباطن) بعد توحيد اسم المدينة |
| كشف تسربات المياه في الخرج | https://www.rukn-eltatawer.com/sa/water-leak-detection-al-kharj/ | كشف تسربات المياه في سكاكا | https://www.rukn-eltatawer.com/sa/water-leak-detection-sakakah/ | 0.9992 | نسخة مدينة شبه مطابقة (الخرج ↔ سكاكا) بعد توحيد اسم المدينة |
| كشف تسربات المياه في أبو عريش / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-abu-arish/ | كشف تسربات المياه في الخرج | https://www.rukn-eltatawer.com/sa/water-leak-detection-al-kharj/ | 0.9984 | نسخة مدينة شبه مطابقة (أبو عريش ↔ الخرج) بعد توحيد اسم المدينة |
| كشف تسربات المياه في أبو عريش / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-abu-arish/ | كشف تسربات المياه في سكاكا | https://www.rukn-eltatawer.com/sa/water-leak-detection-sakakah/ | 0.9978 | نسخة مدينة شبه مطابقة (أبو عريش ↔ سكاكا) بعد توحيد اسم المدينة |
| كشف تسربات المياه في جنوب جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-south-jeddah/ | كشف تسربات المياه في شرق جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-jeddah/ | 0.9978 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في رابغ / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-rabigh/ | كشف تسربات المياه في الظهران | https://www.rukn-eltatawer.com/sa/water-leak-detection-dhahran/ | 0.9976 | نسخة مدينة شبه مطابقة (رابغ ↔ الظهران) بعد توحيد اسم المدينة |
| كشف تسربات المياه في حفر الباطن / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-hafar-al-batin/ | كشف تسربات المياه في الظهران | https://www.rukn-eltatawer.com/sa/water-leak-detection-dhahran/ | 0.9976 | نسخة مدينة شبه مطابقة (حفر الباطن ↔ الظهران) بعد توحيد اسم المدينة |
| كشف تسربات المياه في جنوب جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-south-jeddah/ | كشف تسربات المياه في شمال جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-jeddah/ | 0.9974 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كهربائي منازل بجدة | https://www.rukn-eltatawer.com/sa/home-electrician-jeddah/ | شركة كهربائي منازل بجدة | https://www.rukn-eltatawer.com/sa/home-electrician-elec-jeddah/ | 0.9972 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في رابغ / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-rabigh/ | كشف تسربات المياه في عرعر | https://www.rukn-eltatawer.com/sa/water-leak-detection-arar/ | 0.9972 | نسخة مدينة شبه مطابقة (رابغ ↔ عرعر) بعد توحيد اسم المدينة |
| كشف تسربات المياه في حفر الباطن / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-hafar-al-batin/ | كشف تسربات المياه في عرعر | https://www.rukn-eltatawer.com/sa/water-leak-detection-arar/ | 0.9971 | نسخة مدينة شبه مطابقة (حفر الباطن ↔ عرعر) بعد توحيد اسم المدينة |
| كشف تسربات المياه في شرق الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-riyadh/ | كشف تسربات المياه في شمال الرياض | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-riyadh/ | 0.997 | تعارض كلمات مفتاحية داخل نفس المدينة (الرياض) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في عرعر | https://www.rukn-eltatawer.com/sa/water-leak-detection-arar/ | كشف تسربات المياه في سكاكا | https://www.rukn-eltatawer.com/sa/water-leak-detection-sakakah/ | 0.9962 | نسخة مدينة شبه مطابقة (عرعر ↔ سكاكا) بعد توحيد اسم المدينة |
| كشف تسربات المياه في أبو عريش / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-abu-arish/ | كشف تسربات المياه في عرعر | https://www.rukn-eltatawer.com/sa/water-leak-detection-arar/ | 0.9961 | نسخة مدينة شبه مطابقة (أبو عريش ↔ عرعر) بعد توحيد اسم المدينة |
| سباك منازل بمكة المكرمة | https://www.rukn-eltatawer.com/sa/home-plumber-mecca/ | شركة سباك منازل بمكة المكرمة | https://www.rukn-eltatawer.com/sa/home-plumber-elec-mecca/ | 0.9955 | تعارض كلمات مفتاحية داخل نفس المدينة (مكة المكرمة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في شرق جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-east-jeddah/ | كشف تسربات المياه في شمال جدة | https://www.rukn-eltatawer.com/sa/water-leak-detection-north-jeddah/ | 0.9955 | تعارض كلمات مفتاحية داخل نفس المدينة (جدة) — صفحتان تتصارعان على نفس النية |
| كشف تسربات المياه في رابغ / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-rabigh/ | كشف تسربات المياه في أبو عريش / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-abu-arish/ | 0.9954 | نسخة مدينة شبه مطابقة (رابغ ↔ أبو عريش) بعد توحيد اسم المدينة |
| كشف تسربات المياه في رابغ / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-rabigh/ | كشف تسربات المياه في سكاكا | https://www.rukn-eltatawer.com/sa/water-leak-detection-sakakah/ | 0.9954 | نسخة مدينة شبه مطابقة (رابغ ↔ سكاكا) بعد توحيد اسم المدينة |
| كشف تسربات المياه في حفر الباطن / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-hafar-al-batin/ | كشف تسربات المياه في أبو عريش / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-abu-arish/ | 0.9954 | نسخة مدينة شبه مطابقة (حفر الباطن ↔ أبو عريش) بعد توحيد اسم المدينة |
| كشف تسربات المياه في حفر الباطن / شركة ركن التطور | https://www.rukn-eltatawer.com/sa/water-leak-detection-hafar-al-batin/ | كشف تسربات المياه في سكاكا | https://www.rukn-eltatawer.com/sa/water-leak-detection-sakakah/ | 0.9954 | نسخة مدينة شبه مطابقة (حفر الباطن ↔ سكاكا) بعد توحيد اسم المدينة |

_… و6976 صفاً إضافياً في ملف CSV._

## 4) عدم تطابق نية البحث (Intent Mismatch)

هنا فقط التناقض الحقيقي بين العنوان والجسم (مثلاً شحن سيارات بأسئلة الشقق، أو تكييف بفقرات رخام/خشب). عبارة موسم الذروة صُنّفت تحت القوالب وليست نية بحث مستقلة.

| العنوان | الرابط | كلمات | فئة المشكلة | ملاحظات محددة |
| --- | --- | --- | --- | --- |
| شركة شحن سيارات بجدة | https://www.rukn-eltatawer.com/sa/car-shipping-jeddah/ | 1097 | intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار |
| شركة شحن سيارات بالدمام | https://www.rukn-eltatawer.com/sa/car-shipping-dammam/ | 1723 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالدمام | https://www.rukn-eltatawer.com/sa/domestic-shipping-dammam/ | 1737 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالدمام | https://www.rukn-eltatawer.com/sa/furniture-shipping-dammam/ | 1734 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالدمام | https://www.rukn-eltatawer.com/sa/duct-cleaning-dammam/ | 1857 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن سيارات بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/car-shipping-medina/ | 1811 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/domestic-shipping-medina/ | 1814 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/furniture-shipping-medina/ | 1828 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/duct-cleaning-medina/ | 1940 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن سيارات بمكة المكرمة | https://www.rukn-eltatawer.com/sa/car-shipping-mecca/ | 1777 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بمكة المكرمة | https://www.rukn-eltatawer.com/sa/domestic-shipping-mecca/ | 1794 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بمكة المكرمة | https://www.rukn-eltatawer.com/sa/duct-cleaning-mecca/ | 1938 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن داخلي داخل بجدة | https://www.rukn-eltatawer.com/sa/domestic-shipping-jeddah/ | 1713 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن سيارات بأبها | https://www.rukn-eltatawer.com/sa/car-shipping-abha/ | 1719 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بأبها | https://www.rukn-eltatawer.com/sa/domestic-shipping-abha/ | 1702 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بأبها | https://www.rukn-eltatawer.com/sa/furniture-shipping-abha/ | 1732 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن سيارات بالطائف | https://www.rukn-eltatawer.com/sa/car-shipping-taif/ | 1705 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالطائف | https://www.rukn-eltatawer.com/sa/domestic-shipping-taif/ | 1740 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالطائف | https://www.rukn-eltatawer.com/sa/furniture-shipping-taif/ | 1710 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالطائف | https://www.rukn-eltatawer.com/sa/duct-cleaning-taif/ | 1893 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن أثاث بجدة | https://www.rukn-eltatawer.com/sa/furniture-shipping-jeddah/ | 1741 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بجدة | https://www.rukn-eltatawer.com/sa/duct-cleaning-jeddah/ | 1854 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن سيارات بالخبر | https://www.rukn-eltatawer.com/sa/car-shipping-khobar/ | 1724 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالخبر | https://www.rukn-eltatawer.com/sa/domestic-shipping-khobar/ | 1706 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالخبر | https://www.rukn-eltatawer.com/sa/furniture-shipping-khobar/ | 1714 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالخبر | https://www.rukn-eltatawer.com/sa/duct-cleaning-khobar/ | 1840 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة شحن سيارات بالرياض | https://www.rukn-eltatawer.com/sa/car-shipping-riyadh/ | 1723 | boilerplate_overuse/intent_mismatch | عنوان شحن سيارات بينما النص يعامل الخدمة كخدمة منزل/عقار // شحن سيارات يستخدم صياغة انتقال المنازل |
| شركة شحن داخلي داخل بالرياض | https://www.rukn-eltatawer.com/sa/domestic-shipping-riyadh/ | 1752 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة شحن أثاث بالرياض | https://www.rukn-eltatawer.com/sa/furniture-shipping-riyadh/ | 1735 | boilerplate_overuse/intent_mismatch | عنوان شحن بينما الأسئلة تفترض شقق وفلل |
| شركة تنظيف وصيانة دكتات المكيفات بالرياض | https://www.rukn-eltatawer.com/sa/duct-cleaning-riyadh/ | 1875 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بأبها | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-abha/ | 1802 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالطائف | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-taif/ | 1807 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالخبر | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-khobar/ | 1798 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالدمام | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-dammam/ | 1789 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالمدينة المنورة | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-medina/ | 1912 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بمكة المكرمة | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-mecca/ | 1860 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بجدة | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-jeddah/ | 1789 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |
| شركة غسيل وتنظيف مكيفات بالرياض | https://www.rukn-eltatawer.com/sa/ac-cleaning-washing-riyadh/ | 1819 | boilerplate_overuse/intent_mismatch | عنوان عن تكييف بينما النص/الأسئلة تتحدث عن تنظيف منازل أو رخام وخشب |

## 5) أخطاء وعناصر مفقودة

H1 القالب موجود من عنوان المقال. لا توجد نصوص `lorem ipsum` ولا أرقام `966000000000` داخل المحتوى المفحوص. الصفوف أدناه: صور داخل الجسم أو عناصر بنيوية أخرى.

| العنوان | الرابط | كلمات | H1 داخل الجسم | H2 | الفئة | ملاحظات |
| --- | --- | --- | --- | --- | --- | --- |
| تنظيف فلل بالباحة / خدمات احترافية من ركن التطور 2026 | https://www.rukn-eltatawer.com/sa/villa-cleaning-al-baha/ | 2236 | 0 | 14 | errors_missing | لا صور داخل المحتوى |
| كشف تسربات المياه بالخفجي | https://www.rukn-eltatawer.com/sa/water-leak-detection-khafji/ | 8252 | 0 | 28 | errors_missing | لا صور داخل المحتوى |
| كشف تسربات المياه في مكة | https://www.rukn-eltatawer.com/sa/water-leak-detection-makkah-center/ | 2081 | 0 | 5 | errors_missing | لا صور داخل المحتوى |

## أولويات المعالجة

1. حذف/استبدال فقرة «تجهيزاً مرتباً قبل انتقال أو موسم ذروة» من كل خدمة ليست نقل عفش.
2. إعادة كتابة أسئلة «هل الخدمة للشقق والفلل؟» لتطابق نوع الخدمة (سيارات، شحن، مكافحة…).
3. دمج أو تمييز أزواج cannibalization داخل المدينة (`سباك` مقابل `شركة سباك`، أحياء جدة/الرياض لكشف التسربات).
4. إصلاح صفحات التكييف التي تتحدث عن رخام/خشب وصفحات شحن السيارات/الأثاث التي تفترض عقاراً.
5. تنويع هيكل H2 لكل عائلة خدمة بدل الهيكل الثابت «اطلب… / ما هي خدمة… / مميزات…».
6. الصفحات الهيكلية (مدن، أسعار، اتصال، خريطة، مدونة) لا تحتاج 1000 كلمة.

## ملفات CSV

- `thin-content.csv`
- `boilerplate-overuse.csv`
- `template-clusters.csv`
- `similar-pairs.csv` / `similar-clusters.csv`
- `intent-mismatch.csv`
- `errors-missing.csv`
- `findings-master.csv` (كل المستندات المعلّمة)
- `all-docs.csv` (الجرد الكامل بما فيه السليم آلياً)
- `summary.json`

إعادة التشغيل:

```bash
WP_USER=cursor WP_APP_PASSWORD='xxxx' python3 audit/seo_content_audit.py \
  --base https://www.rukn-eltatawer.com/sa --out-dir audit/seo-run
```
الكاش الافتراضي: `/tmp/rukn-seo-audit`. لا تضع كلمة مرور التطبيقات في git.
