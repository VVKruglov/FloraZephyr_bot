# import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes



# Логирование
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)


# Каталог товаров
catalog = [
    {"name": "Сладкий комплимент", "price": 600, "image": "img/sk.jpg"},
    {"name": "Розовый ранункулюс", "price": 800, "image": "img/rr.jpg"},
    {"name": "Воздушная роза", "price": 700, "image": "img/vr.jpg"},
    {"name": "Нежные лепестки", "price": 700, "image": "img/nl.jpg"},
    {"name": "Голубые гортензии", "price": 800, "image": "img/gg.jpg"},
    {"name": "Корзина с цветами", "price": 2000, "image": "img/kf.jpg"},
]

# Каталог акций
promotions = [
    {"name": "Скидка на первый заказ!", "image": "img/a.jpg", "description": "Скидка 20% на первый заказ!"},
    {"name": "Скидка на заказ от трех композиций!", "image": "img/a.jpg", "description": "Скидка 25% на заказ от трех композиций!"},
    {"name": "В честь дня учителя", "image": "img/a.jpg", "description": "Скидка 30% на любую композицию с 1 по 5 октября"}
]
# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Добро пожаловать в ФлораЗефир!\n' 
                                     'Здесь ты можешь узнать информацию о ценах, доставке, составе.' 
                                     'Достаточно написать соответствующие слова.\n' 
                                     'Нажми /catalog для просмотра товаров.\n'
                                     'Нажми /promotion, чтобы узнать о наших акциях')

# Отображение каталога
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(item['name'], callback_data=str(index))] for index, item in enumerate(catalog)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите товар:', reply_markup=reply_markup)
    
# Отображение акций
async def show_promotions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(item['name'], callback_data=f"promo_{index}")] for index, item in enumerate(promotions)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Текущие акции. Нажми, чтобы узнать подробнее:', reply_markup=reply_markup)

# Обработка выбора товара
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
   # Проверяем, является ли callback_data числом (индекс товара)
    
    item_index = int(query.data)
    if item_index >= 0 and item_index < len(catalog):  # Проверяем, что индекс допустим
        item = catalog[item_index]
        print(f"Найден товар: {item['name']}")
        
        # Создаем кнопку "Заказать"
        keyboard = [[InlineKeyboardButton("Заказать", callback_data=f"order_{item_index}")]]
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
        print("Индекс товара за пределами каталога.")
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

    # Получаем индекс товара из callback_data
    item_index = int(query.data.split('_')[1])
    item = catalog[item_index]

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

# Обработка вопросов (например, доставка и цена)
async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    if 'цена' in text:
        await update.message.reply_text('Цены на наши товары начинаются от 600 руб. Подробнее нажмите /catalog')
    elif 'цену' in text:
        await update.message.reply_text('Цены на наши товары начинаются от 600 руб. Подробнее нажмите /catalog')
    elif 'стоимость' in text:
        await update.message.reply_text('Цены на наши товары начинаются от 600 руб. Подробнее нажмите /catalog')
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
    app.add_handler(CallbackQueryHandler(button, pattern=r'^\d+$'))
    app.add_handler(CallbackQueryHandler(order, pattern=r'^order_\d+$'))
    app.add_handler(CallbackQueryHandler(promotion_button, pattern=r'^promo_\d+$'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq))

    app.run_polling()

if __name__ == '__main__':
    main()

