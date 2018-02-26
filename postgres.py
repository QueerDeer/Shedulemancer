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
    cursor, conn = connector()

    cursor.execute("SELECT * FROM public.memes WHERE name = (%s)", (name,))  #
    memes = cursor.fetchall()
    cursor.close()
    conn.close()

    if len(memes) != 0:
        return memes[0]["file_id"]
    else:
        return None


def get_memes_by_tag(tag):
    cursor, conn = connector()

    cursor.execute("SELECT * FROM public.memes WHERE (%s) = ANY (tags)", (tag,))  #
    memes = cursor.fetchall()
    marray = []

    for m in memes:
        marray.append(m["file_id"])

    cursor.close()
    conn.close()
    return marray


def get_last_memes():
    cursor, conn = connector()

    cursor.execute("SELECT * FROM public.memes ORDER BY number DESC LIMIT 6")
    memes = cursor.fetchall()
    marray = []

    for m in memes:
        marray.append(m["file_id"])

    cursor.close()
    conn.close()
    return marray


def set_user_condition(uid, num_script, step):
    cursor, conn = connector()

    cursor.execute("SELECT * FROM public.users WHERE uid = (%s)", (uid,))  #
    users = cursor.fetchall()

    if (len(users) != 0):
        try:
            cursor.execute("UPDATE public.users SET (num_script, step) = (%s, %s) where uid = %s",
                           (num_script, step, uid,))
        except psycopg2.Error as e:
            print(e.pgerror)
        else:
            conn.commit()

    else:
        try:
            cursor.execute("INSERT INTO public.users (uid, num_script, step) VALUES (%s, %s, %s)",
                           (uid, num_script, step,))
        except psycopg2.Error as e:
            print(e.pgerror)
        else:
            conn.commit()

    cursor.close()
    conn.close()


def get_user_condition(uid):
    cursor, conn = connector()

    cursor.execute("SELECT * FROM public.users WHERE uid = (%s)", (uid,))  #
    user = cursor.fetchall()
    cursor.close()
    conn.close()

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
