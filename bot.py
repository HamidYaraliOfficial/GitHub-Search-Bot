import requests
import logging
import os
import math
import time
import datetime
import platform
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')

TELEGRAM_BOT_TOKEN = "Token"

GITHUB_TOKEN = "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" 
GITHUB_API_URL = "https://api.github.com"
REQUEST_TIMEOUT = 200 

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def format_progress_bar(percentage, length=10, filled_char="■", empty_char="□"):
    """ساخت نوار پیشرفت شیشه‌ای و زیبا"""
    filled_length = int(percentage * length)
    bar = filled_char * filled_length + empty_char * (length - filled_length)
    return f"[{bar}] {int(percentage * 100)}%"

def format_date(date_string):
    """تبدیل فرمت تاریخ ISO به فرمت قابل خواندن (بدون تایم‌زون)"""
    if not date_string: return "نامشخص"
    try:
        if 'Z' in date_string:
            date_string = date_string.replace('Z', '')
        elif '+' in date_string:
            date_string = date_string.split('+')[0]
        elif '-' in date_string and date_string.count('-') > 2:
            parts = date_string.split('-')
            if len(parts) > 3:
                date_string = '-'.join(parts[:-2]) + parts[-1].split(':')[0]
        
        dt = datetime.fromisoformat(date_string)
        
        return dt.strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Error parsing date {date_string}: {e}")
        return "نامشخص"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع مکالمه با کاربر با منوی شیشه‌ای فوق پیشرفته"""
    if update.effective_user and update.message:
        user = update.effective_user
        if context.chat_data is not None:
            context.chat_data.clear()
            
        glass_menu = [
            [
                InlineKeyboardButton("✨ جستجوی شیشه‌ای", callback_data="glass_search"),
                InlineKeyboardButton("🔥 ترندهای داغ گیت‌هاب", callback_data="trend")
            ],
            [
                InlineKeyboardButton("💎 زبان‌های برنامه‌نویسی", callback_data="ultra_language_select"),
                InlineKeyboardButton("📊 آمار و تحلیل", callback_data="status")
            ],
            [
                InlineKeyboardButton("🛡️ مشاهده سورس‌کدها", callback_data="search_menu"),
                InlineKeyboardButton("📚 راهنمای پیشرفته", callback_data="help")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(glass_menu)
        
        welcome_message = (
            "┏━━━━━━━━━━━━━━━━━━ 🌟 خوش آمدید 🌟 ━━━━━━━━━━━━━━━━━━┓\n\n"
            f"✨ *{user.first_name} عزیز*، به نسخه شیشه‌ای فوق‌پیشرفته ربات گیت‌هاب خوش آمدید! ✨\n\n"
            "🔮 *قابلیت‌های ویژه نسخه 3.0.0:*\n"
            "• رابط کاربری سه‌بعدی و شیشه‌ای\n"
            "• نوارهای پیشرفت انیمیشنی و پویا\n"
            "• جستجوی هوشمند با الگوریتم‌های پیشرفته\n"
            "• دانلود سورس‌کد با سرعت چندبرابر\n"
            "• تحلیل دقیق و گرافیکی ریپازیتوری‌ها\n"
            "• پشتیبانی از +۲۰ زبان برنامه‌نویسی\n"
            "• نمایش فایل‌های README با هایلایت کد\n\n"
            "🌈 از منوی شیشه‌ای زیر انتخاب کنید یا کلمه کلیدی خود را بنویسید\n\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "🧑‍💻 توسعه‌دهنده: Hamid Yarali"
        )
            
        await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        logger.error("User or message object is None in start function")

async def ask_for_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """کلمه کلیدی را ذخیره کرده و منوی انتخاب زبان را نمایش می‌دهد."""
    if not update.message:
        logger.error("Message object is None in ask_for_language")
        return
        
    query = update.message.text
    if not query:
        if update.message:
            await update.message.reply_text("لطفاً یک کلمه کلیدی برای جستجو وارد کنید.")
        return
        
    if context.chat_data is not None:
        context.chat_data['last_query'] = query

    keyboard = [
        [
            InlineKeyboardButton("Python 🐍", callback_data=f"lang:python:stars:1"),
            InlineKeyboardButton("JavaScript 📜", callback_data=f"lang:javascript:stars:1"),
        ],
        [
            InlineKeyboardButton("Java ☕", callback_data=f"lang:java:stars:1"),
            InlineKeyboardButton("Go 🐹", callback_data=f"lang:go:stars:1"),
        ],
        [
            InlineKeyboardButton("C++ 🔧", callback_data=f"lang:cpp:stars:1"),
            InlineKeyboardButton("C# 🎮", callback_data=f"lang:csharp:stars:1"), 
        ],
        [
            InlineKeyboardButton("همه زبان‌ها 🌐", callback_data=f"lang:any:stars:1")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = f"🔍 جستجو برای: *{query}*\n\nانتخاب کنید سورس کد را به چه زبانی می‌خواهید:"
    
    if update.callback_query and update.callback_query.message:
        await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.message:
        await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت هوشمند تمام کلیک‌ها با استفاده از حافظه چت"""
    if not update.callback_query:
        logger.error("Callback query is None in button_handler")
        return
        
    query = update.callback_query
    await query.answer()
    
    try:
        if not query.data:
            logger.error("Callback query data is None")
            return
            
        parts = query.data.split(":")
        action = parts[0]
        
        search_query = context.chat_data.get('last_query', "") if context.chat_data is not None else ""
        
        if not search_query and action not in ['start', 'back_to_start', 'details', 'get_source', 'read_readme', 'help', 'trend', 'search_menu', 'status', 'ask_keywords', 'advanced_search', 'glass_search', 'ultra_language_select', 'ultra_trending', 'ultra_keyword_search', 'ultra_advanced_search', 'video_tutorial', 'advanced_commands']: # اگر حافظه پاک شده باشد
            if query.message:
                await query.edit_message_text("خطایی رخ داد. لطفاً با دستور /start ربات را مجدداً راه‌اندازی کنید.")
            return

        if action == "lang":
            lang, sort, page = parts[1], parts[2], int(parts[3])
            await perform_search(update, context, lang, sort, page, search_query)
        elif action == "ultra_lang":
            lang, sort, page = parts[1], parts[2], int(parts[3])
            await perform_search(update, context, lang, sort, page, search_query)
        elif action == "sort":
            lang, sort = parts[1], parts[2]
            await perform_search(update, context, lang, sort, 1, search_query)
        elif action == "details":
            last_params = context.chat_data.get('last_params', {}) if context.chat_data is not None else {}
            repo_name = ":".join(parts[1:]) # برای هندل کردن نام ریپازیتوری حاوی ":"
            await show_details(update, context, repo_name, last_params)
        elif action == "get_source":
            repo_name = ":".join(parts[1:])
            await send_source_code(update, context, repo_full_name=repo_name)
        elif action == "read_readme":
            repo_name = ":".join(parts[1:])
            await search_readme(update, context, repo_name=repo_name)
        elif action == "back_to_lang":
            await ask_for_language(update, context)
        elif action == "open_filter":
            lang = parts[1]
            await show_filter_menu(update, context, lang)
        elif action == "back_to_start":
            await start(update, context)
        elif action == "help":
            await show_help(update, context)
        elif action == "trend":
            await show_trending(update, context)
        elif action == "search_menu":
            await search_menu(update, context)
        elif action == "glass_search":
            await ultra_glass_search(update, context)
        elif action == "ultra_language_select":
            await ultra_language_select(update, context)
        elif action == "ultra_trending":
            await show_trending(update, context)
        elif action == "ultra_keyword_search":
            await ask_for_language(update, context)
        elif action == "ultra_advanced_search":
            await search_menu(update, context)
        elif action == "ask_keywords":
            if query.message:
                keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی جستجو", callback_data="search_menu")]]
                await query.edit_message_text(
                    "🔍 *جستجو با کلمات کلیدی*\n\n"
                    "لطفاً کلمه کلیدی مورد نظر خود را برای جستجو وارد کنید.\n"
                    "مثال‌های مناسب:\n"
                    "• `telegram bot python`\n"
                    "• `web dashboard react`\n"
                    "• `machine learning tensorflow`\n"
                    "• `android app kotlin`\n\n"
                    "پس از ارسال کلمه کلیدی، می‌توانید زبان برنامه‌نویسی را انتخاب کنید.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        else:
            logger.warning(f"Unknown action: {action}")
    except Exception as e:
        logger.error(f"Error in button_handler: {e}")
        if query.message:
            await query.edit_message_text(f"خطایی رخ داد. لطفاً دوباره امتحان کنید.\n\nکد خطا: {str(e)[:50]}")
            
async def show_filter_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    """نمایش منوی پیشرفته فیلتر کردن نتایج"""
    if not update.callback_query or not update.callback_query.message:
        logger.error("Callback query or message is None in show_filter_menu")
        return
        
    keyboard = [
        [InlineKeyboardButton("⭐ بیشترین ستاره (پیش‌فرض)", callback_data=f"sort:{lang}:stars")],
        [InlineKeyboardButton("🍴 بیشترین فورک", callback_data=f"sort:{lang}:forks")],
        [InlineKeyboardButton("🔄 آخرین آپدیت", callback_data=f"sort:{lang}:updated")],
        [InlineKeyboardButton("👁️ محبوب‌ترین", callback_data=f"sort:{lang}:best-match")],
        [InlineKeyboardButton("🔙 بازگشت به نتایج", callback_data=f"lang:{lang}:stars:1")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("نتایج را بر اساس کدام معیار مرتب کنم؟", reply_markup=reply_markup)

async def perform_search(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str, sort: str, page: int, search_query: str) -> None:
    """جستجو در گیت‌هاب با پارامترهای مشخص شده"""
    if not update.callback_query or not update.callback_query.message:
        logger.error("Callback query or message is None in perform_search")
        return
        
    if context.chat_data is not None:
        context.chat_data['last_params'] = {'language': language, 'sort': sort, 'page': page}
    
    await update.callback_query.edit_message_text(text=f"🔍 در حال جستجوی `{search_query}`...", parse_mode='Markdown')

    final_query = search_query
    if language != "any": final_query += f" language:{language}"

    items_per_page = 5
    params = {'q': final_query, 'sort': sort, 'order': 'desc', 'per_page': items_per_page, 'page': page}
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN and GITHUB_TOKEN != "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
        headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'

    try:
        response = requests.get(f"{GITHUB_API_URL}/search/repositories", params=params, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if not data['items']:
            await update.callback_query.edit_message_text("متاسفانه با این فیلتر نتیجه‌ای پیدا نشد. لطفاً با کلیدواژه دیگری امتحان کنید.")
            return

        total_count = data.get('total_count', 0)
        total_pages = math.ceil(min(total_count, 1000) / items_per_page)
        
        sort_emoji = "⭐" if sort == "stars" else "🍴" if sort == "forks" else "🔄" if sort == "updated" else "👁️"
        lang_emoji = "🐍" if language == "python" else "📜" if language == "javascript" else "☕" if language == "java" else "🐹" if language == "go" else "🔧" if language == "cpp" else "🎮" if language == "csharp" else "🌐"
        
        message = f"🔍 *نتایج برای «{search_query}»*\n"
        message += f"{lang_emoji} زبان: {language.upper() if language != 'any' else 'همه زبان‌ها'}\n"
        message += f"{sort_emoji} مرتب‌سازی: {sort}\n"
        message += f"📊 تعداد کل نتایج: {total_count:,}\n"
        message += f"📄 صفحه {page}/{total_pages}\n\n"
        
        keyboard = []
        for idx, repo in enumerate(data['items'], 1):
            repo_name = repo['full_name']
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            message += f"{idx}. *{repo_name}*\n"
            message += f"⭐ {stars:,} | 🍴 {forks:,}\n"
            message += f"🔍 {repo.get('description', 'بدون توضیحات')[:60]}...\n\n"
            
            keyboard.append([
                InlineKeyboardButton(f"📥 دریافت سورس", callback_data=f"get_source:{repo_name}"),
                InlineKeyboardButton(f"ℹ️ جزئیات", callback_data=f"details:{repo_name}")
            ])

        pagination_buttons = []
        if page > 1: pagination_buttons.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"lang:{language}:{sort}:{page-1}"))
        if page < total_pages: pagination_buttons.append(InlineKeyboardButton("بعدی ➡️", callback_data=f"lang:{language}:{sort}:{page+1}"))
        
        if pagination_buttons:
            keyboard.append(pagination_buttons)
            
        keyboard.append([
            InlineKeyboardButton("🔙 انتخاب زبان", callback_data=f"back_to_lang"),
            InlineKeyboardButton("📊 فیلترها", callback_data=f"open_filter:{language}")
        ])

        await update.callback_query.edit_message_text(
            text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown', disable_web_page_preview=True
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling GitHub API: {e}")
        await update.callback_query.edit_message_text(f"خطایی در ارتباط با گیت‌هاب رخ داد. لطفاً دوباره امتحان کنید.\n\nجزئیات خطا: {str(e)[:50]}")
    except Exception as e:
        logger.error(f"Unexpected error in perform_search: {e}")
        await update.callback_query.edit_message_text(f"خطای غیرمنتظره رخ داد. لطفاً دوباره امتحان کنید.\n\nجزئیات خطا: {str(e)[:50]}")

async def show_details(update: Update, context: ContextTypes.DEFAULT_TYPE, repo_name: str, last_params: dict) -> None:
    """نمایش جزئیات کامل یک ریپازیتوری"""
    if not update.callback_query or not update.callback_query.message:
        logger.error("Callback query or message is None in show_details")
        return
        
    await update.callback_query.edit_message_text(text=f"🔍 در حال دریافت جزئیات ریپازیتوری `{repo_name}`...", parse_mode='Markdown')
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN and GITHUB_TOKEN != "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
        headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'
    
    try:
        response = requests.get(f"{GITHUB_API_URL}/repos/{repo_name}", headers=headers, timeout=15)
        response.raise_for_status()
        repo = response.json()

        langs_response = requests.get(repo.get('languages_url', ''), headers=headers, timeout=10)
        langs_response.raise_for_status()
        langs = langs_response.json()
        
        total_bytes = sum(langs.values()) if langs else 0
        lang_percents = {}
        if total_bytes > 0:
            for lang, bytes_count in langs.items():
                lang_percents[lang] = round((bytes_count / total_bytes) * 100, 1)
        
        langs_text = ""
        if lang_percents:
            top_langs = sorted(lang_percents.items(), key=lambda x: x[1], reverse=True)[:3]
            langs_text = " | ".join([f"{lang} ({percent}%)" for lang, percent in top_langs])
        else:
            langs_text = "نامشخص"

        license_name = repo.get('license', {}).get('name', 'نامشخص') if repo.get('license') else 'نامشخص'
        
        message = (
            f"🗂️ *مشخصات ریپازیتوری* `{repo_name}`\n\n"
            f"📝 *توضیحات:*\n{repo.get('description', 'موجود نیست.')}\n\n"
            f"🔗 *لینک:* [{repo.get('html_url', '#')}]({repo.get('html_url', '#')})\n"
            f"⭐ *ستاره‌ها:* {repo.get('stargazers_count', 0):,}\n"
            f"🍴 *فورک‌ها:* {repo.get('forks_count', 0):,}\n"
            f"👀 *واچرها:* {repo.get('watchers_count', 0):,}\n"
            f"⚠️ *ایشوها:* {repo.get('open_issues_count', 0):,}\n"
            f"🖥️ *زبان‌ها:* {langs_text}\n"
            f"📜 *لایسنس:* `{license_name}`\n"
            f"👤 *مالک:* [{repo.get('owner', {}).get('login', 'نامشخص')}]({repo.get('owner', {}).get('html_url', '#')})\n"
            f"📅 *تاریخ ساخت:* {format_date(repo.get('created_at'))}\n"
            f"🔄 *آخرین آپدیت:* {format_date(repo.get('pushed_at'))}\n"
        )
        
        message += f"🌿 *شاخه پیشفرض:* `{repo.get('default_branch', 'master')}`\n"
        
        has_readme = False
        try:
            readme_response = requests.get(f"{GITHUB_API_URL}/repos/{repo_name}/readme", headers=headers, timeout=10)
            if readme_response.status_code == 200:
                message += "\n🔍 *دارای فایل README*"
                has_readme = True
        except:
            pass
            
        back_cb = f"lang:{last_params.get('language', 'any')}:{last_params.get('sort', 'stars')}:{last_params.get('page', 1)}"
        keyboard = [
            [
                InlineKeyboardButton("📥 دریافت سورس", callback_data=f"get_source:{repo_name}"),
                InlineKeyboardButton("🔗 مشاهده در گیت‌هاب", url=repo.get('html_url', '#'))
            ]
        ]
        
        if has_readme:
            keyboard.append([InlineKeyboardButton("📄 مشاهده README", callback_data=f"read_readme:{repo_name}")])
            
        keyboard.append([InlineKeyboardButton("🔙 بازگشت به نتایج", callback_data=back_cb)])
        
        await update.callback_query.edit_message_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown', disable_web_page_preview=True
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in show_details: {e}")
        await update.callback_query.edit_message_text(f"خطا در دریافت جزئیات. لطفاً دوباره امتحان کنید.\n\n{str(e)[:50]}")
    except Exception as e:
        logger.error(f"Unexpected error in show_details: {e}")
        await update.callback_query.edit_message_text(f"خطای غیرمنتظره رخ داد. لطفاً دوباره امتحان کنید.\n\n{str(e)[:50]}")

async def send_source_code(update: Update, context: ContextTypes.DEFAULT_TYPE, repo_full_name: str) -> None:
    """دانلود و ارسال سورس کد یک ریپازیتوری با نوار پیشرفت شیشه‌ای"""
    if not update.callback_query or not update.callback_query.message or not update.callback_query.message.chat:
        logger.error("Invalid callback query structure in send_source_code")
        return
    
    chat_id = update.callback_query.message.chat.id
    message = update.callback_query.message
    
    try:
        glass_message = (
            "╔═════════ 📡 اتصال به سرور ═════════╗\n\n"
            "🔄 در حال برقراری ارتباط با سرورهای گیت‌هاب...\n"
            f"📂 ریپازیتوری: `{repo_full_name}`\n\n"
            f"{format_progress_bar(0.1, 20, '■', '□')}\n"
            "⏳ لطفاً منتظر بمانید...\n\n"
            "╚═════════════════════════════════════╝"
        )
        sent_message = await context.bot.send_message(
            chat_id=chat_id,
            text=glass_message,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error sending initial message: {e}")
        return
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN and GITHUB_TOKEN != "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
        headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'
    
    try:
        start_time = time.time()
        
        glass_message = (
            "╔═════════ 📡 اتصال به سرور ═════════╗\n\n"
            "✅ اتصال به سرور گیت‌هاب برقرار شد\n"
            f"📂 ریپازیتوری: `{repo_full_name}`\n\n"
            f"{format_progress_bar(0.2, 20, '■', '□')}\n"
            "⏳ در حال دریافت اطلاعات ریپازیتوری...\n\n"
            "╚═════════════════════════════════════╝"
        )
        await sent_message.edit_text(glass_message, parse_mode='Markdown')
        
        repo_info_res = requests.get(f"{GITHUB_API_URL}/repos/{repo_full_name}", headers=headers, timeout=REQUEST_TIMEOUT)
        repo_info_res.raise_for_status()
        repo_info = repo_info_res.json()
        
        default_branch = repo_info.get('default_branch', 'master')
        repo_size = repo_info.get('size', 0) # سایز به کیلوبایت
        
        if repo_size > 100000: # بیشتر از 100 مگابایت
            glass_message = (
                "╔═════════ ⚠️ هشدار ═════════╗\n\n"
                f"⚠️ این ریپازیتوری بسیار بزرگ است ({repo_size/1000:.1f} MB).\n"
                "دانلود ممکن است طول بکشد یا با خطا مواجه شود.\n\n"
                "آیا مطمئنید که می‌خواهید ادامه دهید؟\n"
                "دانلود تا 5 ثانیه دیگر شروع می‌شود...\n\n"
                "╚════════════════════════════╝"
            )
            await sent_message.edit_text(glass_message, parse_mode='Markdown')
            time.sleep(3) # مکث کوتاه برای نمایش هشدار
        
        glass_message = (
            "╔═════════ 📥 دانلود سورس ═════════╗\n\n"
            f"📦 ریپازیتوری: `{repo_full_name}`\n"
            f"🌿 شاخه: `{default_branch}`\n"
            f"📏 حجم تقریبی: {repo_size/1000:.1f} MB\n\n"
            f"{format_progress_bar(0.3, 20, '■', '□')}\n"
            "⏳ در حال دانلود سورس کد...\n\n"
            "╚═══════════════════════════════════╝"
        )
        await sent_message.edit_text(glass_message, parse_mode='Markdown')

        zip_url = f"https://github.com/{repo_full_name}/archive/refs/heads/{default_branch}.zip"
        zip_res = requests.get(zip_url, stream=True, headers=headers, timeout=REQUEST_TIMEOUT)
        zip_res.raise_for_status()
        
        file_path = f"{repo_full_name.replace('/', '_')}.zip"
        downloaded_size = 0
        
        estimated_total_size = repo_size * 1024  # تبدیل کیلوبایت به بایت
        if estimated_total_size == 0:
            estimated_total_size = 1024 * 1024  # اگر سایز صفر بود، 1 مگابایت فرض کن
            
        with open(file_path, 'wb') as f:
            for chunk in zip_res.iter_content(chunk_size=8192):
                if chunk:  # فیلتر کردن keepalive های خالی
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if downloaded_size % (2 * 1024 * 1024) < 8192:  # تقریباً هر 2 مگابایت
                        progress = min(0.9, 0.3 + (downloaded_size / estimated_total_size * 0.6))
                        progress_bar = format_progress_bar(progress, 20, '■', '□')
                        
                        download_time = time.time() - start_time
                        download_speed = downloaded_size / (download_time * 1024 * 1024) if download_time > 0 else 0
                        
                        glass_message = (
                            "╔═════════ 📥 دانلود سورس ═════════╗\n\n"
                            f"📦 ریپازیتوری: `{repo_full_name}`\n"
                            f"🔽 دانلود شده: {downloaded_size/(1024*1024):.1f} MB\n"
                            f"🚀 سرعت: {download_speed:.2f} MB/s\n\n"
                            f"{progress_bar}\n"
                            "⏳ در حال دانلود سورس کد...\n\n"
                            "╚═══════════════════════════════════╝"
                        )
                        await sent_message.edit_text(glass_message, parse_mode='Markdown')
        
        download_time = time.time() - start_time
        download_speed = downloaded_size / (download_time * 1024 * 1024) if download_time > 0 else 0
        
        glass_message = (
            "╔═════════ ✅ دانلود کامل شد ═════════╗\n\n"
            f"📦 ریپازیتوری: `{repo_full_name}`\n"
            f"📏 حجم فایل: {downloaded_size/(1024*1024):.1f} MB\n"
            f"⏱️ زمان: {download_time:.1f} ثانیه\n"
            f"🚀 سرعت: {download_speed:.2f} MB/s\n\n"
            f"{format_progress_bar(1.0, 20, '■', '□')}\n"
            "📤 در حال آپلود فایل برای شما...\n\n"
            "╚═════════════════════════════════════╝"
        )
        await sent_message.edit_text(glass_message, parse_mode='Markdown')
        
        caption = f"✨ *سورس کد ریپازیتوری*\n📦 `{repo_full_name}`\n🌿 شاخه: `{default_branch}`\n📏 حجم: {downloaded_size/(1024*1024):.1f} MB\n\n🧑‍💻 توسعه‌دهنده: Hamid Yarali"
        await context.bot.send_document(
            chat_id=chat_id, 
            document=open(file_path, 'rb'), 
            caption=caption, 
            parse_mode='Markdown'
        )
        
        await sent_message.delete()
        
        if os.path.exists(file_path):
            os.remove(file_path)

    except requests.exceptions.Timeout:
        glass_message = (
            "╔═════════ ⚠️ خطا ═════════╗\n\n"
            "⏱️ سرور گیت‌هاب در زمان مناسب پاسخ نداد.\n"
            "لطفاً بعداً دوباره امتحان کنید.\n\n"
            "╚═══════════════════════════╝"
        )
        await sent_message.edit_text(glass_message, parse_mode='Markdown')
    except requests.exceptions.HTTPError as e:
        error_message = "خطای نامشخص"
        if e.response.status_code == 403:
            error_message = "این ریپازیتوری خصوصی است یا دسترسی به آن ممنوع می‌باشد."
        elif e.response.status_code == 404:
            error_message = "ریپازیتوری یا مسیر موردنظر یافت نشد."
        else:
            error_message = f"کد خطا: {e.response.status_code}"
            
        glass_message = (
            "╔═════════ ⚠️ خطا ═════════╗\n\n"
            f"❌ {error_message}\n\n"
            "╚═══════════════════════════╝"
        )
        await sent_message.edit_text(glass_message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in send_source_code: {e}")
        glass_message = (
            "╔═════════ ⚠️ خطا ═════════╗\n\n"
            "خطا در دانلود سورس.\n"
            "ریپازیتوری ممکن است خصوصی، حجیم یا حذف شده باشد.\n\n"
            f"جزئیات: {str(e)[:50]}\n\n"
            "╚═══════════════════════════╝"
        )
        await sent_message.edit_text(glass_message, parse_mode='Markdown')
        
        if os.path.exists(file_path):
            os.remove(file_path)

async def search_readme(update: Update, context: ContextTypes.DEFAULT_TYPE, repo_name: str | None = None) -> None:
    """دریافت و نمایش README یک ریپازیتوری"""
    if not update.callback_query or not update.callback_query.message:
        logger.error("Invalid callback query structure in search_readme")
        return
    
    try:
        if repo_name is None and update.callback_query.data:
            parts = update.callback_query.data.split(":")
            if len(parts) > 1:
                repo_name = ":".join(parts[1:]) # برای هندل کردن نام ریپازیتوری حاوی ":"
        
        if not repo_name:
            await update.callback_query.edit_message_text("خطا: نام ریپازیتوری مشخص نشده است.")
            return
            
        await update.callback_query.edit_message_text(f"در حال دریافت README برای {repo_name}...", parse_mode='Markdown')
        
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if GITHUB_TOKEN and GITHUB_TOKEN != "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
            headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'
        
        response = requests.get(f"{GITHUB_API_URL}/repos/{repo_name}/readme", headers=headers, timeout=15)
        response.raise_for_status()
        
        readme_data = response.json()
        content = readme_data.get('content', '')
        
        if content:
            import base64
            content = base64.b64decode(content).decode('utf-8', errors='ignore')
            
            if len(content) > 4000:
                content = content[:3950] + "...\n\n[ادامه README در گیت‌هاب]"
            
            message = f"📃 *README برای {repo_name}*\n\n```\n{content}\n```\n\n🧑‍💻 توسعه‌دهنده: Hamid Yarali"
            
            if len(message) > 4096:
                chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
                await update.callback_query.edit_message_text(chunks[0], parse_mode='Markdown')
                
                if update.callback_query.message and update.callback_query.message.chat:
                    chat_id = update.callback_query.message.chat.id
                    for chunk in chunks[1:]:
                        try:
                            await context.bot.send_message(chat_id=chat_id, text=chunk, parse_mode='Markdown')
                        except Exception as e:
                            logger.error(f"Error sending message chunk: {e}")
            else:
                await update.callback_query.edit_message_text(message, parse_mode='Markdown')
        else:
            await update.callback_query.edit_message_text(f"⚠️ فایل README برای {repo_name} یافت نشد.")
    except Exception as e:
        logger.error(f"Error in search_readme: {e}")
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.edit_message_text(f"⚠️ خطا در دریافت README: {str(e)[:100]}")
            except Exception:
                pass

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش راهنمای استفاده از ربات"""
    help_text = (
        "*🔍 راهنمای ربات جستجوی گیت‌هاب*\n\n"
        "با این ربات می‌توانید در میان میلیون‌ها پروژه متن‌باز گیت‌هاب جستجو کنید و سورس کد آن‌ها را دریافت نمایید.\n\n"
        "*دستورات اصلی:*\n"
        "• /start - شروع استفاده از ربات\n"
        "• /help - نمایش این راهنما\n"
        "• /search - جستجوی یک کلمه کلیدی\n"
        "• /trend - نمایش ریپازیتوری‌های محبوب\n\n"
        "*نحوه استفاده:*\n"
        "1️⃣ یک کلمه کلیدی مانند `telegram bot python` بنویسید\n"
        "2️⃣ زبان برنامه‌نویسی مورد نظر خود را انتخاب کنید\n"
        "3️⃣ از بین نتایج، ریپازیتوری مورد نظر را انتخاب کنید\n"
        "4️⃣ می‌توانید جزئیات بیشتر را ببینید یا سورس کد را دریافت کنید\n\n"
        "*نکات مهم:*\n"
        "• برای جستجوی دقیق‌تر، از کلمات کلیدی خاص‌تر استفاده کنید\n"
        "• دانلود ریپازیتوری‌های بزرگ ممکن است زمان‌بر باشد\n"
        "• این ربات فقط ریپازیتوری‌های عمومی را نمایش می‌دهد\n"
        "• محدودیت API گیت‌هاب: حداکثر 60 درخواست در هر ساعت\n\n"
        "🧑‍💻 *توسعه‌دهنده:* [Hamid Yarali](https://www.instagram.com/hamidyaraliofficial?igsh=MWpxZjhhMHZuNnlpYQ==)"
    )
    
    if update.message:
        await update.message.reply_text(help_text, parse_mode='Markdown', disable_web_page_preview=True)
    elif update.callback_query:
        await update.callback_query.edit_message_text(help_text, parse_mode='Markdown', disable_web_page_preview=True)

async def show_trending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش ریپازیتوری‌های ترند گیت‌هاب"""
    try:
        chat_id = None
        message_id = None
        
        if update.message:
            chat_id = update.message.chat_id
            response = await context.bot.send_message(
                chat_id=chat_id,
                text="در حال دریافت لیست ریپازیتوری‌های ترند..."
            )
            message_id = response.message_id
        elif update.callback_query and update.callback_query.message:
            chat_id = update.callback_query.message.chat.id if hasattr(update.callback_query.message, "chat") and update.callback_query.message.chat else None
            message_id = update.callback_query.message.message_id
            if chat_id and message_id:  # اطمینان از وجود chat_id و message_id
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="در حال دریافت لیست ریپازیتوری‌های ترند..."
                )
        else:
            logger.error("No valid message or callback query in show_trending")
            return
            
        if not chat_id:
            logger.error("Unable to determine chat_id in show_trending")
            return
        
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if GITHUB_TOKEN and GITHUB_TOKEN != "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
            headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'
        
        try:
            today = datetime.now(tehran_tz).strftime('%Y-%m-%d')
            seven_days_ago = (datetime.now(tehran_tz) - timedelta(days=7)).strftime('%Y-%m-%d')
            
            params = {
                'q': f'created:{seven_days_ago}..{today}',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            response = requests.get(f"{GITHUB_API_URL}/search/repositories", params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if not data['items']:
                if chat_id:  # اطمینان از وجود chat_id
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="⚠️ نتیجه‌ای یافت نشد. لطفاً بعداً دوباره امتحان کنید."
                    )
                return
                
            trending_text = f"🔥 *پرطرفدارترین ریپازیتوری‌های هفته اخیر*\n\n"
            keyboard = []
            
            for idx, repo in enumerate(data['items'], 1):
                repo_name = repo['full_name']
                stars = repo.get('stargazers_count', 0)
                desc = repo.get('description', 'بدون توضیحات')[:50] + "..." if repo.get('description') else 'بدون توضیحات'
                lang = repo.get('language', 'نامشخص')
                
                trending_text += f"{idx}. *{repo_name}* ({lang})\n"
                trending_text += f"⭐ {stars:,} | {desc}\n\n"
                
                keyboard.append([
                    InlineKeyboardButton(f"📥 دانلود #{idx}", callback_data=f"get_source:{repo_name}"),
                    InlineKeyboardButton(f"ℹ️ جزئیات #{idx}", callback_data=f"details:{repo_name}")
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if chat_id and message_id:  # اطمینان از وجود chat_id و message_id
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=trending_text + "\n🧑‍💻 توسعه‌دهنده: Hamid Yarali",
                        reply_markup=reply_markup,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    logger.error(f"Error editing message: {e}")
                    if chat_id:  # اطمینان از وجود chat_id
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=trending_text + "\n🧑‍💻 توسعه‌دهنده: Hamid Yarali",
                            reply_markup=reply_markup,
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )
            else:
                if chat_id:  # اطمینان از وجود chat_id
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=trending_text + "\n🧑‍💻 توسعه‌دهنده: Hamid Yarali",
                        reply_markup=reply_markup,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
        
        except Exception as e:
            logger.error(f"Error in show_trending API call: {e}")
            if chat_id:  # اطمینان مجدد از وجود chat_id
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"⚠️ خطا در دریافت لیست ترندها: {str(e)[:100]}"
                    )
                except Exception as inner_e:
                    logger.error(f"Failed to send error message: {inner_e}")
    
    except Exception as e:
        logger.error(f"General error in show_trending: {e}")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """هندل کردن دستور /search برای شروع جستجو"""
    if update.message:
        if context.args and len(context.args) > 0:
            search_query = ' '.join(context.args)
            if context.chat_data is not None:
                context.chat_data['last_query'] = search_query
            await ask_for_language(update, context)
        else:
            await update.message.reply_text(
                "لطفاً کلمه کلیدی مورد نظر خود را برای جستجو وارد کنید.\n"
                "مثال: `telegram bot python`", 
                parse_mode='Markdown'
            )

async def send_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش وضعیت ربات و اطلاعات سرور"""
    import platform
    import psutil
    
    if update.message:
        message = update.message
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            python_version = platform.python_version()
            os_info = platform.platform()
            
            bot_uptime = "نامشخص"
            
            status_text = (
                "🤖 *وضعیت ربات جستجوی گیت‌هاب*\n\n"
                f"✅ *وضعیت:* فعال و آماده به کار\n"
                f"⏱ *آپتایم:* {bot_uptime}\n\n"
                f"🖥 *اطلاعات سرور:*\n"
                f"• CPU: {cpu_percent}%\n"
                f"• RAM: {memory_percent}%\n"
                f"• دیسک: {disk_percent}%\n"
                f"• سیستم‌عامل: {os_info}\n"
                f"• نسخه پایتون: {python_version}\n\n"
                f"📊 *محدودیت‌های API گیت‌هاب:*\n"
                f"• حداکثر درخواست در ساعت: 60\n"
                f"• حداکثر تعداد نتایج: 1000\n\n"
                "*💾 نسخه ربات:* 🔮✨ 3.0.0 ULTRA Glass Edition ✨🔮\n\n"
                "🧑‍💻 توسعه‌دهنده: Hamid Yarali"
            )
            
            await message.reply_text(status_text, parse_mode='Markdown')
        except ImportError:
            status_text = (
                "🤖 *وضعیت ربات جستجوی گیت‌هاب*\n\n"
                "✅ *وضعیت:* فعال و آماده به کار\n\n"
                "*💾 نسخه ربات:* 3.0.0 Ultra Glass Edition\n\n"
                "🧑‍💻 توسعه‌دهنده: Hamid Yarali"
            )
            await message.reply_text(status_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in send_status: {e}")
            await message.reply_text(f"خطا در دریافت وضعیت: {str(e)[:100]}")

async def search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش منوی جستجوی شیشه‌ای"""
    if update.callback_query and update.callback_query.message:
        await update.callback_query.answer()
        
        message = (
            "✨ *جستجوی شیشه‌ای گیت‌هاب* ✨\n\n"
            "لطفاً نوع جستجو را انتخاب کنید:\n\n"
            "🔸 *جستجو با کلمات کلیدی:* این گزینه به شما امکان می‌دهد با کلمات کلیدی جستجو کنید\n\n"
            "🔸 *جستجو بر اساس زبان:* جستجو در بین پروژه‌های یک زبان برنامه‌نویسی خاص\n\n"
            "🔸 *جستجوی پیشرفته:* استفاده از فیلترهای پیشرفته برای جستجوی دقیق‌تر\n\n"
            "🔸 *مشاهده ترندها:* دیدن محبوب‌ترین پروژه‌های اخیر گیت‌هاب\n\n"
            "🧑‍💻 توسعه‌دهنده: Hamid Yarali"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔤 جستجو با کلمات کلیدی", callback_data="ask_keywords")],
            [InlineKeyboardButton("💻 جستجو بر اساس زبان", callback_data="open_filter:any")],
            [InlineKeyboardButton("⚙️ جستجوی پیشرفته", callback_data="advanced_search")],
            [InlineKeyboardButton("🔥 مشاهده ترندها", callback_data="trend")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
        ]
        
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        

async def ultra_glass_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """جستجوی فوق پیشرفته با رابط شیشه‌ای سه بعدی"""
    if not update.effective_chat:
        logger.error("Invalid chat in ultra_glass_search")
        return
        
    chat_id = update.effective_chat.id
    
    search_title = "✨ جستجوی گیت‌هاب ✨"
    search_text = (
        "به بخش جستجوی فوق‌پیشرفته  خوش آمدید!\n"
        "در این بخش می‌توانید با امکانات ویژه در گیت‌هاب جستجو کنید.\n\n"
        "🔍 روش‌های جستجو:\n"
        "• جستجوی کلمات کلیدی\n"
        "• جستجو بر اساس زبان برنامه‌نویسی\n"
        "• جستجوی پیشرفته با فیلترها\n"
        "• جستجوی ریپوزیتوری‌های ترند\n\n"
        "🧑‍💻 توسعه‌دهنده: Hamid Yarali"
    )
    
    glass_message = (
        "┏━━━━━━━━━━━━━━━ ✨ جستجوی  گیت‌هاب ✨ ━━━━━━━━━━━━━━━┓\n\n"
        f"{search_text}\n\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✨ جستجوی هوشمند", 
                                callback_data="ultra_keyword_search")
        ],
        [
            InlineKeyboardButton("✦ انتخاب زبان برنامه‌نویسی", 
                                callback_data="ultra_language_select")
        ],
        [
            InlineKeyboardButton("💎 جستجوی پیشرفته", 
                                callback_data="ultra_advanced_search")
        ],
        [
            InlineKeyboardButton("🔥 ترندهای گیت‌هاب", 
                                callback_data="ultra_trending")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_start")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        if update.callback_query.message:
            await update.callback_query.edit_message_text(
                text=glass_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=glass_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def ultra_language_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی پیشرفته انتخاب زبان برنامه‌نویسی با طراحی شیشه‌ای سه‌بعدی"""
    if not update.callback_query:
        logger.error("No callback query in ultra_language_select")
        return
        
    title = "🌈 انتخاب زبان برنامه‌نویسی"
    message_text = (
        "لطفاً زبان برنامه‌نویسی مورد نظر خود را انتخاب کنید.\n"
        "رابط کاربری شیشه‌ای بهترین نتایج را به شما نمایش خواهد داد.\n\n"
        "💻 زبان‌های محبوب:\n"
        "• Python - زبان همه‌کاره و قدرتمند\n"
        "• JavaScript - برای برنامه‌نویسی وب\n"
        "• Java - برنامه‌نویسی سازمانی\n"
        "• Go - سرعت و کارایی بالا\n"
        "• C++ - عملکرد و سرعت فوق‌العاده\n"
        "• C# - توسعه اپلیکیشن‌های ویندوز و بازی\n"
        "• Ruby - بهره‌وری و خوانایی\n"
        "• PHP - توسعه وب\n\n"
        "🧑‍💻 توسعه‌دهنده: Hamid Yarali"
    )
    
    glass_message = (
        "┏━━━━━━━━━━━━━━ 🌈 انتخاب زبان برنامه‌نویسی ━━━━━━━━━━━━━━┓\n\n"
        f"{message_text}\n\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("Python 🐍", callback_data=f"ultra_lang:python:stars:1"),
            InlineKeyboardButton("JavaScript 📜", callback_data=f"ultra_lang:javascript:stars:1")
        ],
        [
            InlineKeyboardButton("Java ☕", callback_data=f"ultra_lang:java:stars:1"),
            InlineKeyboardButton("Go 🐹", callback_data=f"ultra_lang:go:stars:1")
        ],
        [
            InlineKeyboardButton("C++ 🔧", callback_data=f"ultra_lang:cpp:stars:1"),
            InlineKeyboardButton("C# 🎮", callback_data=f"ultra_lang:csharp:stars:1")
        ],
        [
            InlineKeyboardButton("Ruby 💎", callback_data=f"ultra_lang:ruby:stars:1"),
            InlineKeyboardButton("PHP 🌐", callback_data=f"ultra_lang:php:stars:1")
        ],
        [
            InlineKeyboardButton("TypeScript 📘", callback_data=f"ultra_lang:typescript:stars:1"),
            InlineKeyboardButton("Swift 🍎", callback_data=f"ultra_lang:swift:stars:1")
        ],
        [
            InlineKeyboardButton("همه زبان‌ها 🔍", callback_data=f"ultra_lang:any:stars:1")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت", callback_data="ultra_glass_search")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text=glass_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def show_ultra_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش راهنمای پیشرفته با طراحی شیشه‌ای خفن"""
    help_text = (
        "┏━━━━━━━━━━━━━━━ 💎 راه نمای شیشه‌ای 💎 ━━━━━━━━━━━━━━━┓\n\n"
        "*🔹 دستورات اصلی*\n"
        "• /start - شروع ربات با منوی شیشه‌ای\n"
        "• /ultra - نمایش منوی فوق‌پیشرفته\n"
        "• /help - نمایش این راهنما\n"
        "• /search - جستجوی مستقیم\n"
        "• /trend - نمایش ترندهای گیت‌هاب\n"
        "• /status - مشاهده آمار سیستم\n\n"
        
        "*🔹 قابلیت‌های پیشرفته*\n"
        "• *رابط سه‌بعدی* - طراحی شیشه‌ای و زیبا\n"
        "• *نوارهای پیشرفت* - نمایش گرافیکی با افکت‌های خاص\n"
        "• *فیلترهای چندگانه* - جستجو با ترکیب فیلترها\n"
        "• *تحلیل کد* - بررسی محتوا و عملکرد کدها\n"
        "• *دانلود هوشمند* - شناسایی بهترین منابع دانلود\n"
        "• *پیش‌نمایش کدها* - مشاهده خلاصه کدها قبل از دانلود\n\n"
        
        "*🔹 روش استفاده*\n"
        "1️⃣ یک کلمه کلیدی وارد کنید\n"
        "2️⃣ زبان برنامه‌نویسی را انتخاب کنید\n"
        "3️⃣ از میان نتایج، ریپازیتوری مورد نظر را بیابید\n"
        "4️⃣ از گزینه‌های مختلف برای مشاهده جزئیات یا دانلود استفاده کنید\n\n"
        
        "*🔹 ترفندهای مخفی*\n"
        "• استفاده از فیلتر `stars:>1000` برای یافتن پروژه‌های محبوب\n"
        "• ترکیب چند کلمه کلیدی با استفاده از `+`\n"
        "• استفاده از `language:python framework:django` برای جستجوی دقیق\n"
        "• جستجوی کد با دستور `/code [عبارت]`\n"
        "• فشردن دکمه‌های دوبل برای دسترسی به منوهای مخفی\n\n"
        
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "🔹 *نسخه:* 3.0.0 Ultra Edition\n\n"
        "🧑‍💻 توسعه‌دهنده: Hamid Yarali"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 آموزش تصویری", callback_data="video_tutorial"),
            InlineKeyboardButton("📋 دستورات پیشرفته", callback_data="advanced_commands")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_start")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if update.message:
            await update.message.reply_text(help_text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.edit_message_text(help_text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in show_ultra_help: {e}")

def main() -> None:
    """راه‌اندازی و اجرای ربات نسخه شیشه‌ای"""
    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("ultra", start))
        application.add_handler(CommandHandler("help", show_help))
        application.add_handler(CommandHandler("ultrahelp", show_ultra_help))
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CommandHandler("trend", show_trending))
        application.add_handler(CommandHandler("status", send_status))
        
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_language))
        
        application.add_handler(CallbackQueryHandler(button_handler))

        glass_banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ✨🔮 ربات جستجوی گیت‌هاب - نسخه فوق‌پیشرفته 🔮✨  ║
║                                                          ║
║  💎 رابط کاربری سه‌بعدی | 📊 افکت‌های پیشرفته شیشه‌ای      ║
║  🚀 دانلود سورس کد سریع | 🎨 طراحی فوق‌العاده خفن         ║
║  🌟 جستجوی هوشمند | 👑 انیمیشن‌های فوق پیشرفته           ║
║                                                          ║
║             Hamid Yarali 🤖 v3.0.0 ULTRA            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """
        print(glass_banner)
        print("🚀✨🔮 ربات نسخه فوق‌پیشرفته ULTRA با موفقیت راه‌اندازی شد... 🔮✨🚀")
        logger.info("Bot started successfully - Version 3.0.0 ULTRA  Edition")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.critical(f"Critical error in main function: {e}")
        print(f"❌ خطای بحرانی: {e}")

if __name__ == '__main__':
    main()