from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

inline_close = InlineKeyboardButton('Отмена', callback_data='Close')
inline_close2 = InlineKeyboardButton('Нет', callback_data='feedback_no')
inline_fb = InlineKeyboardButton('Да', callback_data='feedback')
inline_Create = InlineKeyboardButton('✅ Создать заявку', callback_data='Create')
inline_End = InlineKeyboardButton('✅ Завершить', callback_data='End')
inline_EndComment = InlineKeyboardButton('✅ Отправить', callback_data='EndComment')
inline_Answer = InlineKeyboardButton('Ответить', callback_data='Answer')
inline_itsme = InlineKeyboardButton('Да', callback_data='itsme')
inline_itsnotme = InlineKeyboardButton('Нет', callback_data='itsnotme')
inline_LastCom = InlineKeyboardButton('Ответить нa комментарий', callback_data='LastCom')
inline_oneStar = InlineKeyboardButton('1⭐', callback_data='oneStar')
inline_twoStar = InlineKeyboardButton('2⭐', callback_data='twoStar')
inline_threeStar = InlineKeyboardButton('3⭐', callback_data='threeStar')
inline_fourStar = InlineKeyboardButton('4⭐', callback_data='fourStar')
inline_fiveStar = InlineKeyboardButton('5⭐', callback_data='fiveStar')

button1 = KeyboardButton('1️⃣Создать заявку')
button2 = KeyboardButton('2️⃣Напомнить логин')
button3 = KeyboardButton('3️⃣Сбросить пароль')
markup3 = ReplyKeyboardMarkup(resize_keyboard=True).add(
    button1).add(button2).add(button3)

markup2 = ReplyKeyboardMarkup(resize_keyboard=True).add(
    button1).add(button2)


keyboard_inlCl = InlineKeyboardMarkup().add(inline_close)
keyboard_inl = InlineKeyboardMarkup().add(inline_Create)
keyboard_inl2 = InlineKeyboardMarkup().add(inline_End, inline_close)
keyboard_inl3 = InlineKeyboardMarkup().add(inline_EndComment, inline_close)
keyboard_feedbackYN = InlineKeyboardMarkup().add(inline_fb, inline_close2)
keyboard_ans = InlineKeyboardMarkup().add(inline_Answer)
keyboard_inlCom = InlineKeyboardMarkup().add(inline_Create, inline_LastCom)
keyboard_YesNo = InlineKeyboardMarkup().add(inline_itsme, inline_itsnotme)

keyboard_Stars = InlineKeyboardMarkup().add(
    inline_oneStar, inline_twoStar, inline_threeStar, inline_fourStar, inline_fiveStar)


empty = InlineKeyboardMarkup(inline_keyboard=[[]])
