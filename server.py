import os

import db_init
from db_init import initialize

from flask import Flask, redirect, url_for, render_template, request, Blueprint, flash, Response, make_response
from flask_login import LoginManager
import psycopg2
import psycopg2 as dbapi2
from queries import select

from psycopg2 import Error
from psycopg2 import extensions
from flask_login import login_user, logout_user, login_required
import binascii
from werkzeug.urls import url_parse

import ssl
import certifi
import requests
from bs4 import BeautifulSoup
from flask_login import login_required, UserMixin
from app import app
extensions.register_type(extensions.UNICODE)
extensions.register_type(extensions.UNICODEARRAY)
lm = LoginManager(app)
lm.login_view = 'login'
lm.init_app(app)


# class User(UserMixin, db.Model):


"""@lm.user_loader
def load_user(user_ID):  # it will return null if ID is invalid
    return User.get(user_ID)
"""


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# app.config['TESTING'] = False


#HEROKU = False

# if(not HEROKU):
#os.environ['DATABASE_URL'] = "dbname='postgres' user='postgres' host='localhost' password='1234' port='5432'"
# initialize(os.environ.get('DATABASE_URL'))
# pass

url = os.getenv("DATABASE_URL")
print(url)
connection = dbapi2.connect(url)
cursor = connection.cursor()

r = requests.get(
    "https://biletinial.com/tiyatro?date=&thisweekend=false&filmTypeId=")

source = BeautifulSoup(r.content, "lxml")

# cursor = connection.cursor()

theater = source.find_all("div", attrs={"class": "eventContents"})
for e_property in theater:
    event_title = e_property.find(
        "div", attrs={"class": "flex fluid title"})
    event_loc = e_property.find("span", attrs={"class": "ml-5 locName"})
    event_date = e_property.find("div", attrs={"class": "eventDate flex"})
    # event_price = teather.find("div", attrs={"class": "flex fluid title"})
    eventName = str((event_title).text)
    eventLoc = str((event_loc).text)
    eventDate = str((event_date).text)
    eventDate = eventDate.strip()
    # print(eventDate)
    word = "theater"
    command_select = f"SELECT event_type_id FROM event_type_id WHERE (event_type = '{word}')"
    cursor.execute(command_select)
    answer = cursor.fetchone()
    # print(answer)
    command_INSERT = f"INSERT INTO event(event_name, location, date1, event_type_number) VALUES('{eventName}','{eventLoc}','{eventDate}',(SELECT event_type_id FROM event_type_id WHERE (event_type = '{word}')))"
    # cursor.execute("INSERT INTO a_table (c1, c2, c3) VALUES(%s, %s, %s)", (v1, v2, v3))

    try:
        cursor.execute(command_INSERT)
    except:
        pass
    connection.commit()


@ app.route("/")
@ app.route("/home_page")
def home_page():
    select_command = "SELECT event_name,date1,location,event_id FROM event"
    cursor.execute(select_command)
    event = cursor.fetchall()
    selected_events = []
    i = 0
    while (i < 7):
        selected_events.append(event[i])
        i += 1

    return render_template("home_page.html", selected_events=selected_events)


@app.route('/login_page')
def login1():
    return render_template('login.html')


@ app.route('/profile')
def profile():
    try:
        cookie = request.cookies.get("session_id")
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        # print(type(cookie))
        cursor.execute(search_command)
        userid = cursor.fetchone()
        print(userid)
    except:
        userid = None
    user = None
    if userid is not None:
        search_command = f"SELECT username,name,age,email,gender FROM user_info WHERE user_id = {userid[0]}"

        cursor.execute(search_command)
        answer = cursor.fetchone()
        user = {}
        user["username"] = answer[0]
        user["name"] = answer[1]
        user["age"] = answer[2]
        user["email"] = answer[3]
        user["gender"] = answer[4]
        search_command2 = f"SELECT event_num FROM like_info WHERE user_num = {userid[0]}"
        cursor.execute(search_command2)
        eventid = cursor.fetchall()
        favevent = []
        print(eventid)
        eventlist = []
        for e in eventid:

            select_command = f"SELECT event_name,date1,location FROM event WHERE (event_id = {e[0]})"
            cursor.execute(select_command)
            favevent = cursor.fetchall()
            eventlist.append(favevent)

    elif userid is None:
        return redirect('/login')
    print(user)
    return render_template("profile.html", user=user, eventlist=eventlist)


@ app.route('/login', methods=['GET', 'POST'])
def login():

    req = request.form
    username = req.get("username")
    password = req.get("password")

    answer = None
    try:
        select_command = "SELECT user_id FROM user_info WHERE username = %s and password = %s "
        cursor.execute(select_command, (username, password))

        answer = cursor.fetchone()
        print(answer)
        session_number = binascii.b2a_hex(
            os.urandom(15)).decode(encoding='utf-8')
        insert_command = "INSERT INTO session(session_id, userid) VALUES (%s,%s)"
        cursor.execute(insert_command, (session_number, answer[0]))
        connection.commit()
        print("a")
        res = make_response(redirect('/profile'))
        res.set_cookie("session_id", session_number)
        return res

    except:
        flash('Please check your login details and try again')
        # connection.rollback()
        return redirect('/login_page')

    # return render_template("login.html")


@ app.route('/theater')
def theater_page():
    select_command = "SELECT event_name,date1,location,event_id FROM event WHERE event_type_number = %s"
    cursor.execute(select_command, ("1"))
    event = cursor.fetchall()

    # cursor.commit()
    return render_template("theater.html", event=event)


@ app.route('/signup', methods=['GET'])
def signup1():
    return render_template("signup.html")


@ app.route('/signup', methods=['POST', 'GET'])
def signup():
    req = request.form
    if request.method == 'POST':
        email = req.get("email")
        username = req.get("username")
        password = req.get("password")
        name = req.get("name")
        age = req.get("age")
        gender = req.get("gender")
        print(email)
    try:
        insert_command = "INSERT INTO user_info(username, password, email, name,age, gender, role) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        # WHERE NOT EXISTS (SELECT username FROM user_info WHERE username = %s)"
        cursor.execute(insert_command, (username, password,
                                        email, name, age, gender, "user"))
        connection.commit()
    except:
        flash('Email address already exists')
        connection.rollback()
        return redirect(url_for('signup'))
    else:
        return redirect(url_for('login'))

    return render_template("signup.html")


@ app.route("/logout_page")
def logout_page():
    response = make_response(redirect('/home_page'))
    try:
        cookie = request.cookies.get("session_id")

        delete_command = "DELETE FROM session WHERE session_id = %s"
        cursor.execute(delete_command, (cookie))
        connection.commit()
    except:
        flash('Login first to logout')
    # session id yi sil
    response.delete_cookie('session_id')
    return response


@ app.route("/like")
def like():

    event_id = request.args.get("event_id")
    cookie = request.cookies.get("session_id")
    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        answer = cursor.fetchone()

    elif cookie is None:
        return redirect('/login')
    try:
        insert_command = "INSERT INTO like_info(event_num,user_num) VALUES(%s,%s)"
        cursor.execute(insert_command, (event_id, answer[0]))
        connection.commit()
    except:
        pass
    return redirect('/profile')


@ app.route("/comment", methods=['GET'])
def comment():
    return render_template("event.html")


@ app.route("/event", methods=['POST', 'GET'])
def event():
    event_id = request.args.get("event_id")
    cookie = request.cookies.get("session_id")
    commentlist = []
    selectcommand = f"SELECT event_name,date1,location FROM event WHERE (event_id = {event_id})"
    cursor.execute(selectcommand)
    event = cursor.fetchall()
    print(event)

    user = None

    comments = []
    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]
        user = {"user_id": userid}

        req = request.form
        if request.method == 'POST':
            comment = req.get("comment")
            print(comment)
            print(comment)

            try:
                insert_command = "INSERT INTO comment(event_number,user_number,comment) VALUES(%s,%s,%s)"
                cursor.execute(insert_command, (event_id, userid, comment))
                connection.commit()
            except:
                pass

    else:
        return redirect('/login')
    try:
        select_command = f"SELECT comment,comment_id,event_number,user_number,e.username,e.user_id,e.role from comment INNER JOIN user_info as e ON e.user_id = user_number WHERE event_number = {event_id}"
        cursor.execute(select_command)
        commentlist = cursor.fetchall()
        for c in commentlist:
            comments.append({
                "comment": c[0],
                "comment_id": c[1],
                "event_number": c[2],
                "user_number": c[3],
                "user": {
                    "username": c[4],
                    "user_id": c[5],
                    "role": c[6]
                }
            })

        """cursor.execute(select_command)
        commentlist = cursor.fetchall()
        select_command = f"SELECT user_info.username from comment RIGHT JOIN user_info ON comment.user_number = user_info.user_id WHERE user_number={userid[0]}"
        cursor.execute(select_command)
        username2 = cursor.fetchone()
        select_command = f"SELECT comment.comment WHERE event_number = {event_id}, user_info.username from comment RIGHT JOIN user_info ON comment.user_number = user_info.user_id WHERE user_number={userid[0]}"
        cursor.execute(select_command)
        username1 = cursor.fetchall()
        print(username1)"""
        #username = username1[0]

    except:
        pass

    return render_template('event.html', comments=comments, event_id=event_id, event=event, user=user)


@ app.route("/deleteComment", methods=['POST', 'GET'])
def delete_event():
    event_id = request.args.get("event_id")
    comment_id = request.args.get("comment_id")
    cookie = request.cookies.get("session_id")

    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]

        search_command = f"SELECT user_id FROM user_info WHERE user_id = '{userid}' and role = 'admin'"
        cursor.execute(search_command)
        userTuple = cursor.fetchone()
        if userTuple is None:
            delete_command = f"DELETE FROM comment WHERE (user_number = {userid} and comment_id = {comment_id})"
        else:
            delete_command = f"DELETE FROM comment WHERE (comment_id = {comment_id})"

        if request.method == 'POST':
            try:
                cursor.execute(delete_command)
            except Exception as e:
                print(e)
                pass
            connection.commit()

    else:
        return redirect('/login')

    return redirect(f"/event?event_id={event_id}")


@ app.route("/updateComment", methods=['POST', 'GET'])
def update_comment():
    event_id = request.args.get("event_id")
    #user_id = request.args.get("user_id")
    cookie = request.cookies.get("session_id")
    commentU = {}
    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()
        req = request.form
        if request.method == 'POST':
            answer = req.get("comment")
            commentU["userid"] = userid[0]
            commentU["text"] = answer
        if request.method == 'POST':
            try:
                update_command = f"UPDATE comment SET comment={answer} WHERE (user_id = {userid[0]})"
                cursor.execute(update_command)
            except:
                pass

    else:
        return redirect('/login')

    return render_template("event.html", event_id=event_id, commentU=commentU, userid=userid)


if __name__ == "__main__":
    app.secret_key = 'mysecretkey'
    app.run(debug=True)
