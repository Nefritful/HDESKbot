import dialogs
import vars
import sql
import keyboards
import logging
import re

logger = logging.getLogger(__name__)


# Общие функции
async def initScore(Score, message_id, user, reg):
    if vars.Dev_Log == 1:
        await vars.bot.send_message(user, 'Dev_Log: ' + str(user) + ' начал оценку(' + str(Score) + ').')
    logger.info('%s начал оценку( %s', user, Score)
    await Despose_All(user)
    await init_All(user)
    vars.userHistory[user].append(message_id)
    vars.userHistory[user].append(Score)
    if Score == 1:
        await vars.bot.send_message(user, dialogs.score1)
        await reg.NewScore.set()
    if Score == 2:
        await vars.bot.send_message(user, dialogs.score2, reply_markup=keyboards.keyboard_feedbackYN)
    if Score == 3:
        await vars.bot.send_message(user, dialogs.score3, reply_markup=keyboards.keyboard_feedbackYN)
    if Score == 4:
        await vars.bot.send_message(user, dialogs.score4, reply_markup=keyboards.keyboard_feedbackYN)
    if Score == 5:
        await vars.bot.send_message(user, dialogs.score5, reply_markup=keyboards.keyboard_feedbackYN)

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

async def Despose_All(id):
    if id in vars.userHistory:
        del vars.userHistory[id]
    if id in vars.userMessage:
        del vars.userMessage[id]
    if id in vars.userBotActions:
        del vars.userBotActions[id]

async def Delete_Carefuly(chat_id, message_id):
    try:
        await vars.bot.delete_message(chat_id, message_id)
        logger.info('успешное удаление старого сообщения')
    except ValueError:
        logger.info('ошибка при удалении старого сообщения:')
        logger.info(ValueError)

async def init_All(id):
    if id in vars.userHistory:
        logger.info('userHistory уже создан')
    else:
        vars.userHistory.update({id: []})
    if id in vars.userMessage:
        logger.info('userMessage уже создан')
    else:
        vars.userMessage.update({id: []})
    if id in vars.userBotActions:
        logger.info('userBotActions уже создан')
    else:
        vars.userBotActions.update({id: []})

# Конец общих функций


async def feedback(message):
    if message.text is not None:  # Только текст
        vars.userMessage[message.chat.id].append(message.text)
    res = sql.feedback(message.chat.id, vars.userMessage[message.chat.id], vars.userHistory[message.chat.id])
    await vars.bot.send_message(message.chat.id, "Отзыв успешно отправлен. \n" + dialogs.newReq,
                                reply_markup=keyboards.keyboard_inl)
    await Despose_All(message.chat.id)


async def NewReq(message):
    if message.chat.id in vars.userMessage:
        if message.text is not None:  # Только текст
            if vars.Dev_Log == 1:
                await vars.bot.send_message(message.chat.id,
                                            'Dev_Log: ' + str(message.chat.id) + ' добавил текст ' + message.text)
            logger.info('%s  добавил текст %s', message.chat.id, message.text)
            vars.userHistory[message.chat.id].append(message.text)

            #await Delete_Carefuly(message.chat.id, message.message_id-1)
            messageTemp = ""
            for x in range(len(vars.userHistory[message.chat.id])):
                messageTemp = messageTemp + vars.userHistory[message.chat.id][x] + "\r\n"

            await vars.bot.send_message(message.chat.id,
                                        dialogs.addInfoStr2 + '\r\n' + messageTemp + '\r\n' + dialogs.addInfoStr,
                                        reply_markup=keyboards.keyboard_inl2)
        else:  # Есть файл
            file_info = ""
            Size_ok = 1
            Closed = 0
            if message.photo is not None:
                if len(message.photo) > 0:
                    filter_size = filter(lambda p: p.file_size < vars.MAX_FILE_SIZE, message.photo)
                    photos = sorted(
                        list(map(lambda p: p, filter_size)),
                        key=lambda s: s['file_size'])
                    file_info = await vars.bot.get_file(photos[-1]['file_id'])
            if message.video is not None:
                if message.voice.file_size > 19500000:
                    file_info = await vars.bot.get_file(message.video.file_id)
                else:
                    Size_ok = 0
            if message.voice is not None:
                if message.voice.file_size < 19500000:
                    file_info = await vars.bot.get_file(message.voice.file_id)
                else:
                    Size_ok = 0
            if message.video_note is not None:
                file_info = vars.bot.get_file(message.video_note.file_id)
            if message.document is not None:
                if message.document.file_size < 19500000:
                    file_info = await vars.bot.get_file(message.document.file_id)
                else:
                    Size_ok = 0
            if message.audio is not None:
                if message.audio.file_size > 19500000:
                    file_info = vars.bot.get_file(message.audio.file_id)
                else:
                   Size_ok = 0
            if message.caption is not None:
                vars.userHistory[message.chat.id].append(message.caption)
            if Size_ok == 1:
                temp = "https://api.telegram.org/file/bot" + vars.TOKEN + "/" + file_info.file_path
                vars.userMessage[message.chat.id].append(temp)
                if message.caption is not None:
                    if vars.Dev_Log == 1:
                        await vars.bot.send_message(message.chat.id, 'Dev_Log: ' + str(message.chat.id) +
                                                    ' добавил файл и текст ' + message.caption)
                    logger.info('%s  добавил файл и текст %s', message.chat.id, message.caption)

                if len(vars.userHistory[message.chat.id]) in vars.userBotActions[message.chat.id]:
                    try:
                        messageTemp = ""
                        for x in range(len(vars.userHistory[message.chat.id])):
                            messageTemp = messageTemp + vars.userHistory[message.chat.id][x] + "\r\n"
                        await vars.bot.edit_message_text(chat_id=message.chat.id,
                                                         message_id=message.message_id + 1,
                                                         text=dialogs.addInfoStr2 + '\r\n' + messageTemp + '\r\n' + 'Добавлено файлов: ' + str(
                                                             len(vars.userMessage[
                                                                     message.chat.id])) + '\r\n' + dialogs.addInfoStr,
                                                         reply_markup=keyboards.keyboard_inlCom)
                    except ValueError:
                        logger.info(ValueError)
                    try:
                        await vars.bot.delete_message(message.chat_id, message.message_id)
                        print('успешное удаление старого сообщения')
                    except ValueError:
                        logger.info('ошибка при удалении старого сообщения:')
                        logger.info(ValueError)
                else:
                    vars.userBotActions[message.chat.id].append(len(vars.userHistory[message.chat.id]))
                    messageTemp = ""
                    for x in range(len(vars.userHistory[message.chat.id])):
                        messageTemp = messageTemp + vars.userHistory[message.chat.id][x] + "\r\n"


                    await vars.bot.send_message(
                        message.chat.id,
                        dialogs.addInfoStr2 + '\r\n' + messageTemp + '\r\n' + 'Добавлено файлов: ' + str(len(vars.userMessage[message.chat.id])) + '\r\n' + dialogs.addInfoStr,
                        reply_markup=keyboards.keyboard_inl2)
            else:
                await vars.bot.send_message(message.from_user.id,
                                            'Файл привышает лимит в 20МБ, попробуйте перезаписать или сжать файл',
                                            reply_markup=keyboards.keyboard_inl2)
    else:
        await vars.bot.send_message(message.from_user.id, dialogs.error,
                                    reply_markup=keyboards.keyboard_inl)


async def NewCom(message):
    if message.chat.id in vars.userMessage:
        if message.text is not None:  # Только текст
            if vars.Dev_Log == 1:
                await vars.bot.send_message(message.chat.id, 'Dev_Log: ' + str(message.chat.id) +
                                            ' добавил текст комментария ' + message.text)
            logger.info('%s добавил текст комментария %s', message.chat.id, message.text)
            vars.userHistory[message.chat.id].append(message.text)

            #await Delete_Carefuly(message.chat.id, message.message_id - 1)
            messageTemp = ""
            for x in range(len(vars.userHistory[message.chat.id][0:])):
                messageTemp = messageTemp + vars.userHistory[message.chat.id][x] + "\r\n"

            await vars.bot.send_message(message.chat.id,
                                        dialogs.addInfoStr2 + '\r\n' + messageTemp + '\r\n' + dialogs.comInfoStr,
                                        reply_markup=keyboards.keyboard_inl3)

        else:  # Есть файл
            file_info = ""
            Size_ok = 1
            Closed = 0
            if message.photo is not None:
                if len(message.photo) > 0:
                    filter_size = filter(lambda p: p.file_size < vars.MAX_FILE_SIZE, message.photo)
                    photos = sorted(
                        list(map(lambda p: p, filter_size)),
                        key=lambda s: s['file_size'])
                    file_info = await vars.bot.get_file(photos[-1]['file_id'])
            if message.video is not None:
                if message.voice.file_size > 19500000:
                    file_info = await vars.bot.get_file(message.video.file_id)
                else:
                    Size_ok = 0
            if message.voice is not None:
                if message.voice.file_size < 19500000:
                    file_info = await vars.bot.get_file(message.voice.file_id)
                else:
                    Size_ok = 0
            if message.video_note is not None:
                file_info = vars.bot.get_file(message.video_note.file_id)
            if message.document is not None:
                if message.document.file_size < 19500000:
                    file_info = await vars.bot.get_file(message.document.file_id)
                else:
                    Size_ok = 0
            if message.audio is not None:
                if message.audio.file_size > 19500000:
                    file_info = vars.bot.get_file(message.audio.file_id)
                else:
                    Size_ok = 0
            if message.caption is not None:
                vars.userHistory[message.chat.id].append(message.caption)
            if Size_ok == 1:
                temp = "https://api.telegram.org/file/bot" + vars.TOKEN + "/" + file_info.file_path
                vars.userMessage[message.chat.id].append(temp)
                if message.caption is not None:
                    if vars.Dev_Log == 1:
                        await vars.bot.send_message(message.chat.id, 'Dev_Log: ' + str(message.chat.id) +
                                                    ' добавил файл и текст ' + message.caption)
                    logger.info('%s добавил файл и текст %s', message.chat.id, message.caption)

                if len(vars.userHistory[message.chat.id]) in vars.userBotActions[message.chat.id]:
                    try:
                        messageTemp = ""
                        for x in range(len(vars.userHistory[message.chat.id])):
                            messageTemp = messageTemp + vars.userHistory[message.chat.id][x] + "\r\n"
                        await vars.bot.edit_message_text(chat_id=message.chat.id,
                                                         message_id=message.message_id + 1,
                                                         text=dialogs.addInfoStr2 + '\r\n' + messageTemp + '\r\n' + 'Добавлено файлов: ' + str(
                                                             len(vars.userMessage[
                                                                     message.chat.id])) + '\r\n' + dialogs.addInfoStr,
                                                         reply_markup=keyboards.keyboard_inlCom)
                    except ValueError:
                        logger.info(ValueError)
                    try:
                        await vars.bot.delete_message(message.chat_id, message.message_id)
                        print('успешное удаление старого сообщения')
                    except ValueError:
                        logger.info('ошибка при удалении старого сообщения:')
                        logger.info(ValueError)
                else:
                    vars.userBotActions[message.chat.id].append(len(vars.userHistory[message.chat.id]))
                    messageTemp = ""
                    for x in range(len(vars.userHistory[message.chat.id][1:])):
                        messageTemp = messageTemp + vars.userHistory[message.chat.id][x] + "\r\n"

                    await vars.bot.send_message(
                        message.chat.id,
                        dialogs.addInfoStr2 + '\r\n' + messageTemp + '\r\n' + 'Добавлено файлов: ' + str(len(vars.userMessage[message.chat.id])) + '\r\n' + dialogs.comInfoStr,
                        reply_markup=keyboards.keyboard_inl3)
            else:
                await vars.bot.send_message(message.from_user.id,
                                            'Файл привышает лимит в 20МБ, попробуйте перезаписать или сжать файл',
                                            reply_markup=keyboards.keyboard_inl3)
    else:
        await vars.bot.send_message(message.from_user.id, dialogs.newReq3,
                                    reply_markup=keyboards.keyboard_inl)


async def NewInit(message):
    message_new = 'Пользователь {} просит предоставить доступ к боту. ID: {}'.format(message.text, message.from_user_id)
    list = ["Запрос на предоставление доступа.",message_new]
    await sql.addMessageICQ(vars.operator, list, "false")


async def SimpleText(message):
    userdata = sql.checkAuth(message.from_user.id)
    if userdata == "false":
        if message.chat.id in vars.userHistory:
            if vars.userHistory[message.chat.id][0] == "New":
                if message.text is not None:  # Только текст
                    vars.userMessage.update({message.chat.id: []})
                    vars.userMessage[message.chat.id].append(
                        "Пользователь " + message.text + " просит предоставить доступ к HDESKBot. Код телеграмма:" + str(
                            message.from_user.id))
                    del vars.userHistory[message.chat.id]
                    vars.userHistory.update({message.chat.id: []})
                    res = sql.addMessageICQ_verify(vars.operator, vars.userMessage[message.chat.id],
                                             vars.userHistory[message.chat.id])
                    logger.info('ISSUE123', message.chat.id, res)
                    await vars.bot.send_message(message.from_user.id, dialogs.wait)
                    del vars.userHistory[message.chat.id]
                    del vars.userMessage[message.chat.id]
                else:
                    await vars.bot.send_message(message.from_user.id, "Прошу ввести запрашиваемые данные текстом.")
        else:
            await vars.bot.send_message(message.from_user.id, dialogs.auth)
    else:
        await init_All(message.chat.id)
        if message.text is not None:  # Только текст
            vars.userHistory[message.chat.id].append(message.text)
        else:  # Есть файл
            file_info = ""
            Size_ok = 1
            Closed = 0
            if message.photo is not None:
                if len(message.photo) > 0:
                    filter_size = filter(lambda p: p.file_size < vars.MAX_FILE_SIZE, message.photo)
                    photos = sorted(
                        list(map(lambda p: p, filter_size)),
                        key=lambda s: s['file_size'])
                    file_info = await vars.bot.get_file(photos[-1]['file_id'])
            if message.video is not None:
                if message.voice.file_size > 19500000:
                    file_info = await vars.bot.get_file(message.video.file_id)
                else:
                    Size_ok = 0
            if message.voice is not None:
                if message.voice.file_size < 19500000:
                    file_info = await vars.bot.get_file(message.voice.file_id)
                else:
                    Size_ok = 0
            if message.video_note is not None:
                file_info = vars.bot.get_file(message.video_note.file_id)
            if message.document is not None:
                if message.document.file_size < 19500000:
                    file_info = await vars.bot.get_file(message.document.file_id)
                else:
                    Size_ok = 0
            if message.audio is not None:
                if message.audio.file_size > 19500000:
                    file_info = vars.bot.get_file(message.audio.file_id)
                else:
                    Size_ok = 0
            if message.caption is not None:
                vars.userHistory[message.chat.id].append(message.caption)
            if Size_ok == 1:
                temp = "https://api.telegram.org/file/bot" + vars.TOKEN + "/" + file_info.file_path
                vars.userMessage[message.chat.id].append(temp)
                if message.caption is not None:
                    if vars.Dev_Log == 1:
                        await vars.bot.send_message(message.chat.id, 'Dev_Log: ' + str(message.chat.id) +
                                                    ' добавил файл и текст ' + message.caption)
                    logger.info('%s  добавил файл и текст %s', message.chat.id, message.caption)

                if len(vars.userHistory[message.chat.id]) in vars.userBotActions[message.chat.id]:
                    try:
                        messageTemp = ""
                        for x in range(len(vars.userHistory[message.chat.id])):
                            messageTemp = messageTemp + vars.userHistory[message.chat.id][x] + "\r\n"
                        await vars.bot.edit_message_text(chat_id=message.chat.id,
                                                         message_id=message.message_id+1,
                                                         text=dialogs.addInfoStr2 + '\r\n' + messageTemp + '\r\n' + 'Добавлено файлов: ' + str(len(vars.userMessage[message.chat.id])) + '\r\n' + dialogs.addInfoStr,
                                                         reply_markup=keyboards.keyboard_inlCom)
                    except ValueError:
                        logger.info(ValueError)
                    try:
                        await vars.bot.delete_message(message.chat_id, message.message_id)
                        print('успешное удаление старого сообщения')
                    except ValueError:
                        logger.info('ошибка при удалении старого сообщения:')
                        logger.info(ValueError)


                else:
                    vars.userBotActions[message.chat.id].append(len(vars.userHistory[message.chat.id]))
                    messageTemp = ""
                    for x in range(len(vars.userHistory[message.chat.id])):
                        messageTemp = messageTemp + vars.userHistory[message.chat.id][x] + "\r\n"

                    await vars.bot.send_message(
                        message.chat.id,
                        dialogs.addInfoStr2 + '\r\n' + messageTemp + '\r\n' + 'Добавлено файлов: ' + str(len(vars.userMessage[message.chat.id])) + '\r\n' + dialogs.addInfoStr,
                            reply_markup=keyboards.keyboard_inlCom)
            else:
                await vars.bot.send_message(message.from_user.id,
                                            'Файл привышает лимит в 20МБ, попробуйте перезаписать или сжать файл',
                                            reply_markup=keyboards.keyboard_inl2)
        if len(vars.userMessage[message.chat.id]) == 0:
            await vars.bot.send_message(message.from_user.id, dialogs.newReq, reply_markup=keyboards.keyboard_inlCom)
async def LoginBack(message):
    userdata = sql.checkAuth(message.from_user.id)
    if userdata == "false":
        await vars.bot.send_message(message.from_user.id, "Привязка пользователя еще не пройдена!")
    else:
        Login = userdata.split(',')[1].split(':')[1]
        await vars.bot.send_message(message.from_user.id, 'Ваш логин: ' + Login)
async def PasswordBack(message):
    userdata = sql.checkAuth(message.from_user.id)
    if userdata == "false":
        await vars.bot.send_message(message.from_user.id, "Привязка пользователя еще не пройдена!")
    else:
        res = sql.change_pwd(message.from_user.id)
        #list = ["Сброс пароля.", "\nПользователь "+ userdata.split(',')[3].split(':')[1] + " запрашивает сброс пароля." + "\nID в базе: "+ userdata.split(',')[0].split(':')[1]+ "\nTelegramID: "+ userdata.split(',')[17].split(':')[1]+ "\nЛогин: "+ userdata.split(',')[1].split(':')[1]+ "\nНомер телефона: "+ userdata.split(',')[5].split(':')[1]]
        #await vars.bot.send_message(message.from_user.id, res,reply_markup=keyboards.markup2)
        #await sql.addMessageICQ(message.from_user.id,list , "false")


async def Create_Callback(message):
    if vars.Dev_Log == 1:
        await vars.bot.send_message(message.chat.id,
                                    'Dev_Log: ' + str(message.chat.id) + ' начал создание заявки.')
    logger.info('%s начал создание', message.chat.id)
    await init_All(message.chat.id)
    await Delete_Carefuly(message.chat.id, message.message_id)

    tempMsg = ''
    if len(vars.userHistory[message.chat.id]) > 0:
        for x in range(len(vars.userHistory[message.chat.id])):
            tempMsg = tempMsg + vars.userHistory[message.chat.id][x] + "\r\n"
    if tempMsg != '':
        await vars.bot.send_message(message.chat.id,
                                    dialogs.addInfoStr2 + '\r\n' + tempMsg + '\r\n' + dialogs.addInfoStr,
                                    reply_markup=keyboards.keyboard_inl2)
    else:
        await vars.bot.send_message(message.chat.id, dialogs.addInfoStr, reply_markup=keyboards.keyboard_inlCl)


async def Answer_Callback(call):
    if vars.Dev_Log == 1:
        await vars.bot.send_message(call.message.chat.id,
                                    'Dev_Log: ' + str(call.message.chat.id) + ' начал комментирование.')
    logger.info('%s начал комментирование', call.message.chat.id)
    await Despose_All(call.message.chat.id)
    await init_All(call.message.chat.id)
    message_id = call.message.text[call.message.text.find("№") + 1:call.message.text.find(" ")]
    vars.userHistory[call.message.chat.id].append(message_id)
    try:
        await vars.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                         text=call.message.text, reply_markup=keyboards.empty)
    except ValueError:
        logger.info('ошибка при удалении кнопки:')
        logger.info(ValueError)
    await vars.bot.send_message(call.message.chat.id, dialogs.comInfoStr2,
                                reply_markup=keyboards.keyboard_inlCl)


async def Close_Callback(call):
    if vars.Dev_Log == 1:
        await vars.bot.send_message(call.message.chat.id,
                                    'Dev_Log: ' + str(call.message.chat.id) + ' отменил создание.')
    logger.info('%s отменил создание', call.message.chat.id)

    await Despose_All(call.message.chat.id)

    await Delete_Carefuly(call.message.chat.id, call.message.message_id)
    await vars.bot.send_message(call.message.chat.id, dialogs.cancel)
    await vars.bot.send_message(call.message.chat.id, dialogs.newReq,
                                reply_markup=keyboards.keyboard_inl)


async def feedback_no_Callback(call):
    if vars.Dev_Log == 1:
        await vars.bot.send_message(call.message.chat.id,
                                    'Dev_Log: ' + str(call.message.chat.id) + ' отказался от отзыва.')
    logger.info('%s отказался от отзыва', call.message.chat.id)

    vars.userMessage[call.message.chat.id].append(" ")
    res = sql.feedback(call.message.chat.id, vars.userMessage[call.message.chat.id],
                       vars.userHistory[call.message.chat.id])
    await vars.bot.send_message(call.message.chat.id, dialogs.newReq, reply_markup=keyboards.keyboard_inl)
    await Despose_All(call.message.chat.id)



async def End_Callback(call, reg):
    if vars.Dev_Log == 1:
        await vars.bot.send_message(call.message.chat.id,
                                    'Dev_Log: ' + str(call.message.chat.id) + ' закончил создание заявки.')
    logger.info('%s закончил создание', call.message.chat.id)

    if call.message.chat.id in vars.userMessage:
        res = sql.addMessageICQ(call.message.chat.id, vars.userHistory[call.message.chat.id],
                                vars.userMessage[call.message.chat.id])
        await Despose_All(call.message.chat.id)

        await Delete_Carefuly(call.message.chat.id, call.message.message_id)
        try:
            req_id_str = res[2:8]
            req_id = int(''.join(filter(str.isdigit, req_id_str)))
            message_result = 'Заявка {} успешно создана'.format(req_id)
            await vars.bot.send_message(call.message.chat.id, message_result)
            await vars.bot.send_message(call.message.chat.id,
                                        dialogs.newReq,
                                        reply_markup=keyboards.keyboard_inl)
            await reg.Neutral.set()
        except ValueError:
            if vars.Dev_Log == 1:
                await vars.bot.send_message(call.message.chat.id,
                                            'Dev_Log: ' + str(call.message.chat.id) + ' ОШИБКА.')
            await vars.bot.send_message(call.message.chat.id, res)
            await reg.Neutral.set()
    else:
        await Delete_Carefuly(call.message.chat.id, call.message.message_id)

        await vars.bot.send_message(call.message.chat.id, dialogs.error)
        await reg.Neutral.set()


async def EndComment_Callback(call, reg):
    if vars.Dev_Log == 1:
        await vars.bot.send_message(call.message.chat.id,
                                    'Dev_Log: ' + str(call.message.chat.id) + ' закончил комментарий.')
    logger.info('%s закончил комментарий', call.message.chat.id)
    if call.message.chat.id in vars.userMessage:
        if len(vars.userMessage[call.message.chat.id]) > 0:
            res = sql.addComment3(call.message.chat.id, vars.userHistory[call.message.chat.id],
                                  vars.userMessage[call.message.chat.id])
        else:
            res = sql.addComment3(call.message.chat.id, vars.userHistory[call.message.chat.id],
                                  0)
        if res == None:
            await Delete_Carefuly(call.message.chat.id, call.message.message_id)
            await vars.bot.send_message(call.message.chat.id, dialogs.successCom)
            await vars.bot.send_message(call.message.chat.id, dialogs.newReq,
                                        reply_markup=keyboards.keyboard_inl)
        else:
            await vars.bot.send_message(call.message.chat.id,
                                        "Ошибка в отправке коментария. Пропишите команду /clear и повторите попытку.")

        await Despose_All(call.message.chat.id)

        await reg.Neutral.set()
    else:
        await Delete_Carefuly(call.message.chat.id, call.message.message_id)

        await vars.bot.send_message(call.message.chat.id, dialogs.error)
        await reg.Neutral.set()


async def LastCom_Callback(call, reg):
    if vars.Dev_Log == 1:
        await vars.bot.send_message(call.message.chat.id,
                                    'Dev_Log: ' + str(call.message.chat.id) + ' закончил комментарий.')
    logger.info('%s закончил комментарий', call.message.chat.id)
    if call.message.chat.id in vars.userMessage:
        if len(vars.userMessage[call.message.chat.id]) > 0:
            res = sql.addComment4(call.message.chat.id, vars.userHistory[call.message.chat.id],
                                  vars.userMessage[call.message.chat.id])
            print(res)
        else:
            res = sql.addComment4(call.message.chat.id, vars.userHistory[call.message.chat.id],
                                  0)
            print(res)
        if res == None:
            await Delete_Carefuly(call.message.chat.id, call.message.message_id)
            await vars.bot.send_message(call.message.chat.id, dialogs.successCom)
            await vars.bot.send_message(call.message.chat.id, dialogs.newReq,
                                        reply_markup=keyboards.keyboard_inl)
        else:
            await vars.bot.send_message(call.message.chat.id, "Ошибка в отправке коментария. Пропишите команду /clear и повторите попытку.")

        await Despose_All(call.message.chat.id)

        await reg.Neutral.set()
    else:
        await Delete_Carefuly(call.message.chat.id, call.message.message_id)

        await vars.bot.send_message(call.message.chat.id, dialogs.error)
        await reg.Neutral.set()


async def Claim_Callback(call):
    userdata = sql.checkAuth(call.message.chat.id)
    if userdata == "false":
        await vars.bot.send_message(call.message.chat.id, "Привязка пользователя еще не пройдена!")
    else:
        message_id = call.message.text.split('\n')[0]
        res = sql.check_assign(message_id)
        if res == "1":
            res = sql.assign_message(call.message.chat.id, message_id)
            await vars.bot.send_message(call.message.chat.id, "Заявка закреплена за вами")
        if res == "0":
            await vars.bot.send_message(call.message.chat.id, "Заявка уже назначина другому инженеру")