# -*- coding: utf-8 -*-
import psycopg2
from urllib import parse
import os

parse.uses_netloc.append("postgres")
db_url = parse.urlparse(os.environ["DATABASE_URL"])


def connector():
    conn = psycopg2.connect(
        database=db_url.path[1:],
        user=db_url.username,
        password=db_url.password,
        host=db_url.hostname,
        port=db_url.port
    )
    cursor = conn.cursor()
    return cursor, conn


# memeses
def insert_memes(name, file_id=0, tags=""):
    cursor, conn = connector()

    try:
        cursor.execute("INSERT INTO public.memes (name, file_id, tags) VALUES (%s, %s, %s)", (name, file_id, tags,))
    except psycopg2.Error as e:
        print(e.pgerror)
    else:
        conn.commit()

    cursor.close()
    conn.close()


def update_memes_tags(name, tags):
    cursor, conn = connector()

    try:
        cursor.execute("UPDATE public.memes SET tags = (%s) where name = (%s)", (tags, name,))
    except psycopg2.Error as e:
        print(e.pgerror)
    else:
        conn.commit()

    cursor.close()
    conn.close()


def update_memes_file_id(name, file_id):
    cursor, conn = connector()

    try:
        cursor.execute("UPDATE public.memes SET file_id = (%s) where name = (%s)", (file_id, name,))
    except psycopg2.Error as e:
        print(e.pgerror)
    else:
        conn.commit()

    cursor.close()
    conn.close()


def get_memes_by_name(name):
    memes = db.query("SELECT * FROM public.memes WHERE name = '{0}'".format(name))
    if len(memes) != 0:
        return memes[0]["file_id"]
    else:
        return None


def get_memes_by_tag(tag):
    memes = db.query("SELECT * FROM public.memes WHERE '{0}' = ANY (tags)".format(tag))
    marray = []
    for m in memes:
        marray.append(m["file_id"])
    return marray


def get_last_memes():
    memes = db.query("SELECT * FROM public.memes ORDER BY number DESC LIMIT 6")
    marray = []
    for m in memes:
        marray.append(m["file_id"])
    return marray


def set_user_condition(uid, num_script, step):
    users = db.query("SELECT * FROM public.users WHERE uid = '{0}'".format(uid))
    if (len(users) != 0):
        update = db.prepare("UPDATE public.users SET (num_script, step) = ($2, $3) where uid = $1")
        update(uid, num_script, step)
    else:
        insert = db.prepare("INSERT INTO public.users (uid, num_script, step) VALUES ($1, $2, $3)")
        insert(uid, num_script, step)


def get_user_condition(uid):
    user = db.query("SELECT * FROM public.users WHERE uid = '{0}'".format(uid))
    if (len(user) != 0):
        return user[0]['num_script'], user[0]['step']
    else:
        return 0, 0


# scheduler
def check_alert():
    cursor, conn = connector()

    cursor.execute("SELECT sub_chat_id FROM subscribers")
    test_chat_id = cursor.fetchone()[0]
    cursor.execute("SELECT alert_day FROM subscribers")
    next_day = cursor.fetchone()[0]
    cursor.execute("SELECT today_mesg_id FROM subscribers")
    first_alert_message_id = cursor.fetchone()[0]
    cursor.execute("SELECT tomorrow_mesg_id FROM subscribers")
    second_alert_message_id = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return test_chat_id, next_day, first_alert_message_id, second_alert_message_id


def set_last_messages(f_a_m_id, s_a_m_id):
    cursor, conn = connector()

    try:
        cursor.execute("UPDATE subscribers SET today_mesg_id = (%s)", (f_a_m_id,))
    except psycopg2.Error as e:
        print(e.pgerror)
    else:
        conn.commit()
    try:
        cursor.execute("UPDATE subscribers SET tomorrow_mesg_id = (%s)", (s_a_m_id,))
    except psycopg2.Error as e:
        print(e.pgerror)
    else:
        conn.commit()

    cursor.close()
    conn.close()


def reschedule(next_day):
    cursor, conn = connector()

    try:
        cursor.execute("UPDATE subscribers SET alert_day = (%s)", (next_day,))
    except psycopg2.Error as e:
        print(e.pgerror)
    else:
        conn.commit()

    cursor.close()
    conn.close()
