# -*- coding: utf-8 -*-
import postgresql

db =  postgresql.open('pq://postgres:justdoit@localhost:5432/telegramm') #вынести в config.py, разбить на отдельные части

def insert_memes(name, file_id=0, tags=""):
      insert = db.prepare("INSERT INTO public.memes (name, file_id, tags) VALUES ($1, $2, $3)")
      insert(name, file_id, tags)

def update_memes_tags(name, tags):
        update = db.prepare("UPDATE public.memes SET tags = $2 where name = $1")
        update(name, tags)

def update_memes_file_id(name, file_id):
        update = db.prepare("UPDATE public.memes SET file_id = $2 where name = $1")
        update(name, file_id)


def get_memes_by_name(name):
      memes = db.query("SELECT * FROM public.memes WHERE name = '{0}'".format(name))
      if len(memes) !=0:
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
    if(len(users) != 0):
        update = db.prepare("UPDATE public.users SET (num_script, step) = ($2, $3) where uid = $1")
        update(uid, num_script, step)
    else:
        insert = db.prepare("INSERT INTO public.users (uid, num_script, step) VALUES ($1, $2, $3)")
        insert(uid, num_script, step)

def get_user_condition(uid):
    user = db.query("SELECT * FROM public.users WHERE uid = '{0}'".format(uid))
    if(len(user) != 0):
        return user[0]['num_script'], user[0]['step']
    else:
        return 0,0