import requests
from requests.exceptions import HTTPError
from requests_ntlm import HttpNtlmAuth
import ast
import vars
import logging
import logic

logger = logging.getLogger(__name__)


def AuthNew():
    return HttpNtlmAuth(vars.servLog, vars.servPass)


def checkAuth(uid):
    # Пытаемся залезть на hdesk
    try:
        x = requests.post(
            'http://' + vars.server + '//telebotapi/checkAuth', data={'uid': uid}, auth=AuthNew(), timeout=3)
        return x.content.decode("unicode-escape")

    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)


def getCookie(uid):
    # Пытаемся залезть на hdesk
    try:
        session = requests.Session()
        response = session.get('http://' + vars.server + '//telebotAPI/checkAuth', data={'uid': uid}, timeout=3)
        return (session.cookies.get_dict())
    except Exception:
        return 'connErr'


def getMyLoginAuth(uid):
    try:
        x = requests.post('http://' + vars.server + '/telebotAPI/getMyLogin', data={'uid': uid}, auth=AuthNew())
    except HTTPError as http_err:
        logger.error('HTTP error occurred: %s', http_err)
    except Exception as err:
        logger.error('Other error occurred: %s', err)
    else:
        return x.content.decode('UTF-8')


def getMyLastUpMes(uid):
    try:
        x = requests.post(
            'http://' + vars.server + '/telebotAPI/getLastUpdatedMessage', data={'uid': uid}, auth=AuthNew())
    except HTTPError as http_err:
        logger.error('HTTP error occurred: %s', http_err)
    except Exception as err:
        logger.error('Other error occurred: %s', err)
    else:
        return x.content.decode("unicode-escape")


def getSubjectNameAuth(subject):
    x = requests.post(
        'http://' + vars.server + '/telebotAPI/getSubjectName', data={'subject': subject}, auth=AuthNew())
    return x.content.decode('UTF-8')


def getMyMessagesAuth(uid):
    try:
        x = requests.post(
            'http://' + vars.server + '/telebotapi/getMyMessages', allow_redirects=True, data={'uid': uid},
            auth=AuthNew(), timeout=4)
    except HTTPError as http_err:
        logger.error('HTTP error occurred: %s', http_err)
    except Exception as err:
        logger.error('Other error occurred: %s', err)
    else:
        return x.content.decode('UTF-8')


def getMessageAuth(uid, mid):
    x = requests.post('http://' + vars.server + '/telebotAPI/getMessage', data={'uid': uid, 'mid': mid}, auth=AuthNew())
    return x.content.decode('UTF-8')


def getCommentsAuth(mid):
    x = requests.post('http://' + vars.server + '/telebotAPI/getComments', data={'mid': mid}, auth=AuthNew())
    return x.content.decode('UTF-8')


def getStatsAuth():
    x = requests.post('http://' + vars.server + '/telebotAPI/getStats', auth=AuthNew())
    return x.content


def getSubjectListAuth():
    x = requests.post('http://' + vars.server + '/telebotAPI/getSubjectList', auth=AuthNew())
    return x.content


def feedback(sender_id, messagelist, historylist):  # feedback_telegram(message_id,stars,comment,user_id);
    mid = getMyLoginAuth(sender_id)
    mid_dict = ast.literal_eval(mid)
    message = logic.deEmojify(messagelist[0])
    if message == "":
        message = " "
    try:
        sender = mid_dict['id']
    except Exception:
        logger.error('Невозможно получить ID, пользователь не прошел авторизацию')

    try:
        x = requests.Session()
        url = "http://" + vars.server + "/telebotAPI/feedback_telegram"

        payload = {
            'user_id': sender,
            'message_id': historylist[0],
            'stars': historylist[1],
            'comment': message,
        }
        logger.debug('%s %s %s %s', sender_id, historylist[0], historylist[1], messagelist[0])
        u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут
    except HTTPError as http_err:
        logger.error('HTTP error occurred: %s', http_err)
    except Exception as err:
        logger.error('Other error occurred: %s', err)
    else:
        res = u.decode('UTF-8')
        return res


def addMessageICQ(sender_id, messagelist, filelist):
    mid = getMyLoginAuth(sender_id)
    mid_dict = ast.literal_eval(mid)
    try:
        sender = mid_dict['id']
    except Exception:
        logger.error('Невозможно получить ID, пользователь не прошел авторизацию')
    message = ""
    if len(messagelist) > 0:
        subject = messagelist[0]
    else:
        subject = "Без темы"
    for x in range(len(messagelist)):
        message = message + messagelist[x] + "\r\n"
    message = logic.deEmojify(message)
    if message == "":
        message = " "
    try:
        x = requests.Session()
        url = "http://" + vars.server + "/telebotAPI/addMessage_telegram"

        payload = {
            'sender_id': sender,
            'telegram': sender_id,
            'subject_id': 1,
            'message': message,
            'filelist': filelist,
        }
        logger.debug('%s %s %s %s', sender_id, subject, message, filelist)
        u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут
    except HTTPError as http_err:
        logger.error('HTTP error occurred: %s', http_err)
    except Exception as err:
        logger.error('Other error occurred: %s', err)
    else:
        res = u.decode('UTF-8')
        return res


def addMessageICQ_verify(sender_id, messagelist, filelist):

    mid = getMyLoginAuth(str(sender_id))
    mid_dict = ast.literal_eval(mid)
    sender = mid_dict['id']
    message = ""
    subject = messagelist[0]
    for x in range(len(messagelist)):
        message = message + messagelist[x] + "\r\n"
    message = logic.deEmojify(messagelist[0])
    if message == "":
        message = " "
    try:
        x = requests.Session()
        url = "http://" + vars.server + "/telebotAPI/addMessage_telegram"

        payload = {
            'sender_id': sender,
            'telegram': sender_id,
            'subject_id': 1,
            'message': message,
            'filelist': filelist,
            'action': "verify",
        }
        logger.debug('%s %s %s %s', sender_id, subject, message, filelist)
        u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут
    except HTTPError as http_err:
        logger.error('HTTP error occurred: %s', http_err)
    except Exception as err:
        logger.error('Other error occurred: %s', err)
    else:
        res = u.decode('UTF-8')
        return res


def cngStatus(user_id, uid, message_id, text):
    userdata = getCookie(uid)

    cookie = "ci_session="+userdata.get('ci_session')
    x = requests.Session()
    url = "http://" + vars.server + "/messages/changeStatus"

    payload = {
        'id': message_id,
        'do': 'set_status',
        'status': text,
    }
    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут
    logger.debug(u)


def cngStatus2(user_id, uid, message_id, text):
    logger.info(user_id, uid, message_id, text)


def closeMessage(user_id, uid, message_id, text):
    userdata = getCookie(uid)

    cookie = "ci_session="+userdata.get('ci_session')
    x = requests.Session()
    url = "http://" + vars.server + "/telebotAPI/close_message"

    payload = {
        'mess_id': message_id,
        'category': 'incident',
        'comment': text,
        'user_id': user_id,
        'filelist': '',
    }
    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут
    logger.debug(u)


def closeMessage2(user_id, uid, message_id, text):
    logger.info(user_id, uid, message_id, text)


def addComment3(uid, messagelist, filelist):

    rawLogin = ast.literal_eval(getMyLoginAuth(uid))

    user_id = rawLogin['id']
    message = ""
    for msg in messagelist[1:]:
        message = message + msg + "\r\n"
    message = logic.deEmojify(message)
    if message == "":
        message = " "
    x = requests.Session()
    url = "http://" + vars.server + "/telebotAPI/addComment_telegram"

    payload = {
        'message_id': int(messagelist[0]),
        'telegram': uid,
        'user_id': user_id,
        'comment_type': 2,
        'comment_text': message,
        'spend_time': 0,
        'spend_taxi': 0,
        'hard_work_time': '',
        'filelist': filelist,
    }

    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут
    logger.debug(u)


def addComment4(uid, messagelist, filelist):

    rawLogin = ast.literal_eval(getMyLoginAuth(uid))
    rawMes_id = ast.literal_eval(getMyLastUpMes(rawLogin['id']))

    user_id = rawLogin['id']
    message = ""
    for msg in messagelist:
        message = message + msg + "\r\n"
    message = logic.deEmojify(messagelist[0])
    if message == "":
        message = " "
    x = requests.Session()
    url = "http://" + vars.server + "/telebotAPI/addComment_telegram"

    payload = {
        'message_id': rawMes_id['message_id'],
        'telegram': uid,
        'user_id': user_id,
        'comment_type': 2,
        'comment_text': message,
        'spend_time': 0,
        'spend_taxi': 0,
        'hard_work_time': '',
        'filelist': filelist,
    }

    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут
    logger.info('%s', u)

def addHideComment(uid, messagelist, filelist):

    rawLogin = ast.literal_eval(getMyLoginAuth(uid))
    userdata = checkAuth(uid)
    Login = userdata.split(',')[1].split(':')[1]
    user_id = rawLogin['id']
    message = ""
    for msg in messagelist[1:]:
        message = message + msg + "\r\n"
    message = logic.deEmojify(message)
    if message == "":
        message = " "
    x = requests.Session()
    url = "http://" + vars.server + "/telebotAPI/addComment_telegram"

    payload = {
        'message_id': int(messagelist[0]),
        'telegram': uid,
        'user_id': user_id,
        'comment_type': 1,
        'comment_text': message,
        'spend_time': 0,
        'spend_taxi': 0,
        'hard_work_time': '',
        'filelist': filelist,
    }

    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут
    logger.debug(u)

def ifAdmin(uid):

    x = requests.Session()
    url = "http://" + vars.server + "/telebotAPI/check_admin"

    payload = {
        'telegram': uid,
    }
    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут

    res = u.decode('UTF-8')
    logger.debug(res)
    return res

def change_pwd(uid):

    x = requests.Session()
    url = "http://" + vars.server + "/telebotAPI/change_pwd"

    payload = {
        'telegram': uid,
    }
    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут

    res = u.decode('UTF-8')

    return res

def assign_message(uid,mid):

    x = requests.Session()
    url = "http://" + vars.server + "/telebotAPI/assign_message"

    payload = {
        'telegram': uid,
        'message_id': mid,
    }
    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут

    res = u.decode('UTF-8')

    return res

def check_assign(mid):

    x = requests.Session()
    url = "http://" + vars.server + "/telebotAPI/check_assign"

    payload = {
        'message_id': mid,
    }
    u = x.post(url, data=payload, auth=AuthNew()).content
    # если ответ успешен, исключения задействованы не будут

    res = u.decode('UTF-8')
    logger.debug(res)
    return res