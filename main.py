from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8628955679:AAHrH2CADokPkNtbuqgIIKJp2n6v43Aw1XA"

orders = {}
scores = {}
counter = 0

async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global counter
    counter += 1
    text = " ".join(context.args)

    keyboard = [[InlineKeyboardButton("✅ قبول", callback_data="take")]]

    msg = await update.message.reply_text(
        f"🔢 كوماند #{counter}\n\n🚚 كوموند جديد:\n\n{text}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    orders[msg.message_id] = {"taken": False, "text": text, "number": counter}

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user.first_name
    msg_id = query.message.message_id

    if orders.get(msg_id, {}).get("taken"):
        await query.answer("❌ هاد الكوموند خذاها شي واحد", show_alert=True)
        return

    orders[msg_id]["taken"] = True
    original_text = orders[msg_id]["text"]
    number = orders[msg_id]["number"]

    # زيد نقطة للي خذا الكوماند
    scores[user] = scores.get(user, 0) + 1

    await query.edit_message_text(
        f"✅ خذاها: {user}\n\n🔢 كوماند #{number}\n\n🚚 كوموند جديد:\n\n{original_text}"
    )
    await query.answer()

async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not orders:
        await update.message.reply_text("📋 ما كاين حتى كوماند!")
        return

    msg = "📋 *لائحة الكوماندات:*\n\n"
    for msg_id, data in orders.items():
        status = "✅ مخذوز" if data["taken"] else "⏳ في الانتظار"
        msg += f"#{data['number']} {status} — {data['text']}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not scores:
        await update.message.reply_text("🏆 ما كاين حتى واحد خذا كوماند!")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    msg = "🏆 *لائحة المتصدرين:*\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (user, score) in enumerate(sorted_scores):
        medal = medals[i] if i < 3 else f"{i+1}."
        msg += f"{medal} {user} — {score} كوماند\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("cmd", cmd))
app.add_handler(CommandHandler("list", list_orders))
app.add_handler(CommandHandler("top", top))
app.add_handler(CallbackQueryHandler(button))

print("Bot running...")
app.run_polling()