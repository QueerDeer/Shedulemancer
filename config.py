# -*- coding: utf-8 -*-

token = "545213183:AAF2vAqvhV_YTgP-LUZrV3vsBkF6iNbNWJA"

# enumeration of scenarios
S_ADD_MEMES = 1

# enumeration of steps, while adding memeses
S_START = 0
S_ENTER_NAME = 1
S_ENTER_TAGS = 2
S_SEND_PIC = 3

# scheduler
TEST_MY_ID = 363412185  # my test chat (not group, tet-a-tet)
SUBSCRIBERS_HOUR = 5

# hard useful shit
LESSONS = [
    '10:15 — 13:30 К-923\nСтатистические методы обработки информации (доп.главы)\nОвсянникова Н.В.\n\n14:30 — 17:00 Д-304\nЦифровые динамические системы\nКтитров С.В.',
    'Отдыхаем',
    '10:15 — 12:40 К-923\nЦифровые динамические системы\nКтитров С.В\n\n13:35 — 16:05 К-923\n(нечетные) Статистические методы обработки информации (доп. главы)\nОвсянникова Н.В.\n(четные) Теория игр и исследование операций (доп. главы) Коновалов Р.В., Кулябичев Ю.П.\n\n16:15 — 18:40 (нечетные) К-822, (четные) К-307\nСтандартизация информационных технологий\nСтепанова Е.Б.',
    '10:15 — 13:30 В-407\nВеб-программирование\nЛеонова Н.М.\n\n14:30 — 17:00 K-822\n(четные) Учебная (научно-исследовательская) практика\n(нечетные) Стандартизация информационных технологий\nСтепанова Е.Б.',
    '08:30 — 10:05 каф.20\nВоенная подготовка\n\n10:15 — 17:00 каф.20\nВоенная подготовка',
    '09:20 — 12:40 Д-312\nТеория игр и исследование операций (доп. главы)\nКоновалов Р.В., Кулябичев Ю.П.\n\n14:30 — 17:50 Д-304\nМатематическое обеспечение систем специального назначения\nПивторацкая С.В.',
    'Отдыхаем']
CALENDAR_VOCABULARY = {
    '/today': -1,
    '/today@mephi_shed_bot': -1,
    '/tomorrow': 0,
    '/tomorrow@mephi_shed_bot': 0,

    '/mon': 0,
    '/mon@mephi_shed_bot': 0,
    '/tue': 1,
    '/tue@mephi_shed_bot': 1,
    '/wed': 2,
    '/wed@mephi_shed_bot': 2,
    '/thu': 3,
    '/thu@mephi_shed_bot': 3,
    '/fri': 4,
    '/fri@mephi_shed_bot': 4,
    '/sat': 5,
    '/sat@mephi_shed_bot': 5,
    '/sun': 6,
    '/sun@mephi_shed_bot': 6
}

# # deleting previous notification
# TEST_CHAT_ID = 0
# NEXT_DAY = 0
# FIRST_ALERT_MESSAGE_ID = 0
# SECOND_ALERT_MESSAGE_ID = 0
