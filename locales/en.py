EN_TEXTS = {
    "welcome": """🎓 <b>Welcome to AI Quiz Academy!</b>

🤖 I'm a smart bot for creating, managing, and publishing quizzes on Telegram.

<b>What I can do:</b>
📝 Create multiple choice & true/false quizzes
📤 Publish quizzes to channels and groups
📅 Schedule automatic publishing
🤖 Generate questions with AI
📊 Advanced performance analytics

Choose from the menu below to start! 👇""",
    "main_menu": "📋 <b>Main Menu</b>\n\nChoose what you want to do:",
    "quiz_menu": "📝 <b>Quiz Management</b>\n\nChoose an action:",
    "create_quiz": "📝 Create Quiz",
    "my_quizzes": "📋 My Quizzes",
    "publish": "📤 Publish Quiz",
    "schedule": "📅 Schedule",
    "channels": "📢 Channels",
    "analytics": "📊 Analytics",
    "settings": "⚙️ Settings",
    "ai_tools": "🤖 AI Tools",
    "support": "💬 Support",
    "admin_panel": "🔧 Admin Panel",
    "enter_quiz_title": "📝 <b>Enter quiz title:</b>",
    "enter_quiz_description": "📄 <b>Enter quiz description</b> (or press skip):",
    "select_category": "📂 <b>Select quiz category:</b>",
    "enter_question": """📝 <b>Enter the question:</b>

Press "Finish" when done.""",
    "enter_options": """🔤 <b>Enter options</b> (each on a new line):

Example:
Option A
Option B
Option C
Option D""",
    "select_correct": "✅ <b>Select the correct answer:</b>",
    "select_question_type": "📋 <b>Select question type:</b>",
    "question_added": "✅ Question added! ({count} questions)\n\nAdd another or press Finish.",
    "quiz_created": "✅ <b>Quiz created!</b>\n\n📝 Title: {title}\n📊 Questions: {count}",
    "no_quizzes": "❌ No quizzes yet.\n\nPress 'Create Quiz' to start!",
    "quiz_details": """📝 <b>{title}</b>

📄 Description: {description}
📂 Category: {category}
📊 Questions: {count}
👥 Participants: {participants}
📅 Created: {created}""",
    "confirm_delete": "⚠️ Are you sure you want to delete '{title}'?",
    "quiz_deleted": "✅ Quiz deleted!",
    "select_quiz_to_publish": "📤 <b>Select quiz to publish:</b>",
    "select_channel": "📢 <b>Select channel/group:</b>",
    "no_channels": "❌ No channels linked.\n\nUse /add_channel to add one.",
    "publish_success": "✅ Quiz published to {channel}!",
    "publish_failed": "❌ Publish failed: {error}",
    "schedule_set": "✅ Scheduled!\n\n📅 Time: {time}\n🔄 Repeat: {repeat}",
    "enter_schedule_time": "📅 <b>Enter schedule time:</b>\n\nFormat: <code>YYYY-MM-DD HH:MM</code>",
    "select_repeat": "🔄 <b>Select repeat type:</b>",
    "channel_added": "✅ Channel '{title}' added!",
    "channel_removed": "✅ Channel removed!",
    "bot_not_admin": "❌ Bot is not admin in this channel/group.",
    "force_subscribe": "⚠️ <b>Please subscribe to these channels first:</b>",
    "check_subscription": "✅ Check Subscription",
    "not_subscribed": "❌ You haven't subscribed to all required channels!",
    "language_changed": "✅ Language changed!",
    "stats_user": """📊 <b>Your Statistics:</b>

📝 Quizzes: {quizzes}
❓ Questions: {questions}
📢 Channels: {channels}
📅 Active Schedules: {schedules}""",
    "broadcast_enter": "📨 <b>Enter the message to broadcast:</b>",
    "broadcast_confirm": "📨 <b>Confirm Broadcast</b>\n\nMessage:\n{message}\n\nUsers: {count}",
    "broadcast_done": "✅ Done!\n\n✅ Success: {success}\n❌ Failed: {failed}",
    "support_enter": "💬 <b>Send your message:</b>",
    "support_sent": "✅ Message sent! We'll reply soon.",
    "cancelled": "❌ Cancelled.",
    "error_occurred": "❌ Error occurred! Try again.",
    "loading": "⏳ Loading...",
    "finish": "✅ Finish",
    "skip": "⏭️ Skip",
    "back": "🔙 Back",
    "cancel": "❌ Cancel",
    "yes": "✅ Yes",
    "no": "❌ No",
    "next": "⏭️ Next",
    "previous": "⏮️ Previous",
    "confirm": "✅ Confirm",
    "multiple_choice": "📝 Multiple Choice",
    "true_false": "✅❌ True / False",
    "none_repeat": "❌ No Repeat",
    "daily": "📅 Daily",
    "weekly": "📆 Weekly",
    "monthly": "🗓️ Monthly",
    "quiz_result": """📊 <b>Quiz Result</b>

📝 {title}
✅ Correct: {correct}/{total}
📈 Score: {percentage}%

{grade}""",
    "excellent": "🏆 Excellent!",
    "very_good": "🌟 Very Good!",
    "good": "👍 Good",
    "fair": "📝 Fair",
    "fail": "📚 Needs Review",
    "queue_empty": "📭 Queue is empty.",
    "queue_item": "📋 {position}. {quiz_title} → {channel_title} ({status})",
    "ai_generate_prompt": "🤖 <b>Enter topic to generate questions:</b>",
    "ai_generating": "🤖 Generating questions with AI...",
    "ai_limit_reached": "⚠️ You've reached the daily AI limit ({limit} requests).",
    "calendar_view": "📅 <b>Publishing Schedule</b>\n\n{schedule}",
    "no_schedule": "📭 No publishing schedule.",
    "export_success": "✅ Quizzes exported!",
    "import_prompt": "📥 <b>Send a JSON or TXT file to import:</b>",
    "import_success": "✅ Imported {count} quizzes!",
    "import_failed": "❌ Import failed! Check the file format.",
    "help_text": """📖 <b>User Guide</b>

<b>Basic Commands:</b>
/start - Start bot
/help - Help
/add_quiz - Quick add question
/my_quizzes - My quizzes
/add_channel - Add channel
/my_channels - My channels
/stats - My statistics
/calendar - Publishing schedule
/queue - Publishing queue
/export - Export quizzes
/import - Import quizzes
/generate - Generate AI questions
/language - Change language
/admin - Admin panel

<b>Quick add format:</b>
<code>/add_quiz answer; question; opt1; opt2; opt3; opt4</code>""",
}
