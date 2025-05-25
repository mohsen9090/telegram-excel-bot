#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" ربات مدیریت Excel پیشرفته - قسمت دوم نسخه 2.0 
توسعه‌دهنده: ربات Excel Manager """
# ادامه از main1.py ============================ 
# حذف رکورد ============================
async def delete_start(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع حذف رکورد""" try: 
        ensure_excel_file() df = 
        pd.read_excel(EXCEL_FILE)
        
        if df.empty: await 
            update.message.reply_text("📭 هیچ 
            رکوردی برای حذف وجود ندارد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        msg = "🗑️ **شماره ردیف مورد نظر برای 
        حذف:**\n\n" for i, row in df.iterrows():
            name = clean_value(row.get('نام', 
            f'ردیف {i+1}')) family = 
            clean_value(row.get('نام خانوادگی', 
            '')) if family:
                name += f" {family}" msg += 
            f"{i+1}. {name}\n"
        
        await update.message.reply_text(msg) 
        return DELETE_ROW
    except Exception as e: logger.error(f"Error 
        in delete_start: {e}") await 
        update.message.reply_text("❌ خطا در 
        بارگذاری رکوردها.", 
        reply_markup=get_keyboard()) return 
        ConversationHandler.END
async def delete_confirm(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """تأیید و حذف رکورد""" try: row_num = 
        int(update.message.text) - 1 df = 
        pd.read_excel(EXCEL_FILE)
        
        if row_num < 0 or row_num >= len(df): 
            await update.message.reply_text("❌ 
            شماره ردیف نامعتبر است.") return 
            DELETE_ROW
        
        # نمایش اطلاعات رکورد قبل از حذف
        deleted_record = df.iloc[row_num] 
        record_info = f"🗑️ **رکورد حذف شده:**\n" 
        for col in df.columns:
            value = 
            clean_value(deleted_record[col]) if 
            value:
                record_info += f"• {col}: 
                {value}\n"
        
        df = 
        df.drop(row_num).reset_index(drop=True) 
        user_theme = 
        load_user_theme(update.effective_user.id)
        
        if create_excel(df, user_theme): await 
            update.message.reply_text(
                f"✅ **رکورد با موفقیت حذف 
                شد!**\n\n{record_info}", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} deleted a 
            record")
        else: raise Exception("Error creating 
            Excel file")
        
    except ValueError: await 
        update.message.reply_text("❌ لطفاً یک عدد 
        معتبر وارد کنید.") return DELETE_ROW
    except Exception as e: logger.error(f"Error 
        in delete_confirm: {e}") await 
        update.message.reply_text("❌ خطا در حذف 
        رکورد.", reply_markup=get_keyboard())
    
    return ConversationHandler.END
# ============================ جستجو 
# ============================
async def search_start(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع جستجو""" fields = load_fields() 
    keyboard = [[KeyboardButton(field)] for field 
    in fields] 
    keyboard.append([KeyboardButton("🔍 جستجو در 
    همه فیلدها")])
    
    await update.message.reply_text( "🔍 **جستجو 
        در کدام فیلد؟**", 
        reply_markup=ReplyKeyboardMarkup(keyboard, 
        resize_keyboard=True)
    ) return SEARCH_FIELD async def 
search_field_select(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """انتخاب فیلد جستجو""" field = 
    update.message.text fields = load_fields()
    
    if field == "🔍 جستجو در همه فیلدها": 
        context.user_data['search_field'] = "all" 
        await update.message.reply_text("🔍 
        **کلیدواژه جستجو را وارد کنید:**") return 
        SEARCH_VALUE
    elif field not in fields: await 
        update.message.reply_text("❌ فیلد 
        نامعتبر است.") return SEARCH_FIELD
    
    context.user_data['search_field'] = field 
    await update.message.reply_text(f"🔍 
    **کلیدواژه جستجو در فیلد '{field}':**") 
    return SEARCH_VALUE
async def search_process(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """پردازش جستجو""" try: keyword = 
        update.message.text.strip() field = 
        context.user_data['search_field']
        
        ensure_excel_file() df = 
        pd.read_excel(EXCEL_FILE)
        
        if df.empty: await 
            update.message.reply_text("📭 هیچ 
            رکوردی برای جستجو وجود ندارد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        # جستجو
        if field == "all":
            # جستجو در همه فیلدها
            mask = df.astype(str).apply(lambda x: 
            x.str.contains(keyword, case=False, 
            na=False)).any(axis=1) results = 
            df[mask]
        else:
            # جستجو در فیلد خاص
            results = 
            df[df[field].astype(str).str.contains(keyword, 
            case=False, na=False)]
        
        message = format_search_results(results, 
        keyword, MAX_SEARCH_RESULTS) await 
        update.message.reply_text(message, 
        reply_markup=get_keyboard())
        
        logger.info(f"User 
        {update.effective_user.id} searched for 
        '{keyword}'")
        
    except Exception as e: logger.error(f"Error 
        in search_process: {e}") await 
        update.message.reply_text("❌ خطا در 
        جستجو.", reply_markup=get_keyboard())
    
    return ConversationHandler.END
# ============================ مدیریت فیلدها 
# ============================
async def field_management_start(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """شروع مدیریت فیلدها""" fields = 
    load_fields()
    
    keyboard = [ [KeyboardButton("➕ اضافه کردن 
        فیلد"), KeyboardButton("🗑️ حذف فیلد")], 
        [KeyboardButton("📋 نمایش فیلدها"), 
        KeyboardButton("🔄 بازگشت به پیش‌فرض")], 
        [KeyboardButton("🏠 بازگشت به منوی 
        اصلی")]
    ]
    
    msg = f"⚙️ **مدیریت فیلدها**\n\n" msg += f"📊 
    تعداد فیلدهای فعلی: {len(fields)}\n" msg += 
    f"📋 فیلدهای موجود:\n" for i, field in 
    enumerate(fields, 1):
        msg += f" {i}. {field}\n"
    
    await update.message.reply_text( msg, 
        reply_markup=ReplyKeyboardMarkup(keyboard, 
        resize_keyboard=True)
    ) return FIELD_MANAGEMENT async def 
field_management_handle(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """مدیریت عملیات فیلدها""" text = 
    update.message.text
    
    if text == "➕ اضافه کردن فیلد": await 
        update.message.reply_text("📝 **نام فیلد 
        جدید را وارد کنید:**") return ADD_FIELD
    elif text == "🗑️ حذف فیلد": return await 
        delete_field_start(update, context)
    elif text == "📋 نمایش فیلدها": return await 
        show_fields(update, context)
    elif text == "🔄 بازگشت به پیش‌فرض": return 
        await reset_fields(update, context)
    elif text == "🏠 بازگشت به منوی اصلی": await 
        update.message.reply_text("🏠 بازگشت به 
        منوی اصلی", reply_markup=get_keyboard()) 
        return ConversationHandler.END
    else: await update.message.reply_text("❌ 
        گزینه نامعتبر") return FIELD_MANAGEMENT
async def add_field_process(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """اضافه کردن فیلد جدید""" try: new_field = 
        update.message.text.strip()
        
        if not new_field: await 
            update.message.reply_text("❌ نام 
            فیلد نمی‌تواند خالی باشد:") return 
            ADD_FIELD
        
        fields = load_fields()
        
        if new_field in fields: await 
            update.message.reply_text("❌ این 
            فیلد از قبل موجود است:") return 
            ADD_FIELD
        
        fields.append(new_field)
        
        if save_fields(fields):
            # اضافه کردن ستون جدید به فایل Excel 
            # موجود
            if os.path.exists(EXCEL_FILE) and 
            os.path.getsize(EXCEL_FILE) > 0:
                df = pd.read_excel(EXCEL_FILE) if 
                new_field not in df.columns:
                    df[new_field] = "" user_theme 
                    = 
                    load_user_theme(update.effective_user.id) 
                    create_excel(df, user_theme)
            
            await update.message.reply_text( f"✅ 
                **فیلد '{new_field}' با موفقیت 
                اضافه شد!**", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} added 
            field: {new_field}")
        else: await update.message.reply_text("❌ 
            خطا در ذخیره فیلد.", 
            reply_markup=get_keyboard())
        
    except Exception as e: logger.error(f"Error 
        adding field: {e}") await 
        update.message.reply_text("❌ خطا در 
        اضافه کردن فیلد.", 
        reply_markup=get_keyboard())
    
    return ConversationHandler.END async def 
delete_field_start(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """شروع حذف فیلد""" fields = load_fields()
    
    if len(fields) <= 1: await 
        update.message.reply_text("❌ نمی‌توان همه 
        فیلدها را حذف کرد. حداقل یک فیلد باید 
        باقی بماند.") return FIELD_MANAGEMENT
    
    keyboard = [[KeyboardButton(field)] for field 
    in fields] 
    keyboard.append([KeyboardButton("❌ لغو")])
    
    await update.message.reply_text( "🗑️ **کدام 
        فیلد حذف شود؟**\n⚠️ توجه: تمام داده‌های این 
        فیلد پاک خواهد شد!", 
        reply_markup=ReplyKeyboardMarkup(keyboard, 
        resize_keyboard=True)
    ) return DELETE_FIELD async def 
delete_field_process(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """حذف فیلد""" try: field_to_delete = 
        update.message.text
        
        if field_to_delete == "❌ لغو": await 
            update.message.reply_text("❌ حذف 
            فیلد لغو شد.", 
            reply_markup=get_keyboard()) return 
            ConversationHandler.END
        
        fields = load_fields()
        
        if field_to_delete not in fields: await 
            update.message.reply_text("❌ فیلد 
            نامعتبر است.") return DELETE_FIELD
        
        if len(fields) <= 1: await 
            update.message.reply_text("❌ نمی‌توان 
            آخرین فیلد را حذف کرد.") return 
            DELETE_FIELD
        
        fields.remove(field_to_delete)
        
        if save_fields(fields):
            # حذف ستون از فایل Excel
            if os.path.exists(EXCEL_FILE) and 
            os.path.getsize(EXCEL_FILE) > 0:
                df = pd.read_excel(EXCEL_FILE) if 
                field_to_delete in df.columns:
                    df = 
                    df.drop(columns=[field_to_delete]) 
                    user_theme = 
                    load_user_theme(update.effective_user.id) 
                    create_excel(df, user_theme)
            
            await update.message.reply_text( f"✅ 
                **فیلد '{field_to_delete}' با 
                موفقیت حذف شد!**", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} deleted 
            field: {field_to_delete}")
        else: await update.message.reply_text("❌ 
            خطا در حذف فیلد.", 
            reply_markup=get_keyboard())
        
    except Exception as e: logger.error(f"Error 
        deleting field: {e}") await 
        update.message.reply_text("❌ خطا در حذف 
        فیلد.", reply_markup=get_keyboard())
    
    return ConversationHandler.END async def 
show_fields(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """نمایش فیلدها""" fields = load_fields()
    
    msg = f"📋 **فیلدهای موجود ({len(fields)} 
    فیلد):**\n\n" for i, field in 
    enumerate(fields, 1):
        msg += f" {i}. {field}\n"
    
    await update.message.reply_text(msg) return 
    FIELD_MANAGEMENT
async def reset_fields(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """بازگشت به فیلدهای پیش‌فرض""" try: if 
        save_fields(DEFAULT_FIELDS):
            await update.message.reply_text( "🔄 
                **فیلدها به حالت پیش‌فرض بازگشت 
                داده شد!**\n" f"📊 
                {len(DEFAULT_FIELDS)} فیلد پیش‌فرض 
                بارگذاری شد.", 
                reply_markup=get_keyboard()
            ) logger.info(f"User 
            {update.effective_user.id} reset 
            fields to default")
        else: await update.message.reply_text("❌ 
            خطا در بازگشت به پیش‌فرض.", 
            reply_markup=get_keyboard())
        
    except Exception as e: logger.error(f"Error 
        resetting fields: {e}") await 
        update.message.reply_text("❌ خطا در 
        بازگشت به پیش‌فرض.", 
        reply_markup=get_keyboard())
    
    return ConversationHandler.END
# ============================ تغییر تم 
# ============================
async def change_theme(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """تغییر تم رنگی""" current_theme = 
    load_user_theme(update.effective_user.id)
    
    keyboard = [] for key, theme in 
    THEMES.items():
        status = "✅" if key == current_theme 
        else "" 
        keyboard.append([InlineKeyboardButton(f"{theme['name']} 
        {status}", 
        callback_data=f"theme_{key}")])
    
    await update.message.reply_text( f"🎨 
        **انتخاب تم رنگی**\n" f"🔘 تم فعلی: 
        {THEMES[current_theme]['name']}", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    ) async def theme_callback(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """پردازش انتخاب تم""" query = 
    update.callback_query await query.answer()
    
    if query.data.startswith("theme_"): theme = 
        query.data.replace("theme_", "") user_id 
        = query.from_user.id
        
        if save_user_theme(user_id, theme):
            # اعمال تم به فایل موجود
            if os.path.exists(EXCEL_FILE) and 
            os.path.getsize(EXCEL_FILE) > 0:
                df = pd.read_excel(EXCEL_FILE) 
                create_excel(df, theme)
            
            await query.edit_message_text( f"✅ 
                **تم {THEMES[theme]['name']} 
                اعمال شد!**\n" f"🎨 فایل Excel با 
                رنگ‌بندی جدید آماده است."
            ) logger.info(f"User {user_id} 
            changed theme to {theme}")
        else: await query.edit_message_text("❌ 
            خطا در تغییر تم.")
# ============================ آمار سیستم 
# ============================
async def show_stats(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """نمایش آمار سیستم""" try: 
        ensure_excel_file()
        
        # آمار فایل
        record_count = 0
        
        if os.path.exists(EXCEL_FILE) and 
        os.path.getsize(EXCEL_FILE) > 0:
            df = pd.read_excel(EXCEL_FILE) 
            record_count = len(df)
        
        # آمار فیلدها
        fields = load_fields() field_count = 
        len(fields)
        
        # آمار کاربر
        user_theme = 
        load_user_theme(update.effective_user.id)
        
        # حجم فایل
        size_str = 
        get_file_size_string(EXCEL_FILE)
        
        msg = f"""📊 **آمار سیستم** 📋 
**داده‌ها:**
  • تعداد رکوردها: {record_count:,} • تعداد 
  فیلدها: {field_count} • حجم فایل: {size_str}
🎨 **تنظیمات شما:** • تم فعلی: 
  {THEMES[user_theme]['name']}
⏰ **زمان:** • تاریخ: 
  {datetime.now().strftime('%Y/%m/%d')} • ساعت: 
  {datetime.now().strftime('%H:%M:%S')}
🤖 **سیستم:** • نسخه ربات: 2.0 • وضعیت: فعال 
  ✅"""
        
        await update.message.reply_text(msg)
        
    except Exception as e: logger.error(f"Error 
        showing stats: {e}") await 
        update.message.reply_text("❌ خطا در 
        نمایش آمار.")
# ============================ حذف همه رکوردها 
# ============================
async def confirm_delete_all(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """تأیید حذف همه رکوردها""" keyboard = [ 
        [KeyboardButton("⚠️ بله، همه را حذف کن"), 
        KeyboardButton("❌ لغو")]
    ]
    
    await update.message.reply_text( "⚠️ 
        **هشدار!**\n\n" "آیا مطمئن هستید که 
        می‌خواهید **همه رکوردها** را حذف کنید؟\n" 
        "🔥 این عمل قابل بازگشت نیست!\n\n" "لطفاً 
        انتخاب کنید:", 
        reply_markup=ReplyKeyboardMarkup(keyboard, 
        resize_keyboard=True)
    ) return CONFIRM_DELETE_ALL async def 
delete_all_process(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """پردازش حذف همه رکوردها""" text = 
    update.message.text
    
    if text == "⚠️ بله، همه را حذف کن": try:
            # حذف فایل Excel
            if os.path.exists(EXCEL_FILE): 
                os.remove(EXCEL_FILE)
            
            # ایجاد فایل خالی جدید
            ensure_excel_file()
            
            await update.message.reply_text( "✅ 
                **همه رکوردها با موفقیت حذف 
                شدند!**\n" "🗂️ فایل Excel جدید و 
                خالی ایجاد شد.", 
                reply_markup=get_keyboard()
            )
            
            logger.info(f"User 
            {update.effective_user.id} deleted 
            all records")
            
        except Exception as e: 
            logger.error(f"Error deleting all 
            records: {e}") await 
            update.message.reply_text(
                "❌ خطا در حذف رکوردها.", 
                reply_markup=get_keyboard()
            ) else: await 
        update.message.reply_text(
            "❌ **عملیات حذف لغو شد.**\n" "📊 
            رکوردهای شما محفوظ ماندند.", 
            reply_markup=get_keyboard()
        )
    
    return ConversationHandler.END
# ============================ راهنما 
# ============================
async def show_help(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """نمایش راهنما""" help_text = """ℹ️ **راهنمای 
    ربات Excel**
🔹 **عملیات اصلی:** • ➕ اضافه کردن: افزودن 
  رکورد جدید • 📋 نمایش همه: مشاهده تمام رکوردها 
  • ✏️ ویرایش: تغییر اطلاعات موجود • 🗑️ حذف: پاک 
  کردن رکورد خاص • 🔍 جستجو: پیدا کردن رکورد
🔹 **مدیریت:** • ⚙️ مدیریت فیلدها: اضافه/حذف 
  ستون‌ها • 🎨 تغییر تم: انتخاب رنگ‌بندی Excel • 📁 
  دریافت فایل: دانلود Excel
🔹 **اطلاعات:** • 📊 آمار: نمایش اطلاعات سیستم 
  • ℹ️ راهنما: این پیام
🔹 **نکات مهم:** • 🔢 فیلدهای عددی فقط عدد 
  می‌پذیرند • 🎨 تم‌های مختلف برای زیباسازی Excel • 
  💾 تمام تغییرات خودکار ذخیره می‌شود • 🔒 اطلاعات 
  شما امن نگهداری می‌شود
❓ برای سوالات بیشتر با پشتیبانی تماس بگیرید.""" 
    await update.message.reply_text(help_text)
# ============================ مدیریت پیام‌های 
# اصلی ============================
async def handle_main_menu(update: Update, 
context: ContextTypes.DEFAULT_TYPE):
    """مدیریت منوی اصلی""" text = 
    update.message.text
    
    if text == "➕ اضافه کردن": return await 
        add_record_start(update, context)
    elif text == "📋 نمایش همه": await 
        show_all_records(update, context)
    elif text == "📁 دریافت فایل": await 
        send_excel_file(update, context)
    elif text == "✏️ ویرایش": return await 
        edit_start(update, context)
    elif text == "🗑️ حذف": return await 
        delete_start(update, context)
    elif text == "🔍 جستجو": return await 
        search_start(update, context)
    elif text == "⚙️ مدیریت فیلدها": return await 
        field_management_start(update, context)
    elif text == "🎨 تغییر تم": await 
        change_theme(update, context)
    elif text == "📊 آمار": await 
        show_stats(update, context)
    elif text == "🧹 حذف همه": return await 
        confirm_delete_all(update, context)
    elif text == "ℹ️ راهنما": await 
        show_help(update, context)
    else: await update.message.reply_text( "❌ 
            گزینه نامعتبر است.\nلطفاً از منوی زیر 
            انتخاب کنید:", 
            reply_markup=get_keyboard()
        )
# ============================ لغو عملیات 
# ============================
async def cancel(update: Update, context: 
ContextTypes.DEFAULT_TYPE):
    """لغو عملیات در حال انجام""" await 
    update.message.reply_text(
        "❌ **عملیات لغو شد.**\n🏠 بازگشت به منوی 
        اصلی", reply_markup=get_keyboard()
    ) return ConversationHandler.END
# ============================ تابع اصلی 
# ============================
def main(): """تابع اصلی اجرای ربات""" print("🔧 
    در حال راه‌اندازی ربات...")
    
    # بررسی توکن
    if TOKEN == "YOUR_BOT_TOKEN_HERE": print("❌ 
        خطا: لطفاً توکن ربات را در فایل config.py 
        وارد کنید") print("📝 فایل config.py را 
        باز کرده و TOKEN را جایگزین کنید") return
    
    # ایجاد برنامه
    application = 
    ApplicationBuilder().token(TOKEN).build()
    
    # ConversationHandler برای اضافه کردن رکورد
    add_record_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^➕ 
        اضافه کردن$"), add_record_start)], 
        states={
            ADD_DATA: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            add_record_process)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای ویرایش رکورد
    edit_record_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^✏️ 
        ویرایش$"), edit_start)], states={
            EDIT_ROW: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, edit_row_select)], 
            EDIT_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            edit_field_select)], EDIT_VALUE: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, edit_value_apply)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای حذف رکورد
    delete_record_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^🗑️ 
        حذف$"), delete_start)], states={
            DELETE_ROW: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, delete_confirm)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای جستجو
    search_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^🔍 
        جستجو$"), search_start)], states={
            SEARCH_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            search_field_select)], SEARCH_VALUE: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, search_process)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای مدیریت فیلدها
    field_management_handler = 
    ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^⚙️ 
        مدیریت فیلدها$"), 
        field_management_start)], states={
            FIELD_MANAGEMENT: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            field_management_handle)], ADD_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            add_field_process)], DELETE_FIELD: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            delete_field_process)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # ConversationHandler برای حذف همه رکوردها
    delete_all_handler = ConversationHandler( 
        entry_points=[MessageHandler(filters.Regex("^🧹 
        حذف همه$"), confirm_delete_all)], 
        states={
            CONFIRM_DELETE_ALL: 
            [MessageHandler(filters.TEXT & 
            ~filters.COMMAND, 
            delete_all_process)],
        },
        fallbacks=[CommandHandler("cancel", 
        cancel), 
        MessageHandler(filters.Regex("^❌ لغو$"), 
        cancel)],
    )
    
    # اضافه کردن handlers
    application.add_handler(CommandHandler("start", 
    start)) 
    application.add_handler(CallbackQueryHandler(theme_callback)) 
    application.add_handler(add_record_handler) 
    application.add_handler(edit_record_handler) 
    application.add_handler(delete_record_handler) 
    application.add_handler(search_handler) 
    application.add_handler(field_management_handler) 
    application.add_handler(delete_all_handler) 
    application.add_handler(MessageHandler(filters.TEXT 
    & ~filters.COMMAND, handle_main_menu))
    
    # شروع ربات
    print("🤖 ربات Excel مدیریت کامل در حال 
    اجرا...") print("✅ همه عملکردها فعال است:") 
    print(" • اضافه/ویرایش/حذف رکورد") print(" • 
    جستجو پیشرفته") print(" • مدیریت فیلدها") 
    print(" • تم‌های رنگی") print(" • خروجی Excel 
    زیبا") print("📡 منتظر دریافت پیام...")
    
    logger.info("Bot started successfully")
    
    try: application.run_polling() except 
    KeyboardInterrupt:
        print("\n🛑 ربات توسط کاربر متوقف شد") 
        logger.info("Bot stopped by user")
    except Exception as e: print(f"❌ خطا در 
        اجرای ربات: {e}") logger.error(f"Bot 
        error: {e}")
if __name__ == "__main__":
    main()
