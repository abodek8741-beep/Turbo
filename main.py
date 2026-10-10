هذا هو ملف `main.py` كاملًا. يقرأ الرمز من `TELEGRAM_BOT_TOKEN` في أسرار Replit ولا يتضمن الرمز نفسه. **بما أن النسخة السابقة احتوت رمزًا مكتوبًا داخل الملف، ألغِ الرمز القديم من BotFather وأنشئ آخر، ثم حدّث السر في Replit.**

```python
import logging
import os
import random
from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

WELCOME_GIFT_POINTS = 10
REFERRAL_POINTS = 50
DAILY_GIFT_POINTS = 30
TIKTOK_TASK_POINTS = 20

SUPPORT_USERNAME = "@abod097644"
BOT_USERNAME = "abodetbot"
TIKTOK_TASK_URL = "https://www.tiktok.com/@e..e233?_r=1&_t=ZS-9ARIQZKCRN9"

# بيانات مؤقتة: تُمسح عند إيقاف البوت أو إعادة تشغيله.
user_data = {}

PRODUCTS = {
    "tt_followers": {"name": "⚡️ 1000 متابع تيك توك", "price": 100},
    "tt_likes": {"name": "❤️ 5000 لايك تيك توك", "price": 50},
    "tt_views": {"name": "👁 10000 مشاهدة تيك توك", "price": 30},
    "fn_rare": {"name": "🎮 حساب فورتنايت نادر (نادره ونظاميه)", "price": 300},
    "fn_random": {"name": "🎲 حساب فورتنايت عشوائي", "price": 150},
    "yt_subs": {"name": "🔴 500 مشترك يوتيوب", "price": 200},
    "yt_views": {"name": "▶️ 5000 مشاهدة يوتيوب", "price": 80},
    "tg_members": {"name": "📢 1000 عضو قناة تليجرام", "price": 120},
    "ig_followers": {"name": "📸 1000 متابع انستقرام", "price": 110},
    "ig_likes": {"name": "💖 3000 لايك انستقرام", "price": 40},
}


def get_user_profile(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "points": WELCOME_GIFT_POINTS,
            "referrals": 0,
            "last_daily": None,
            "referred_by": None,
            "tiktok_done": False,
        }
    return user_data[user_id]


def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🛍 المتجر والخدمات", callback_data="shop"),
            InlineKeyboardButton("🎁 الهدية اليومية", callback_data="daily_gift"),
        ],
        [
            InlineKeyboardButton("🎮 تجميع نقاط والألعاب", callback_data="games"),
            InlineKeyboardButton(
                "📌 مهام تيك توك (20 نقطة)", callback_data="tiktok_task"
            ),
        ],
        [
            InlineKeyboardButton("🔗 رابط الدعوة", callback_data="referral"),
            InlineKeyboardButton("👤 حسابي ونقاطي", callback_data="my_account"),
        ],
        [
            InlineKeyboardButton(
                "🛠 الدعم الفني",
                url=f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None or update.message is None:
        return

    user_id = user.id
    is_new = user_id not in user_data
    profile = get_user_profile(user_id)

    if is_new and context.args:
        try:
            referrer_id = int(context.args[0])
            if referrer_id != user_id and referrer_id in user_data:
                profile["referred_by"] = referrer_id
                user_data[referrer_id]["points"] += REFERRAL_POINTS
                user_data[referrer_id]["referrals"] += 1
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=(
                            "🎉 قام شخص بالتسجيل عبر رابطك! "
                            f"حصلت على {REFERRAL_POINTS} نقطة."
                        ),
                    )
                except Exception:
                    logging.exception("تعذر إرسال إشعار الإحالة.")
        except ValueError:
            logging.info("تم تجاهل رمز إحالة غير صالح.")

    message_text = (
        f"أهلاً بك يا {user.first_name} في بوت الخدمات والمتجر الشامل! 👋\n\n"
        f"🎁 حصلت على {WELCOME_GIFT_POINTS} نقاط كهدية ترحيبية!"
    )
    await update.message.reply_text(
        message_text,
        reply_markup=get_main_keyboard(),
    )


def back_button(destination="main_menu", label="🔙 العودة"):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=destination)]]
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    user_id = query.from_user.id
    profile = get_user_profile(user_id)
    data = query.data or ""

    if query.message is None:
        return

    if data == "main_menu":
        await query.message.edit_text(
            "القائمة الرئيسية للمتجر:",
            reply_markup=get_main_keyboard(),
        )

    elif data == "my_account":
        text = (
            f"📊 <b>بيانات حسابك:</b>\n\n"
            f"🆔 الآيدي: <code>{user_id}</code>\n"
            f"💎 نقاطك الحالية: {profile['points']} نقطة\n"
            f"👥 عدد دعواتك: {profile['referrals']}"
        )
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=back_button(),
        )

    elif data == "daily_gift":
        today = date.today().isoformat()
        if profile["last_daily"] == today:
            text = "❌ لقد حصلت على هديتك اليومية بالفعل! عد غداً للمزيد."
        else:
            profile["last_daily"] = today
            profile["points"] += DAILY_GIFT_POINTS
            text = (
                f"🎉 مبروك! حصلت على {DAILY_GIFT_POINTS} نقطة كهدية يومية!\n"
                f"💎 رصيدك الجديد: {profile['points']} نقطة."
            )
        await query.message.edit_text(text, reply_markup=back_button())

    elif data == "referral":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        text = (
            f"🔗 <b>رابط الدعوة الخاص بك:</b>\n{ref_link}\n\n"
            f"• شارك الرابط مع أصدقائك، وكل شخص يسجل عبرك تحصل على "
            f"{REFERRAL_POINTS} نقطة!\n"
            f"• عدد مشاركاتك الناجحة: {profile['referrals']}"
        )
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=back_button(),
        )

    elif data == "tiktok_task":
        if profile["tiktok_done"]:
            text = "✅ لقد أتممت مهمة تيك توك مسبقاً وحصلت على مكافأتك!"
            keyboard = back_button()
        else:
            text = (
                "📌 <b>مهمة تيك توك:</b>\n"
                "تابع الحساب عبر الرابط، ثم اضغط زر تأكيد الإتمام "
                f"للحصول على {TIKTOK_TASK_POINTS} نقطة."
            )
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔗 رابط حساب التيك توك",
                            url=TIKTOK_TASK_URL,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "✅ تم الإضافة والمتابعة",
                            callback_data="claim_tiktok",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔙 العودة",
                            callback_data="main_menu",
                        )
                    ],
                ]
            )
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    elif data == "claim_tiktok":
        if not profile["tiktok_done"]:
            profile["tiktok_done"] = True
            profile["points"] += TIKTOK_TASK_POINTS
            text = (
                f"🎉 أضيفت لك {TIKTOK_TASK_POINTS} نقطة.\n"
                f"💎 رصيدك الحالي: {profile['points']} نقطة."
            )
        else:
            text = "⚠️ لقد حصلت على مكافأة هذه المهمة مسبقاً."
        await query.message.edit_text(text, reply_markup=back_button())

    elif data == "games":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🎡 عجلة الحظ", callback_data="spin_wheel")],
                [
                    InlineKeyboardButton(
                        "❌⭕️ لعبة X/O ضد الذكاء الاصطناعي",
                        callback_data="play_xo",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 العودة",
                        callback_data="main_menu",
                    )
                ],
            ]
        )
        await query.message.edit_text(
            "🎮 اختر لعبة لتجميع النقاط:",
            reply_markup=keyboard,
        )

    elif data == "spin_wheel":
        won = random.randint(5, 40)
        profile["points"] += won
        text = (
            f"🎡 دارت عجلة الحظ وحصلت على <b>{won}</b> نقطة! 🎉\n"
            f"💎 رصيدك الآن: {profile['points']}"
        )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🎮 الألعاب", callback_data="games"),
                    InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu"),
                ]
            ]
        )
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    elif data == "play_xo":
        result = random.choice(["win", "draw", "lose"])
        if result == "win":
            profile["points"] += 30
            text = (
                "🏆 <b>فزت على الذكاء الاصطناعي!</b>\n"
                f"🎉 حصلت على <b>30 نقطة</b>.\n"
                f"💎 رصيدك الآن: {profile['points']}"
            )
        elif result == "draw":
            profile["points"] += 15
            text = (
                "🤝 انتهت المباراة بالتعادل.\n"
                f"🎁 حصلت على <b>15 نقطة</b>.\n"
                f"💎 رصيدك الآن: {profile['points']}"
            )
        else:
            text = "❌ خسرت هذه المرة. حاول مجدداً!"

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔄 العب مرة أخرى",
                        callback_data="play_xo",
                    ),
                    InlineKeyboardButton("🔙 الألعاب", callback_data="games"),
                ]
            ]
        )
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    elif data == "shop":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📱 خدمات تيك توك", callback_data="cat_tt")],
                [InlineKeyboardButton("🎮 حسابات فورتنايت", callback_data="cat_fn")],
                [InlineKeyboardButton("🔴 خدمات يوتيوب", callback_data="cat_yt")],
                [InlineKeyboardButton("📢 دعم قنوات تليجرام", callback_data="cat_tg")],
                [InlineKeyboardButton("📸 خدمات انستقرام", callback_data="cat_ig")],
                [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")],
            ]
        )
        await query.message.edit_text(
            "🛍 اختر القسم الذي تريد التبضع منه:",
            reply_markup=keyboard,
        )

    elif data.startswith("cat_"):
        category = data.removeprefix("cat_")
        category_items = {
            "tt": [
                ("tt_followers", "⚡️ 1000 متابع (100 نقطة)"),
                ("tt_likes", "❤️ 5000 لايك (50 نقطة)"),
                ("tt_views", "👁 10000 مشاهدة (30 نقطة)"),
            ],
            "fn": [
                ("fn_rare", "🎮 حساب نادر (300 نقطة)"),
                ("fn_random", "🎲 حساب عشوائي (150 نقطة)"),
            ],
            "yt": [
                ("yt_subs", "🔴 500 مشترك (200 نقطة)"),
                ("yt_views", "▶️ 5000 مشاهدة (80 نقطة)"),
            ],
            "tg": [("tg_members", "📢 1000 عضو قناة (120 نقطة)")],
            "ig": [
                ("ig_followers", "📸 1000 متابع (110 نقطة)"),
                ("ig_likes", "💖 3000 لايك (40 نقطة)"),
            ],
        }
        items = category_items.get(category)
        if items is None:
            await query.message.edit_text(
                "القسم غير متوفر.",
                reply_markup=back_button("shop", "🔙 المتجر"),
            )
            return

        buttons = [
            [InlineKeyboardButton(name, callback_data=f"buy_{key}")]
            for key, name in items
        ]
        buttons.append(
            [InlineKeyboardButton("🔙 أقسام المتجر", callback_data="shop")]
        )
        await query.message.edit_text(
            "🛒 اختر الخدمة المطلوبة:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif data.startswith("buy_"):
        product_key = data.removeprefix("buy_")
        product = PRODUCTS.get(product_key)
        if product is None:
            await query.message.edit_text(
                "الخدمة غير متوفرة.",
                reply_markup=back_button("shop", "🔙 المتجر"),
            )
            return

        if profile["points"] >= product["price"]:
            profile["points"] -= product["price"]
            text = (
                f"✅ <b>تم شراء: {product['name']} بنجاح!</b>\n\n"
                "⚠️ قد يتأخر الرد من الدعم الفني؛ يرجى الانتظار.\n"
                f"📩 تواصل مع الدعم الفني لإتمام الطلب: {SUPPORT_USERNAME}\n"
                f"💎 الرصيد المتبقي: {profile['points']} نقطة."
            )
        else:
            text = (
                "❌ <b>رصيدك غير كافٍ!</b>\n\n"
                f"سعر الخدمة: {product['price']} نقطة.\n"
                f"رصيدك الحالي: {profile['points']} نقطة.\n"
                "💡 اجمع النقاط من الألعاب ورابط الدعوة أو مهمة تيك توك."
            )
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=back_button("shop", "🔙 المتجر"),
        )


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "لم يتم العثور على TELEGRAM_BOT_TOKEN. "
            "أضف رمز البوت إلى أسرار المشروع في Replit ثم أعد التشغيل."
        )

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    logging.info("تم تشغيل البوت بنجاح.")
    app.run_polling()


if __name__ == "__main__":
    main()
```
