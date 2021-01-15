import asyncio
import logging
import typing

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import callback_data, exceptions

from config import API_TOKEN, DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, admin_id
from db_module import DB_module
from poll_module import get_text_from, get_next_question 
from analysis_module import get_analysis


# Data base
DB = DB_module(DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT)


# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('messages_sender')

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

button_cb = callback_data.CallbackData('button', 'question_name', 'answer' )



def make_keyboard(question_name, answers):
    """ Возвращает клавиатуру """
    if not answers: return None
    
    keyboard = types.InlineKeyboardMarkup()
    row = []
    for answer in answers:
        row.append(types.InlineKeyboardButton(
            answer,
            callback_data=button_cb.new(
                                question_name = question_name,
                                answer = answer)))
    if len(row) == 10:
        keyboard.row(*row[:5])
        keyboard.row(*row[5:])
    else:
        for button in row: keyboard.row(button)
        
    return keyboard

def check_low_answers(user_id):
    answer = DB.get_answer(user_id = user_id)
    for name in ['loyalty', 'manager', 'delivery', 'cooking', 'dietetics']:
        if int(answer[name]) < 7: return True
    return False
    

@dp.message_handler(commands=['start'])
async def send_phone(message: types.Message):
    logging.info('start command from: %r', message.from_user.id) 
    
    DB.add_user(    message.from_user.id, 
                    message.from_user.first_name, 
                    message.from_user.last_name, 
                    message.from_user.username, 
                    message.from_user.language_code)
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, 
                                         resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Отправить телефон 📞', 
                                      request_contact=True))
    
    await message.answer(get_text_from('text_of_questions/authorization.txt'), 
                         reply_markup = keyboard)


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    logging.info('help command from: %r', message.from_user.id) 
    await message.answer(get_text_from('text_of_questions/help.txt'))

    

@dp.callback_query_handler(button_cb.filter(
    question_name=['start', 'loyalty', 'manager', 'delivery', 'cooking', 'dietetics']))
async def callback_vote_action(
    query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    
    # callback_data contains all info from callback data
    logging.info('Got this callback data: %r', callback_data) 
    
    await query.answer()  # don't forget to answer callback query as soon as possible
    callback_question = callback_data['question_name']
    callback_answer = callback_data['answer']
    
    DB.add_answer(user_id = query.from_user.id, 
                  question_name = callback_question, 
                  answer = callback_answer)
    
    question_name, text, answers = get_next_question(callback_question)
    keyboard = make_keyboard(question_name, answers)
    
    edited_text = query.message.text + '\n\nВаша оценка: ' + callback_answer

    await bot.edit_message_text(
        edited_text,
        query.from_user.id,
        query.message.message_id,
        reply_markup=None,
        )
    
    await bot.send_message(query.from_user.id, text, reply_markup = keyboard)
    
    if question_name == 'end':
        if check_low_answers(query.from_user.id):
            await bot.send_message( 
                query.from_user.id, 
                'Расскажите, почему вы поставили низкую оценку?')
        else:
            await bot.send_message( 
                query.from_user.id, 
                'Вы так-же можете оставить тут свой отзыв.')

@dp.message_handler(commands=['admin'])
async def admin_options(message: types.Message):
    logging.info('admin command from: %r', message.from_user.id) 
    
    if message.from_user.id in admin_id:
        question_name, text, answers = get_next_question('admin_options')
        keyboard = make_keyboard(question_name, answers)
    else: 
        text = 'У вас нет доступа'
        keyboard = None
        
    
    await message.answer(text, reply_markup = keyboard)

@dp.callback_query_handler(button_cb.filter(
    question_name=['admin_options', 'admin', 'year', '2021_month']))
async def callback_admin_action(
    query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    
    # callback_data contains all info from callback data
    logging.info('Got this callback data: %r', callback_data) 
    
    await query.answer()  # don't forget to answer callback query as soon as possible
    callback_question = callback_data['question_name']
    callback_answer = callback_data['answer']
    
    question_name, text, answers = get_next_question(callback_question,
                                                     callback_answer)
    keyboard = make_keyboard(question_name, answers)
    
    await bot.send_message(query.from_user.id, text, reply_markup = keyboard)
    
    if question_name == 'all_answers':
        headings = ['id', 'Имя','Фамилия','username','язык','номер телефона','id','id', 'дата ответа', 'лояльность', 'менеджер', 
                    'доставка', 'кулинария', 'диетология', 'отзыв']
        filepath = 'all_answers.xls'
        DB.export_to_excel(headings, filepath)
        document = open(filepath,'rb')
        await bot.send_document(query.from_user.id, document)
        
    elif question_name == 'analysis':
        text = get_analysis(DB.get_answer())
        await bot.send_message(query.from_user.id, text)
    


@dp.message_handler(content_types = types.message.ContentType.TEXT)
async def new_text_message(message: types.Message):
    logging.info('new message from: %r', message.from_user.id) 
    DB.add_review(user_id = message.from_user.id, text = message.text)
    await message.reply('Я передам эту информацию руководству компании. Спасибо!')

@dp.message_handler(content_types = types.message.ContentType.CONTACT)
async def new_contact(message: types.Message):
    logging.info('new phone from: %r', message.from_user.id) 
    DB.add_phone(user_id = message.from_user.id, 
                 phone = message.contact.phone_number)
    await message.reply('Записала. Теперь можем начать.',
                        reply_markup = types.ReplyKeyboardRemove())
    
    await message.answer(get_text_from('text_of_questions/hello.txt'))
    
    question_name, text, answers = get_next_question('start')
    keyboard = make_keyboard(question_name, answers)
    await message.answer(text, reply_markup = keyboard )

@dp.message_handler(content_types = types.message.ContentType.ANY)
async def staf(message: types.Message):
    logging.info('strange staf from: %r', message.from_user.id)
    await message.reply('Я не знаю что это. Если хотите оставить отзыв, то сделайте это с помощью текста')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)