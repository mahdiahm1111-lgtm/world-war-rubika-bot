import asyncio
from rubika_bot_api.api import Robot
from rubika_bot_api import filters

from .config import load_settings
from .db import Database
from .game import Game, fmt
from .data import COUNTRIES

settings = load_settings()
db = Database(settings.db_path)
game = Game(db)
bot = Robot(token=settings.rubika_token)

HELP = """🌍 فرمان‌های بازی جنگ جهانی

/start — شروع
/myid — نمایش شناسه تو
/countries — فهرست کشورها
/choose <کشور> — انتخاب کشور
/me — پروفایل کشور من
/country <کشور> — مشاهده کشور
/status — وضعیت بازی
/income — دریافت درآمد نوبت
/attack <کشور> — شروع نبرد انتزاعی
/war — آخرین نبردها
/alliances — روابط و اتحادها
/leaderboard — رتبه‌بندی
/help — راهنما

فرمان‌های مالک:
/admin
/admin_give <کشور> <مقدار>
/admin_setpower <کشور> <قدرت>
/admin_turn
/admin_reset <کشور>
"""

def country_key(raw):
    raw = raw.strip().lower()
    aliases = {
        "ایرلند":"ireland","فرانسه":"france","آلمان":"germany","ایتالیا":"italy",
        "اسپانیا":"spain","ژاپن":"japan","ترکیه":"turkey","ایران":"iran",
        "مصر":"egypt","برزیل":"brazil","کانادا":"canada","هند":"india"
    }
    return aliases.get(raw, raw)

def profile(c):
    p = game.power(c)
    return (
        f"{c['emoji']} {c['name']}\n"
        f"━━━━━━━━━━━━\n"
        f"💰 خزانه: {fmt(c['treasury'])}\n"
        f"📈 اقتصاد: {fmt(c['economy'])}\n"
        f"🏭 صنعت: {fmt(c['industry'])}\n"
        f"👥 جمعیت: {fmt(c['population'])}\n"
        f"🗺️ سرزمین: {fmt(c['territory'])}\n"
        f"🔬 پژوهش: {fmt(c['research'])}\n"
        f"⭐ قدرت کل: {fmt(p)}"
    )

def require_owner(sender):
    if sender != settings.owner_guid:
        raise PermissionError("این فرمان فقط برای مالک ربات است.")

@bot.on_message(filters=filters.pv & filters.text)
async def handler(bot_instance, m):
    try:
        text = (m.text or "").strip()
        sender = m.sender_id
        if text.startswith("/start"):
            game.register(sender, getattr(m, "sender_name", None) or "بازیکن")
            await m.reply("🌍 به بازی جنگ جهانی خوش آمدی!\n\nبا /countries کشورها را ببین و سپس /choose ireland را بزن.\n\n/help")
            return

        if text == "/myid":
            await m.reply(f"🆔 شناسه شما:\n{sender}")
            return

        game.register(sender, getattr(m, "sender_name", None) or "بازیکن")
        parts = text.split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd == "/help":
            await m.reply(HELP)
        elif cmd == "/countries":
            await m.reply("\n".join(f"{c.emoji} {c.key} — {c.name}" for c in COUNTRIES))
        elif cmd == "/choose":
            if len(parts) < 2: raise ValueError("مثال: /choose ireland")
            key = country_key(parts[1])
            game.choose(sender, key)
            await m.reply("✅ کشور انتخاب شد:\n\n" + profile(game.country(key)))
        elif cmd in ("/me","/status"):
            p = game.player(sender)
            if not p or not p["country_key"]:
                await m.reply("هنوز کشوری انتخاب نکرده‌ای. /countries")
            else:
                await m.reply(profile(game.country(p["country_key"])) + f"\n\n🕐 نوبت بازی: {fmt(game.turn())}")
        elif cmd == "/country":
            if len(parts) < 2: raise ValueError("مثال: /country france")
            c = game.country(country_key(parts[1]))
            if not c: raise ValueError("کشور پیدا نشد.")
            await m.reply(profile(c))
        elif cmd == "/income":
            amount = game.income(sender)
            await m.reply(f"💰 درآمد این نوبت: +{fmt(amount)}")
        elif cmd == "/attack":
            if len(parts) < 2: raise ValueError("مثال: /attack france")
            result = game.attack(sender, country_key(parts[1]))
            w = game.country(result["winner"])
            await m.reply(
                "⚔️ نتیجه نبرد\n\n"
                f"مهاجم: {result['attacker']['emoji']} {result['attacker']['name']}\n"
                f"امتیاز: {fmt(result['ascore'])}\n\n"
                f"مدافع: {result['defender']['emoji']} {result['defender']['name']}\n"
                f"امتیاز: {fmt(result['dscore'])}\n\n"
                f"🏆 برنده: {w['emoji']} {w['name']}\n"
                "این نبرد کاملاً انتزاعی و مبتنی بر آمار بازی است."
            )
        elif cmd == "/leaderboard":
            rows = game.leaderboard()
            await m.reply("🏆 رتبه‌بندی\n\n" + "\n".join(
                f"{i}. {r['emoji']} {r['name']} — قدرت {fmt(game.power(r))}" for i,r in enumerate(rows,1)
            ))
        elif cmd == "/alliances":
            p = game.player(sender)
            if not p or not p["country_key"]: raise ValueError("ابتدا کشور انتخاب کن.")
            rows = game.alliances(p["country_key"])
            await m.reply("🤝 روابط\n\n" + ("\n".join(f"{r['relation']}: {r['b']}" for r in rows) or "هنوز رابطه‌ای ثبت نشده."))
        elif cmd == "/war":
            rows = db.fetchall("SELECT * FROM wars ORDER BY id DESC LIMIT 10")
            await m.reply("📜 آخرین نبردها\n\n" + ("\n".join(
                f"نوبت {fmt(r['turn'])}: {r['attacker']} vs {r['defender']} → {r['winner']}" for r in rows
            ) or "هنوز نبردی ثبت نشده."))
        elif cmd == "/admin":
            require_owner(sender)
            await m.reply("👑 پنل مالک\n/admin_give /admin_setpower /admin_turn /admin_reset")
        elif cmd == "/admin_give":
            require_owner(sender)
            if len(parts) < 3: raise ValueError("مثال: /admin_give ireland 1000")
            game.admin_give(country_key(parts[1]), int(parts[2]))
            await m.reply("✅ انجام شد.")
        elif cmd == "/admin_setpower":
            require_owner(sender)
            if len(parts) < 3: raise ValueError("مثال: /admin_setpower ireland 500")
            game.admin_setpower(country_key(parts[1]), int(parts[2]))
            await m.reply("✅ انجام شد.")
        elif cmd == "/admin_turn":
            require_owner(sender)
            t = game.advance_turn()
            await m.reply(f"🕐 نوبت جدید: {fmt(t)}")
        elif cmd == "/admin_reset":
            require_owner(sender)
            if len(parts) < 2: raise ValueError("مثال: /admin_reset ireland")
            game.admin_reset(country_key(parts[1]))
            await m.reply("♻️ کشور بازنشانی شد.")
        else:
            await m.reply("دستور شناخته نشد. /help")

    except PermissionError as e:
        await m.reply("⛔ " + str(e))
    except ValueError as e:
        await m.reply("❌ " + str(e))
    except Exception as e:
        print("ERROR:", repr(e))
        await m.reply("⚠️ خطای داخلی. لاگ سرور را بررسی کن.")

if __name__ == "__main__":
    asyncio.run(bot.run())
