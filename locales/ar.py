AR_TEXTS = {
    "welcome": """🎓 <b>مرحباً بك في أكاديمية الاختبارات الآلية!</b>

🤖 أنا بوت ذكي لإنشاء وإدارة ونشر الاختبارات في تيليجرام.

<b>ما يمكنني فعله:</b>
📝 إنشاء اختبارات متعددة الخيارات وصح/خطأ
📤 نشر الاختبارات في القنوات والمجموعات
📅 جدولة النشر التلقائي
🤖 توليد أسئلة بالذكاء الاصطناعي
📊 تحليلات متقدمة للأداء

اختر من القائمة أدناه للبدء! 👇""",
    "main_menu": "📋 <b>القائمة الرئيسية</b>\n\nاختر ما تريد فعله:",
    "quiz_menu": "📝 <b>إدارة الاختبارات</b>\n\nاختر الإجراء:",
    "create_quiz": "📝 إنشاء اختبار",
    "my_quizzes": "📋 اختباراتي",
    "publish": "📤 نشر اختبار",
    "schedule": "📅 جدولة",
    "channels": "📢 القنوات",
    "analytics": "📊 التحليلات",
    "settings": "⚙️ الإعدادات",
    "ai_tools": "🤖 أدوات الذكاء الاصطناعي",
    "support": "💬 الدعم",
    "admin_panel": "🔧 لوحة التحكم",
    "enter_quiz_title": "📝 <b>أدخل عنوان الاختبار:</b>",
    "enter_quiz_description": "📄 <b>أدخل وصف الاختبار</b> (أو اضغط تخطي):",
    "select_category": "📂 <b>اختر تصنيف الاختبار:</b>",
    "enter_question": """📝 <b>أدخل السؤال:</b>

أو أرسل الأمر بالصيغة التالية:
<code>السؤال</code>

يمكنك الضغط على "إنهاء" عند الانتهاء.""",
    "enter_options": """🔤 <b>أدخل الخيارات</b> (كل خيار في سطر جديد):

مثال:
خيار أ
خيار ب
خيار ج
خيار د""",
    "select_correct": "✅ <b>اختر الإجابة الصحيحة:</b>",
    "select_question_type": "📋 <b>اختر نوع السؤال:</b>",
    "question_added": "✅ تم إضافة السؤال بنجاح! ({count} أسئلة)\n\nأضف سؤالاً آخر أو اضغط إنهاء.",
    "quiz_created": "✅ <b>تم إنشاء الاختبار بنجاح!</b>\n\n📝 العنوان: {title}\n📊 عدد الأسئلة: {count}",
    "no_quizzes": "❌ لا توجد اختبارات بعد.\n\nاضغط على 'إنشاء اختبار' للبدء!",
    "quiz_details": """📝 <b>{title}</b>

📄 الوصف: {description}
📂 التصنيف: {category}
📊 عدد الأسئلة: {count}
👥 المشاركين: {participants}
📅 تاريخ الإنشاء: {created}""",
    "confirm_delete": "⚠️ هل أنت متأكد من حذف الاختبار '{title}'?",
    "quiz_deleted": "✅ تم حذف الاختبار بنجاح!",
    "select_quiz_to_publish": "📤 <b>اختر الاختبار للنشر:</b>",
    "select_channel": "📢 <b>اختر القناة/المجموعة:</b>",
    "no_channels": "❌ لا توجد قنوات مرتبطة.\n\nاستخدم /add_channel لإضافة قناة.",
    "publish_success": "✅ تم نشر الاختبار بنجاح في {channel}!",
    "publish_failed": "❌ فشل النشر: {error}",
    "schedule_set": "✅ تم جدولة النشر!\n\n📅 الموعد: {time}\n🔄 التكرار: {repeat}",
    "enter_schedule_time": "📅 <b>أدخل موعد النشر:</b>\n\nالصيغة: <code>YYYY-MM-DD HH:MM</code>\nمثال: <code>2024-03-20 14:00</code>",
    "select_repeat": "🔄 <b>اختر نوع التكرار:</b>",
    "channel_added": "✅ تم إضافة القناة '{title}' بنجاح!",
    "channel_removed": "✅ تم إزالة القناة بنجاح!",
    "bot_not_admin": "❌ البوت ليس مشرفاً في هذه القناة/المجموعة.\nأضف البوت كمشرف أولاً.",
    "force_subscribe": "⚠️ <b>يجب عليك الاشتراك في القنوات التالية أولاً:</b>",
    "check_subscription": "✅ تحقق من الاشتراك",
    "not_subscribed": "❌ لم تشترك في جميع القنوات المطلوبة بعد!",
    "language_changed": "✅ تم تغيير اللغة بنجاح!",
    "stats_user": """📊 <b>إحصائياتك:</b>

📝 عدد الاختبارات: {quizzes}
❓ عدد الأسئلة: {questions}
📢 عدد القنوات: {channels}
📅 عدد الجداول النشطة: {schedules}""",
    "broadcast_enter": "📨 <b>أدخل الرسالة التي تريد إرسالها لجميع المستخدمين:</b>",
    "broadcast_confirm": "📨 <b>تأكيد الإرسال الجماعي</b>\n\nالرسالة:\n{message}\n\nعدد المستخدمين: {count}",
    "broadcast_done": "✅ تم الإرسال!\n\n✅ نجح: {success}\n❌ فشل: {failed}",
    "support_enter": "💬 <b>أرسل رسالتك وسيتم إيصالها للإدارة:</b>",
    "support_sent": "✅ تم إرسال رسالتك بنجاح! سيتم الرد عليك قريباً.",
    "cancelled": "❌ تم الإلغاء.",
    "error_occurred": "❌ حدث خطأ! حاول مرة أخرى.",
    "loading": "⏳ جاري التحميل...",
    "finish": "✅ إنهاء",
    "skip": "⏭️ تخطي",
    "back": "🔙 رجوع",
    "cancel": "❌ إلغاء",
    "yes": "✅ نعم",
    "no": "❌ لا",
    "next": "⏭️ التالي",
    "previous": "⏮️ السابق",
    "confirm": "✅ تأكيد",
    "multiple_choice": "📝 اختيار من متعدد",
    "true_false": "✅❌ صح / خطأ",
    "none_repeat": "❌ بدون تكرار",
    "daily": "📅 يومي",
    "weekly": "📆 أسبوعي",
    "monthly": "🗓️ شهري",
    "quiz_result": """📊 <b>نتيجة الاختبار</b>

📝 {title}
✅ الإجابات الصحيحة: {correct}/{total}
📈 النسبة: {percentage}%

{grade}""",
    "excellent": "🏆 ممتاز!",
    "very_good": "🌟 جيد جداً!",
    "good": "👍 جيد",
    "fair": "📝 مقبول",
    "fail": "📚 يحتاج مراجعة",
    "queue_empty": "📭 قائمة الانتظار فارغة.",
    "queue_item": "📋 {position}. {quiz_title} → {channel_title} ({status})",
    "ai_generate_prompt": "🤖 <b>أدخل الموضوع لتوليد الأسئلة:</b>\n\nمثال: 'أسئلة عن الفيزياء للمرحلة الثانوية'",
    "ai_generating": "🤖 جاري توليد الأسئلة بالذكاء الاصطناعي...",
    "ai_limit_reached": "⚠️ لقد وصلت للحد الأقصى من طلبات الذكاء الاصطناعي اليوم ({limit} طلبات).",
    "calendar_view": "📅 <b>جدول النشر</b>\n\n{schedule}",
    "no_schedule": "📭 لا يوجد جدول نشر حالياً.",
    "export_success": "✅ تم تصدير الاختبارات بنجاح!",
    "import_prompt": "📥 <b>أرسل ملف JSON أو TXT للاستيراد:</b>",
    "import_success": "✅ تم استيراد {count} اختبار بنجاح!",
    "import_failed": "❌ فشل الاستيراد! تأكد من صيغة الملف.",
    "help_text": """📖 <b>دليل الاستخدام</b>

<b>الأوامر الأساسية:</b>
/start - بدء البوت
/help - المساعدة
/add_quiz - إضافة سؤال سريع
/my_quizzes - اختباراتي
/add_channel - إضافة قناة
/my_channels - قنواتي
/stats - إحصائياتي
/calendar - جدول النشر
/queue - قائمة الانتظار
/export - تصدير الاختبارات
/import - استيراد الاختبارات
/generate - توليد أسئلة بالذكاء الاصطناعي
/language - تغيير اللغة
/admin - لوحة التحكم (للمشرفين)

<b>إضافة سؤال سريع:</b>
<code>/add_quiz الإجابة; السؤال; خيار1; خيار2; خيار3; خيار4</code>

مثال:
<code>/add_quiz goes; She ____ to school; go; goes; going; goed</code>""",
}