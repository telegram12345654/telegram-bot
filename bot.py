import json
import os
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.getenv("8997264875:AAG9-uAs52ftFWeaIcFf3IiBNOnyqRChctI", "")

# Username کانالت
CHANNEL_ID = "@Omnitrix_Network"

# بعداً ID عددی خودت را اینجا قرار بده
ADMIN_ID = 8758607682

PROJECTS_FILE = "projects.json"


# ============================================================
# DEFAULT PROJECTS
# ============================================================

DEFAULT_PROJECTS = [
    {
        "name": "🟢 Ben 10 Classic",
        "url": "https://amynar.github.io/ben10-classic/"
    },
    {
        "name": "🛸 Omnitrix Alien Force",
        "url": "https://amynar.github.io/OMNITRIX-ALIEN-FORCE/"
    },
    {
        "name": "⚡ Omnitrix Alien Core",
        "url": "https://amynar.github.io/OMNITRIX-ALIEN-CORE/"
    }
]


# ============================================================
# RUNTIME DATA
# ============================================================

drafts = {}


# ============================================================
# PROJECT STORAGE
# ============================================================

def load_projects():

    if not os.path.exists(PROJECTS_FILE):

        save_projects(DEFAULT_PROJECTS)

        return DEFAULT_PROJECTS.copy()

    try:

        with open(
            PROJECTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, list):

            raise ValueError("Invalid projects file")

        return data

    except Exception:

        save_projects(DEFAULT_PROJECTS)

        return DEFAULT_PROJECTS.copy()


def save_projects(data=None):

    if data is None:
        data = projects

    with open(
        PROJECTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


projects = load_projects()


# ============================================================
# SECURITY
# ============================================================

def is_admin(user_id: int) -> bool:

    return user_id == ADMIN_ID


# ============================================================
# HELPERS
# ============================================================

def valid_url(url: str) -> bool:

    url = url.strip()

    return (
        url.startswith("https://")
        or url.startswith("http://")
        or url.startswith("tg://")
    )


def project_button(project):

    return InlineKeyboardButton(
        text=project["name"],
        url=project["url"]
    )


def back_button(callback="main_menu"):

    return InlineKeyboardButton(
        "🔙 بازگشت",
        callback_data=callback
    )


# ============================================================
# MAIN MENU
# ============================================================

async def show_main_menu(update: Update):

    keyboard = [
        [
            InlineKeyboardButton(
                "📝 ساخت پست",
                callback_data="new_post"
            )
        ],
        [
            InlineKeyboardButton(
                "📂 مدیریت پروژه‌ها",
                callback_data="projects_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 لیست پروژه‌ها",
                callback_data="project_preview"
            )
        ]
    ]

    markup = InlineKeyboardMarkup(keyboard)

    text = (
        "🟢 OMNITRIX NETWORK\n\n"
        "⚙️ پنل مدیریت\n\n"
        f"📂 تعداد پروژه‌ها: {len(projects)}\n\n"
        "یکی از گزینه‌ها را انتخاب کن:"
    )

    if update.callback_query:

        await update.callback_query.edit_message_text(
            text,
            reply_markup=markup
        )

    else:

        await update.message.reply_text(
            text,
            reply_markup=markup
        )


# ============================================================
# /START
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "⛔ Access Denied\n\n"
            "شما اجازه دسترسی به پنل مدیریت را ندارید."
        )

        return

    context.user_data.clear()

    await show_main_menu(update)


# ============================================================
# /ID
# ============================================================

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🆔 Telegram ID شما:\n\n"
        f"{update.effective_user.id}"
    )


# ============================================================
# PROJECT MANAGEMENT MENU
# ============================================================

async def projects_menu(query):

    keyboard = [

        [
            InlineKeyboardButton(
                "➕ افزودن پروژه",
                callback_data="project_add"
            )
        ],

        [
            InlineKeyboardButton(
                "✏️ ویرایش پروژه",
                callback_data="project_edit"
            )
        ],

        [
            InlineKeyboardButton(
                "🗑️ حذف پروژه",
                callback_data="project_delete"
            )
        ],

        [
            InlineKeyboardButton(
                "🔀 مرتب‌سازی پروژه‌ها",
                callback_data="project_reorder"
            )
        ],

        [
            InlineKeyboardButton(
                "👀 مشاهده پروژه‌ها",
                callback_data="project_preview"
            )
        ],

        [
            back_button("main_menu")
        ]
    ]

    await query.edit_message_text(
        "📂 مدیریت پروژه‌ها\n\n"
        f"تعداد پروژه‌ها: {len(projects)}\n\n"
        "از این قسمت می‌توانی پروژه‌ها را "
        "اضافه، ویرایش، حذف و مرتب کنی.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# PROJECT PREVIEW
# ============================================================

async def project_preview(query):

    keyboard = []

    for project in projects:

        keyboard.append([
            project_button(project)
        ])

    keyboard.append([
        back_button("projects_menu")
    ])

    await query.edit_message_text(
        "📂 پروژه‌های ذخیره‌شده\n\n"
        "هر پروژه‌ای که اینجا می‌بینی، "
        "می‌تواند مستقیماً به عنوان دکمه "
        "شیشه‌ای داخل پست استفاده شود.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# ADD PROJECT
# ============================================================

async def project_add(query, context):

    context.user_data.clear()

    context.user_data["state"] = "project_add_name"

    await query.edit_message_text(
        "➕ افزودن پروژه\n\n"
        "مرحله 1 از 2\n\n"
        "اسم پروژه را بفرست.\n\n"
        "مثال:\n"
        "🧬 Omnitrix Ultimate"
    )


# ============================================================
# EDIT PROJECT LIST
# ============================================================

async def project_edit_list(query):

    keyboard = []

    for index, project in enumerate(projects):

        keyboard.append([
            InlineKeyboardButton(
                f"✏️ {project['name']}",
                callback_data=f"edit_project:{index}"
            )
        ])

    keyboard.append([
        back_button("projects_menu")
    ])

    await query.edit_message_text(
        "✏️ انتخاب پروژه برای ویرایش:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# EDIT PROJECT MENU
# ============================================================

async def project_edit_menu(query, index):

    project = projects[index]

    keyboard = [

        [
            InlineKeyboardButton(
                "🏷️ تغییر نام",
                callback_data=f"edit_name:{index}"
            )
        ],

        [
            InlineKeyboardButton(
                "🔗 تغییر لینک",
                callback_data=f"edit_url:{index}"
            )
        ],

        [
            InlineKeyboardButton(
                "🔙 بازگشت",
                callback_data="project_edit"
            )
        ]
    ]

    await query.edit_message_text(
        "✏️ ویرایش پروژه\n\n"
        f"🏷️ نام فعلی:\n{project['name']}\n\n"
        f"🔗 لینک فعلی:\n{project['url']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# DELETE PROJECT LIST
# ============================================================

async def project_delete_list(query):

    keyboard = []

    for index, project in enumerate(projects):

        keyboard.append([
            InlineKeyboardButton(
                f"🗑️ {project['name']}",
                callback_data=f"delete_project:{index}"
            )
        ])

    keyboard.append([
        back_button("projects_menu")
    ])

    await query.edit_message_text(
        "🗑️ پروژه‌ای که می‌خواهی حذف کنی را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# DELETE CONFIRMATION
# ============================================================

async def delete_confirmation(query, index):

    project = projects[index]

    keyboard = [

        [
            InlineKeyboardButton(
                "✅ بله، حذف کن",
                callback_data=f"confirm_delete:{index}"
            )
        ],

        [
            InlineKeyboardButton(
                "❌ لغو",
                callback_data="project_delete"
            )
        ]
    ]

    await query.edit_message_text(
        "⚠️ حذف پروژه\n\n"
        f"{project['name']}\n\n"
        "آیا مطمئنی می‌خواهی این پروژه حذف شود؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# REORDER PROJECTS
# ============================================================

async def project_reorder_list(query):

    keyboard = []

    for index, project in enumerate(projects):

        keyboard.append([
            InlineKeyboardButton(
                f"{index + 1}. {project['name']}",
                callback_data=f"reorder_select:{index}"
            )
        ])

    keyboard.append([
        back_button("projects_menu")
    ])

    await query.edit_message_text(
        "🔀 مرتب‌سازی پروژه‌ها\n\n"
        "پروژه را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def project_reorder_controls(query, index):

    project = projects[index]

    keyboard = []

    if index > 0:

        keyboard.append([
            InlineKeyboardButton(
                "⬆️ انتقال به بالا",
                callback_data=f"move_up:{index}"
            )
        ])

    if index < len(projects) - 1:

        keyboard.append([
            InlineKeyboardButton(
                "⬇️ انتقال به پایین",
                callback_data=f"move_down:{index}"
            )
        ])

    keyboard.append([
        back_button("project_reorder")
    ])

    await query.edit_message_text(
        "🔀 مرتب‌سازی\n\n"
        f"پروژه:\n{project['name']}\n\n"
        f"جایگاه فعلی: {index + 1}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# NEW POST
# ============================================================

async def new_post(query, context):

    user_id = query.from_user.id

    drafts[user_id] = {
        "text": "",
        "buttons": []
    }

    context.user_data.clear()

    context.user_data["state"] = "post_text"

    await query.edit_message_text(
        "📝 ساخت پست\n\n"
        "متن پست را بفرست."
    )


# ============================================================
# POST MENU
# ============================================================

async def post_menu(query, user_id):

    draft = drafts.get(user_id)

    if not draft:

        await query.edit_message_text(
            "❌ Draft پیدا نشد."
        )

        return

    button_count = len(draft["buttons"])

    keyboard = [

        [
            InlineKeyboardButton(
                "📂 افزودن پروژه",
                callback_data="post_add_project"
            )
        ],

        [
            InlineKeyboardButton(
                "🔗 افزودن دکمه سفارشی",
                callback_data="post_add_custom"
            )
        ],

        [
            InlineKeyboardButton(
                f"🔘 مدیریت دکمه‌ها ({button_count})",
                callback_data="post_manage_buttons"
            )
        ],

        [
            InlineKeyboardButton(
                "👀 پیش‌نمایش",
                callback_data="post_preview"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 انتشار در کانال",
                callback_data="post_publish"
            )
        ],

        [
            InlineKeyboardButton(
                "❌ لغو پست",
                callback_data="post_cancel"
            )
        ]
    ]

    await query.edit_message_text(
        "📝 مدیریت پست\n\n"
        f"متن:\n{draft['text'][:500]}\n\n"
        f"🔘 تعداد دکمه‌ها: {button_count}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# ADD PROJECT TO POST
# ============================================================

async def post_add_project_menu(query):

    if not projects:

        await query.edit_message_text(
            "❌ هنوز پروژه‌ای وجود ندارد.\n\n"
            "اول از مدیریت پروژه‌ها یک پروژه اضافه کن.",
            reply_markup=InlineKeyboardMarkup([
                [back_button("post_menu")]
            ])
        )

        return

    keyboard = []

    for index, project in enumerate(projects):

        keyboard.append([
            InlineKeyboardButton(
                f"➕ {project['name']}",
                callback_data=f"post_project:{index}"
            )
        ])

    keyboard.append([
        back_button("post_menu")
    ])

    await query.edit_message_text(
        "📂 افزودن پروژه به پست\n\n"
        "پروژه موردنظر را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# CUSTOM BUTTON
# ============================================================

async def post_add_custom(query, context):

    context.user_data["state"] = "custom_button_name"

    await query.edit_message_text(
        "🔗 دکمه سفارشی\n\n"
        "نام دکمه را بفرست.\n\n"
        "مثال:\n"
        "🌐 Website"
    )


# ============================================================
# MANAGE POST BUTTONS
# ============================================================

async def post_manage_buttons(query, user_id):

    draft = drafts.get(user_id)

    if not draft:

        return

    keyboard = []

    for index, button in enumerate(draft["buttons"]):

        keyboard.append([
            InlineKeyboardButton(
                f"🗑️ {button['name']}",
                callback_data=f"remove_post_button:{index}"
            )
        ])

    keyboard.append([
        back_button("post_menu")
    ])

    if not draft["buttons"]:

        text = (
            "🔘 مدیریت دکمه‌ها\n\n"
            "هنوز هیچ دکمه‌ای اضافه نشده."
        )

    else:

        text = (
            "🔘 مدیریت دکمه‌های پست\n\n"
            "برای حذف یک دکمه روی آن بزن:"
        )

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# PREVIEW POST
# ============================================================

async def post_preview(query, user_id):

    draft = drafts.get(user_id)

    if not draft:

        await query.edit_message_text(
            "❌ Draft پیدا نشد."
        )

        return

    keyboard = []

    for button in draft["buttons"]:

        keyboard.append([
            InlineKeyboardButton(
                button["name"],
                url=button["url"]
            )
        ])

    keyboard.extend([
        [
            InlineKeyboardButton(
                "✏️ ویرایش",
                callback_data="post_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 انتشار",
                callback_data="post_publish"
            )
        ]
    ])

    await query.edit_message_text(
        "👀 پیش‌نمایش پست\n\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{draft['text']}\n\n"
        "━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# PUBLISH POST
# ============================================================

async def publish_post(query, context):

    user_id = query.from_user.id

    draft = drafts.get(user_id)

    if not draft:

        await query.edit_message_text(
            "❌ پستی برای انتشار وجود ندارد."
        )

        return

    if not draft["text"].strip():

        await query.answer(
            "پست نمی‌تواند بدون متن باشد.",
            show_alert=True
        )

        return

    keyboard = []

    for button in draft["buttons"]:

        keyboard.append([
            InlineKeyboardButton(
                button["name"],
                url=button["url"]
            )
        ])

    markup = (
        InlineKeyboardMarkup(keyboard)
        if keyboard
        else None
    )

    try:

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=draft["text"],
            reply_markup=markup
        )

    except Exception as error:

        await query.edit_message_text(
            "❌ انتشار ناموفق بود.\n\n"
            "احتمالاً ربات دسترسی لازم برای ارسال پیام "
            "در کانال را ندارد.\n\n"
            f"Error:\n{error}"
        )

        return

    drafts.pop(user_id, None)
    context.user_data.clear()

    await query.edit_message_text(
        "🎉 پست با موفقیت منتشر شد!\n\n"
        "📢 کانال:\n"
        f"{CHANNEL_ID}"
    )


# ============================================================
# CALLBACK HANDLER
# ============================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if not is_admin(user_id):

        await query.answer(
            "⛔ Access Denied",
            show_alert=True
        )

        return

    data = query.data

    # --------------------------------------------------------
    # MAIN
    # --------------------------------------------------------

    if data == "main_menu":

        context.user_data.clear()

        await show_main_menu(update)

        return

    # --------------------------------------------------------
    # PROJECT MENU
    # --------------------------------------------------------

    if data == "projects_menu":

        await projects_menu(query)

        return

    # --------------------------------------------------------
    # PROJECT PREVIEW
    # --------------------------------------------------------

    if data == "project_preview":

        await project_preview(query)

        return

    # --------------------------------------------------------
    # ADD PROJECT
    # --------------------------------------------------------

    if data == "project_add":

        await project_add(query, context)

        return

    # --------------------------------------------------------
    # EDIT PROJECT
    # --------------------------------------------------------

    if data == "project_edit":

        await project_edit_list(query)

        return

    # --------------------------------------------------------
    # EDIT PROJECT
    # --------------------------------------------------------

    if data.startswith("edit_project:"):

        index = int(data.split(":")[1])

        if index >= len(projects):

            await query.edit_message_text(
                "❌ پروژه پیدا نشد."
            )

            return

        await project_edit_menu(query, index)

        return

    # --------------------------------------------------------
    # EDIT NAME
    # --------------------------------------------------------

    if data.startswith("edit_name:"):

        index = int(data.split(":")[1])

        context.user_data["state"] = "edit_project_name"
        context.user_data["edit_index"] = index

        await query.edit_message_text(
            "🏷️ نام جدید پروژه را بفرست."
        )

        return

    # --------------------------------------------------------
    # EDIT URL
    # --------------------------------------------------------

    if data.startswith("edit_url:"):

        index = int(data.split(":")[1])

        context.user_data["state"] = "edit_project_url"
        context.user_data["edit_index"] = index

        await query.edit_message_text(
            "🔗 لینک جدید پروژه را بفرست."
        )

        return

    # --------------------------------------------------------
    # DELETE PROJECT
    # --------------------------------------------------------

    if data == "project_delete":

        await project_delete_list(query)

        return

    # --------------------------------------------------------
    # DELETE CONFIRM
    # --------------------------------------------------------

    if data.startswith("delete_project:"):

        index = int(data.split(":")[1])

        await delete_confirmation(query, index)

        return

    # --------------------------------------------------------
    # CONFIRM DELETE
    # --------------------------------------------------------

    if data.startswith("confirm_delete:"):

        index = int(data.split(":")[1])

        if index >= len(projects):

            await query.edit_message_text(
                "❌ پروژه پیدا نشد."
            )

            return

        deleted = projects.pop(index)

        save_projects()

        await query.edit_message_text(
            "✅ پروژه حذف شد.\n\n"
            f"{deleted['name']}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📂 مدیریت پروژه‌ها",
                        callback_data="projects_menu"
                    )
                ]
            ])
        )

        return

    # --------------------------------------------------------
    # REORDER
    # --------------------------------------------------------

    if data == "project_reorder":

        await project_reorder_list(query)

        return

    if data.startswith("reorder_select:"):

        index = int(data.split(":")[1])

        await project_reorder_controls(
            query,
            index
        )

        return

    # --------------------------------------------------------
    # MOVE UP
    # --------------------------------------------------------

    if data.startswith("move_up:"):

        index = int(data.split(":")[1])

        if index > 0:

            projects[index - 1], projects[index] = (
                projects[index],
                projects[index - 1]
            )

            save_projects()

        await project_reorder_list(query)

        return

    # --------------------------------------------------------
    # MOVE DOWN
    # --------------------------------------------------------

    if data.startswith("move_down:"):

        index = int(data.split(":")[1])

        if index < len(projects) - 1:

            projects[index + 1], projects[index] = (
                projects[index],
                projects[index + 1]
            )

            save_projects()

        await project_reorder_list(query)

        return

    # --------------------------------------------------------
    # NEW POST
    # --------------------------------------------------------

    if data == "new_post":

        await new_post(query, context)

        return

    # --------------------------------------------------------
    # POST MENU
    # --------------------------------------------------------

    if data == "post_menu":

        await post_menu(
            query,
            user_id
        )

        return

    # --------------------------------------------------------
    # ADD PROJECT TO POST
    # --------------------------------------------------------

    if data == "post_add_project":

        await post_add_project_menu(query)

        return

    # --------------------------------------------------------
    # PROJECT SELECTED FOR POST
    # --------------------------------------------------------

    if data.startswith("post_project:"):

        index = int(data.split(":")[1])

        if index >= len(projects):

            await query.answer(
                "❌ پروژه پیدا نشد.",
                show_alert=True
            )

            return

        project = projects[index]

        draft = drafts.get(user_id)

        if not draft:

            return

        draft["buttons"].append({
            "name": project["name"],
            "url": project["url"]
        })

        await query.answer(
            "✅ پروژه به پست اضافه شد."
        )

        await post_menu(
            query,
            user_id
        )

        return

    # --------------------------------------------------------
    # CUSTOM BUTTON
    # --------------------------------------------------------

    if data == "post_add_custom":

        await post_add_custom(
            query,
            context
        )

        return

    # --------------------------------------------------------
    # MANAGE POST BUTTONS
    # --------------------------------------------------------

    if data == "post_manage_buttons":

        await post_manage_buttons(
            query,
            user_id
        )

        return

    # --------------------------------------------------------
    # REMOVE POST BUTTON
    # --------------------------------------------------------

    if data.startswith("remove_post_button:"):

        index = int(data.split(":")[1])

        draft = drafts.get(user_id)

        if draft and 0 <= index < len(draft["buttons"]):

            removed = draft["buttons"].pop(index)

            await query.answer(
                f"🗑️ {removed['name']} حذف شد."
            )

        await post_manage_buttons(
            query,
            user_id
        )

        return

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    if data == "post_preview":

        await post_preview(
            query,
            user_id
        )

        return

    # --------------------------------------------------------
    # PUBLISH
    # --------------------------------------------------------

    if data == "post_publish":

        await publish_post(
            query,
            context
        )

        return

    # --------------------------------------------------------
    # CANCEL POST
    # --------------------------------------------------------

    if data == "post_cancel":

        drafts.pop(user_id, None)
        context.user_data.clear()

        await query.edit_message_text(
            "❌ پست لغو شد.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏠 منوی اصلی",
                        callback_data="main_menu"
                    )
                ]
            ])
        )

        return


# ============================================================
# MESSAGE HANDLER
# ============================================================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if not is_admin(user_id):

        return

    state = context.user_data.get("state")

    # ========================================================
    # ADD PROJECT - NAME
    # ========================================================

    if state == "project_add_name":

        name = update.message.text.strip()

        if not name:

            await update.message.reply_text(
                "❌ اسم پروژه نمی‌تواند خالی باشد."
            )

            return

        context.user_data["project_name"] = name
        context.user_data["state"] = "project_add_url"

        await update.message.reply_text(
            "🔗 مرحله 2 از 2\n\n"
            "لینک پروژه را بفرست.\n\n"
            "مثال:\n"
            "https://example.com"
        )

        return

    # ========================================================
    # ADD PROJECT - URL
    # ========================================================

    if state == "project_add_url":

        url = update.message.text.strip()

        if not valid_url(url):

            await update.message.reply_text(
                "❌ لینک معتبر نیست.\n\n"
                "لینک باید با https:// یا http:// شروع شود."
            )

            return

        name = context.user_data["project_name"]

        projects.append({
            "name": name,
            "url": url
        })

        save_projects()

        context.user_data.clear()

        await update.message.reply_text(
            "🎉 پروژه با موفقیت اضافه شد!\n\n"
            f"🏷️ {name}\n"
            f"🔗 {url}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📂 مدیریت پروژه‌ها",
                        callback_data="projects_menu"
                    )
                ]
            ])
        )

        return

    # ========================================================
    # EDIT PROJECT NAME
    # ========================================================

    if state == "edit_project_name":

        index = context.user_data.get("edit_index")

        if index is None or index >= len(projects):

            context.user_data.clear()

            await update.message.reply_text(
                "❌ پروژه پیدا نشد."
            )

            return

        new_name = update.message.text.strip()

        if not new_name:

            await update.message.reply_text(
                "❌ نام نمی‌تواند خالی باشد."
            )

            return

        projects[index]["name"] = new_name

        save_projects()

        context.user_data.clear()

        await update.message.reply_text(
            "✅ نام پروژه تغییر کرد.\n\n"
            f"🏷️ {new_name}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📂 مدیریت پروژه‌ها",
                        callback_data="projects_menu"
                    )
                ]
            ])
        )

        return

    # ========================================================
    # EDIT PROJECT URL
    # ========================================================

    if state == "edit_project_url":

        index = context.user_data.get("edit_index")

        if index is None or index >= len(projects):

            context.user_data.clear()

            await update.message.reply_text(
                "❌ پروژه پیدا نشد."
            )

            return

        new_url = update.message.text.strip()

        if not valid_url(new_url):

            await update.message.reply_text(
                "❌ لینک معتبر نیست."
            )

            return

        projects[index]["url"] = new_url

        save_projects()

        context.user_data.clear()

        await update.message.reply_text(
            "✅ لینک پروژه تغییر کرد.\n\n"
            f"🔗 {new_url}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📂 مدیریت پروژه‌ها",
                        callback_data="projects_menu"
                    )
                ]
            ])
        )

        return

    # ========================================================
    # POST TEXT
    # ========================================================

    if state == "post_text":

        text = update.message.text.strip()

        if not text:

            await update.message.reply_text(
                "❌ متن پست نمی‌تواند خالی باشد."
            )

            return

        drafts[user_id]["text"] = text

        context.user_data.clear()

        await update.message.reply_text(
            "✅ متن پست ذخیره شد."
        )

        # Send post menu separately
        fake_query = None

        keyboard = [

            [
                InlineKeyboardButton(
                    "📂 افزودن پروژه",
                    callback_data="post_add_project"
                )
            ],

            [
                InlineKeyboardButton(
                    "🔗 دکمه سفارشی",
                    callback_data="post_add_custom"
                )
            ],

            [
                InlineKeyboardButton(
                    "🔘 مدیریت دکمه‌ها",
                    callback_data="post_manage_buttons"
                )
            ],

            [
                InlineKeyboardButton(
                    "👀 پیش‌نمایش",
                    callback_data="post_preview"
                )
            ],

            [
                InlineKeyboardButton(
                    "📢 انتشار",
                    callback_data="post_publish"
                )
            ],

            [
                InlineKeyboardButton(
                    "❌ لغو",
                    callback_data="post_cancel"
                )
            ]
        ]

        await update.message.reply_text(
            "📝 پست آماده ویرایش است:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # ========================================================
    # CUSTOM BUTTON NAME
    # ========================================================

    if state == "custom_button_name":

        name = update.message.text.strip()

        if not name:

            await update.message.reply_text(
                "❌ نام دکمه نمی‌تواند خالی باشد."
            )

            return

        context.user_data["custom_button_name"] = name
        context.user_data["state"] = "custom_button_url"

        await update.message.reply_text(
            "🔗 حالا لینک دکمه را بفرست."
        )

        return

    # ========================================================
    # CUSTOM BUTTON URL
    # ========================================================

    if state == "custom_button_url":

        url = update.message.text.strip()

        if not valid_url(url):

            await update.message.reply_text(
                "❌ لینک معتبر نیست."
            )

            return

        name = context.user_data["custom_button_name"]

        drafts[user_id]["buttons"].append({
            "name": name,
            "url": url
        })

        context.user_data.clear()

        await update.message.reply_text(
            "✅ دکمه اضافه شد!\n\n"
            f"🔘 {name}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ افزودن پروژه",
                    callback_data="post_add_project"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔗 دکمه سفارشی",
                    callback_data="post_add_custom"
                )
            ],
            [
                InlineKeyboardButton(
                    "👀 پیش‌نمایش",
                    callback_data="post_preview"
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 انتشار",
                    callback_data="post_publish"
                )
            ]
        ]

        await update.message.reply_text(
            "📝 ادامه مدیریت پست:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "ERROR:",
        context.error
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not BOT_TOKEN:

        print(
            "❌ BOT_TOKEN در Environment Variables تنظیم نشده است."
        )

        return

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "id",
            get_id
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    app.add_error_handler(
        error_handler
    )

    print(
        "🟢 OMNITRIX NETWORK BOT IS RUNNING..."
    )

    print(
        f"📂 Projects loaded: {len(projects)}"
    )

    app.run_polling()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()