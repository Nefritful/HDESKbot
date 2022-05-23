import dialogs
import vars
import sql
import keyboards
import logic


async def start_command(message):
    userdata = sql.checkAuth(message.from_user.id)
    if userdata == "connErr":
        await vars.bot.send_message(message.from_user.id, dialogs.error)
    elif userdata == "false":
        vars.userHistory.update({message.chat.id: []})
        vars.userHistory[message.chat.id].append("New")
        await vars.bot.send_message(message.from_user.id, dialogs.greatings)
    else:
        await vars.bot.send_message(message.from_user.id, text='Инициализация',
                                    reply_markup=keyboards.markup3)
        await vars.bot.send_message(message.from_user.id, dialogs.greatings2,
                                    reply_markup=keyboards.keyboard_inl)


async def help_command(message):
    await vars.bot.send_message(message.from_user.id, dialogs.help)

async def clear_command(message, reg, id):
    await logic.Despose_All(id)
    await reg.Neutral.set()
    await vars.bot.send_message(message.from_user.id, "Логические цепочки очищены")

async def com_command(message):
    await logic.init_All(message.chat.id)
    tempText = ''

    if message.text is not None:  # Только текст
        tempText = message.text
    else:
        if message.caption is not None:
            tempText = message.caption
    x = tempText.split(" ")
    tempMsg = ''
    for msg in x[2:]:
        tempMsg = tempMsg + ' ' + msg
    vars.userHistory[message.chat.id].append(x[1])
    vars.userHistory[message.chat.id].append(tempMsg)

    res = sql.addComment3(message.chat.id, vars.userHistory[message.chat.id],
                          vars.userMessage[message.chat.id])
    await logic.Despose_All(message.chat.id)
    await vars.bot.send_message(message.chat.id, dialogs.successCom)
    await vars.bot.send_message(message.chat.id, dialogs.greatings2,
                                reply_markup=keyboards.keyboard_inl)

async def hide_command(message):
    await logic.init_All(message.chat.id)
    adminChk = sql.ifAdmin(message.chat.id)
    if adminChk == '1':
        tempText = ''
        if message.text is not None:  # Только текст
            tempText = message.text
        else:
            if message.caption is not None:
                tempText = message.caption
        x = tempText.split(" ")
        tempMsg = ''
        for msg in x[2:]:
            tempMsg = tempMsg + ' ' + msg
        list = [x[1], tempMsg]
        res = sql.addHideComment(message.chat.id, list, vars.userMessage[message.chat.id])
        if res == None:
            await vars.bot.send_message(message.chat.id, dialogs.successCom)
            await vars.bot.send_message(message.chat.id, dialogs.greatings2,
                                        reply_markup=keyboards.keyboard_inl)
        else:
            await vars.bot.send_message(message.chat.id, "Ошибка в отправке коментария. Пропишите команду /clear и повторите попытку.")
        await logic.Despose_All(message.chat.id)
    else:
        await vars.bot.send_message(message.chat.id, "Данная функция доступна только администраторам, требуется повышение прав.")


async def show_command(message):
    x = message.text.split(" ")

    tempStr = sql.getMessageAuth(message.chat.id, x[1])

    if (tempStr != "Нет Вашей заявки с таким номером"):
        answer2 = sql.getCommentsAuth(x[1])
        await vars.bot.send_message(message.chat.id, tempStr + '\r\n' + answer2)
    else:
        await vars.bot.send_message(message.chat.id, tempStr)


async def list_command(message):
    tempStr = sql.getMyMessagesAuth(message.chat.id)
    await vars.bot.send_message(message.chat.id, tempStr)
