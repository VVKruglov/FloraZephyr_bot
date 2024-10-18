# import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes



# Логирование
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)


# Каталог товаров
catalog = {
    "Сладкая осень": [
        {"name": "Ежики и грибочки с варенной сгущенкой", "price": 400, "image": "img/eg.jpg"},
        {"name": "Тыковки и мухоморчики с варенной сгущенкой", "price": 400, "image": "img/tm.jpg"},
        {"name": "Грибочки с варенной сгущенкой", "price": 400, "image": "img/gr.jpg"}
    ],
    "Зефирные цветы": [
        {"name": "Нежные лепестки", "price": 700, "image": "img/nl.jpg"},
        {"name": "Голубые гортензии", "price": 800, "image": "img/gg.jpg"},
        {"name": "Корзина с цветами", "price": 2000, "image": "img/kf.jpg"},
        {"name": "Сладкий комплимент", "price": 600, "image": "img/sk.jpg"},
        {"name": "Розовый ранункулюс", "price": 800, "image": "img/rr.jpg"},
        {"name": "Воздушная роза", "price": 700, "image": "img/vr.jpg"}
    ]
}


# Каталог акций
promotions = [
    {"name": "Скидка на первый заказ!", "image": "img/a.jpg", "description": "Скидка 20% на первый заказ"},
    {"name": "Скидка на заказ от трех композиций!", "image": "img/a.jpg", "description": "Скидка 25% на заказ от трех композиций"},
    {"name": "Xэллоуин", "image": "img/a.jpg", "description": "Скидка 30% на любую композицию с 15 по 31 октября"}
]


# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Добро пожаловать в ФлораЗефир!\n' 
                                     'Здесь ты можешь узнать информацию о ценах, доставке, составе.' 
                                     'Достаточно написать соответствующие слова.\n' 
                                     'Нажми /catalog для просмотра товаров.\n'
                                     'Нажми /promotion, чтобы узнать о наших акциях')


# Отображение каталога с выбором разделов
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sections = list(catalog.keys())  # Получаем названия разделов каталога
    keyboard = [[InlineKeyboardButton(section, callback_data=f"section_{section}")] for section in sections]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите раздел каталога:', reply_markup=reply_markup)
    
    
# Обработка выбора раздела
async def section_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем название раздела из callback_data
    section_name = query.data.split('_')[1]
    context.user_data['current_section'] = section_name

    if section_name in catalog:
        items = catalog[section_name]
        keyboard = [[InlineKeyboardButton(item['name'], callback_data=str(index))] for index, item in enumerate(items)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"Выберите товар из раздела '{section_name}':", reply_markup=reply_markup)
    else:
        await query.message.reply_text("Раздел не найден.")
    
    
# Отображение акций
async def show_promotions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(item['name'], callback_data=f"promo_{index}")] for index, item in enumerate(promotions)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Текущие акции. Нажми, чтобы узнать подробнее:', reply_markup=reply_markup)


# Обработка выбора товара
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    # Получаем раздел каталога и индекс товара
    section_name = context.user_data.get('current_section')
    if not section_name:
        await query.message.reply_text("Раздел не выбран.")
        return

    items = catalog.get(section_name, [])
    item_index = int(query.data)
    
    if 0 <= item_index < len(items):
        item = items[item_index]
        print(f"Найден товар: {item['name']}")

        # Создаем кнопку "Заказать"
        keyboard = [[InlineKeyboardButton("Заказать", callback_data=f"order_{section_name}_{item_index}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            with open(item['image'], 'rb') as photo_file:
                await query.message.reply_photo(
                    photo=photo_file,
                    caption=f"Товар: {item['name']}\nЦена: {item['price']} руб.",
                    reply_markup=reply_markup
                )
        except FileNotFoundError:
            await query.message.reply_text(f"Изображение для товара {item['name']} не найдено.")
    else:
        await query.message.reply_text("Товар не найден.")
    
    
# Обработка выбора акционного товара
async def promotion_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем индекс акции из callback_data
    item_index = int(query.data.split('_')[1])

    if item_index >= 0 and item_index < len(promotions):
        promo = promotions[item_index]
        
        try:
            # Открываем и отправляем изображение акции
            with open(promo['image'], 'rb') as photo_file:
                await query.message.reply_photo(
                    photo=photo_file,
                    caption=f"{promo['name']}\n{promo['description']}",
                )
        except FileNotFoundError:
            await query.message.reply_text(f"Изображение для акции {promo['name']} не найдено.")
    else:
        await query.message.reply_text("Акция не найдена.")


# Обработка нажатия на кнопку "Заказать"
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем раздел и индекс товара из callback_data
    section_name, item_index = query.data.split('_')[1], int(query.data.split('_')[2])
    
    if section_name in catalog:
        item = catalog[section_name][item_index]

        # Сообщение для владельца о заказе
        owner_chat_id = '1238848716'
        order_message = (
            f"ID: {query.from_user.id}\n"
            f"Клиент: {query.from_user.username}\n"
            f"Имя: {query.from_user.first_name} {query.from_user.last_name}\n"
            f"Заказал: {item['name']}"
        )

        # Отправляем владельцу
        await context.bot.send_message(chat_id=owner_chat_id, text=order_message)

        # Подтверждение клиенту
        await query.message.reply_text(f"Ваш заказ на {item['name']} был отправлен! Мы свяжемся с вами.")
    else:
        await query.message.reply_text("Раздел не найден.")


# Обработка вопросов (например, доставка и цена)
async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    if 'цена' in text:
        await update.message.reply_text('Цены на наши товары начинаются от 400 руб. Подробнее нажмите /catalog')
    elif 'цену' in text:
        await update.message.reply_text('Цены на наши товары начинаются от 400 руб. Подробнее нажмите /catalog')
    elif 'стоимость' in text:
        await update.message.reply_text('Цены на наши товары начинаются от 400 руб. Подробнее нажмите /catalog')
    elif 'доставка' in text:
        await update.message.reply_text('Яндекс Go\n'
    'Этот вид доставки вы оплачиваете самостоятельно. В согласованное заранее время я сообщаю вам стоимость, '
    'которую рассчитало приложение до вашего адреса и отправляю ваш заказ. Вы оплачиваете стоимость доставки '
    'курьеру при получении.\n\n'
    'Самовывоз\n'
    'Забрать свой заказ вы можете по адресу: г. Саратов, Ленинский район (Солнечный), ул. Уфимцева д. 3')
    elif 'состав' in text:
        await update.message.reply_text('Состав: яичный белок, яблочный сок, сахар, агар-агар, пищевые красители')
    else:
        await update.message.reply_text('Я могу вам помочь узнать состав, цену и ответить на вопрос по доставке. Просто введите соответствующие слова')



# Запуск бота
def main():
    app = ApplicationBuilder().token('7529805135:AAEYl0ZJ054C7LJFPy-GSsg6nyJC5UXsHOQ').build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalog", show_catalog))
    app.add_handler(CommandHandler("promotion", show_promotions))
    app.add_handler(CallbackQueryHandler(section_button, pattern=r'^section_'))
    app.add_handler(CallbackQueryHandler(button, pattern=r'^\d+$'))
    app.add_handler(CallbackQueryHandler(order, pattern=r'^order_\d+$'))
    app.add_handler(CallbackQueryHandler(promotion_button, pattern=r'^promo_\d+$'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq))

    app.run_polling()

if __name__ == '__main__':
    main()

