import logging
import json
# tasks.json - "Вопрос":["Ответ1", "потенциальный ответ 2", "и другие"]
# users.json - "Id":["status", "name", "№вопроса", "message id of last message from bot to edit"]
#       0 - usual, 1 - change name

TOKEN = ""

import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
mainKeyboard = [
    [
        InlineKeyboardButton("Изменить имя", callback_data='change_name'),
        InlineKeyboardButton("Посмотреть задание", callback_data='get_task'),
    ],
    [InlineKeyboardButton("Статистика", callback_data='stat')],
]
cancelKeyboard = [
    [
        InlineKeyboardButton("Отменить изменения", callback_data='cancel'),
        InlineKeyboardButton("Посмотреть задание", callback_data='get_task'),
    ],
    [InlineKeyboardButton("Статистика", callback_data='stat')],
]

reply_markup = InlineKeyboardMarkup(mainKeyboard)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Если ты тут в первый раз, то введи своё имя, после нажатия "Изменить имя".'
                              ' Дальше можешь приступить к выполнению заданий', reply_markup=reply_markup)

    a_file = open("users.json", "r")
    json_object = json.load(a_file)
    a_file.close()
    if str(update.message.chat_id) not in list(json_object.keys()):
        json_object[update.message.chat_id] = [0, update.message.from_user.first_name, 0, update.message.message_id + 1]

        a_file = open("users.json", "w")
        json.dump(json_object, a_file)
        a_file.close()
    changeJSON(update.message.chat_id, update.message.message_id + 1, "messageId")


def changeJSON(userId, what, where):
    n = {
        "status": 0,
        "name": 1,
        "question": 2,
        "messageId": 3
    }
    a_file = open("users.json", "r", encoding="utf-8")
    json_object = json.load(a_file)
    a_file.close()

    json_object[str(userId)][n[where]] = what

    a_file = open("users.json", "w", encoding="utf-8")
    json.dump(json_object, a_file)
    a_file.close()


def genStat(uId):
    #import copy
    now = datetime.datetime.now()
    stat = "Вот текущая статстика на " + now.strftime("%d-%m %H:%M:%S") + ":\n"

    with open("users.json", "r", encoding="utf-8") as read_file:
        user = json.load(read_file)
    """
    userc = copy.deepcopy(user)
    toSort = []
    for i in list(user.keys()):
        toSort.append(user[i][2])
    toSort.sort(reverse=True)
    usersIdSorted = []
    print(toSort)
    for i in range(len(list(user.keys()))):
        res = toSort[i]
        for j in list(user.keys()):
            if user[j][2] == res:
                print(user[j][2])
                usersIdSorted.append(j)
                break

    #print(usersIdSorted)

    for i in range(len(usersIdSorted)):
        name = userc[usersIdSorted[i]][1]
        if uId == usersIdSorted[i]:
            name = "<u>" + name + "</u>"

        stat += str(i + 1) + ". " + name + ": ✅" + str(user[usersIdSorted[i]][2]) + "\n"
        del userc[usersIdSorted[i]]
"""
    userS = sorted(user.values(), key=lambda a: a[2], reverse=True)
    #print(userS)

    for i in range(len(userS)):
        name = userS[i][1]

        if name == user[str(uId)][1]:
            name = "<u>"+name+"</u>"
        stat+=str(i+1)+". "+name+" ✅"+str(userS[i][2])+"\n"

    return stat


def getTask(num):
    with open("tasks.json", "r", encoding="utf-8") as read_file:
        data = json.load(read_file)
    # print(data)
    if num >= len(list(data.keys())):
        task = "Ты выполнил все задания, молодец!"
    else:
        task = "Задание №" + str(num + 1) + ":\n" + list(data.keys())[num]
    return task


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()
    print(query)
    if query.data == "change_name":
        changeJSON(query.message.chat_id, 1, "status")
        with open("users.json", "r", encoding="utf-8") as read_file:
            user = json.load(read_file)
        curName = user[str(query.message.chat_id)][1]

        end = curName
        if curName == "":
            end = "*никакое*"

        query.edit_message_text(text="Хорошо, введи своё новое имя, текущее - " + end, reply_markup=InlineKeyboardMarkup(cancelKeyboard))
    elif query.data == "cancel":
        query.edit_message_text(text="Имя не изменилось", reply_markup=reply_markup)

        changeJSON(query.message.chat_id, 0, "status")

    elif query.data == "get_task":
        changeJSON(query.message.chat_id, 0, "status")

        with open("users.json", "r", encoding="utf-8") as read_file:
            user = json.load(read_file)
        question = user[str(query.message.chat_id)][2]
        query.edit_message_text(text=getTask(question), reply_markup=reply_markup)
    elif query.data == "stat":
        changeJSON(query.message.chat_id, 0, "status")

        try:
            query.edit_message_text(text=genStat(query.message.chat_id), reply_markup=reply_markup,
                                    parse_mode=ParseMode.HTML)
        except:
            pass


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Use /start to test this bot.")


def onMessage(update: Update, context: CallbackContext) -> None:
    with open("users.json", "r", encoding="utf-8") as read_file:
        user = json.load(read_file)
    status = user[str(update.message.chat_id)][0]
    lName = user[str(update.message.chat_id)][1]
    if lName == "":
        lName = "*никакое*"
    mId = user[str(update.message.chat_id)][3]
    question = user[str(update.message.chat_id)][2]
    bot = Bot(token=TOKEN)
    if status == 1:
        changeJSON(update.message.chat_id, 0, "status")

        changeJSON(update.message.chat_id, update.message.text, "name")
        bot.edit_message_text(chat_id=update.message.chat_id, text="Хорошо, введи своё новое имя, предыдущим было - " + lName,
                              message_id=mId)
        update.message.reply_text("Твоё имя изменено на " + update.message.text, reply_markup=reply_markup)

    elif status == 0:

        with open("tasks.json", "r", encoding="utf-8") as read_file:
            tasks = json.load(read_file)
        a = 0
        if question >= len(list(tasks.keys())):
            a = 1

        corAnsw = []
        try:
            corAnsw = tasks[list(tasks.keys())[question]]
        except:
            pass
        if a == 1:
            bot.edit_message_text(chat_id=update.message.chat_id, text="Ты уже выполнил все задания!",
                                  message_id=mId)
            update.message.reply_text("Новые задания закончились\n",
                                      reply_markup=reply_markup)
        elif update.message.text in corAnsw:
            changeJSON(update.message.chat_id, question + 1, "question")
            bot.edit_message_text(chat_id=update.message.chat_id, text="Это задание (№"+str(question+1)+") было выполнено правильно",
                                  message_id=mId)
            update.message.reply_text("Ответ правильный✅\n" + getTask(question + 1),
                                      reply_markup=reply_markup)
        else:
            bot.edit_message_text(chat_id=update.message.chat_id, text="Это задание (№"+str(question+1)+") было выполнено неправильно",
                                  message_id=mId)
            update.message.reply_text("Ответ не правильный❌\n" + getTask(question), reply_markup=reply_markup)
    changeJSON(update.message.chat_id, update.message.message_id + 1, "messageId")


def main() -> None:
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, onMessage))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
