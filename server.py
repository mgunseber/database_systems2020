import os

import db_init
from db_init import initialize

from flask import Flask, redirect, url_for, render_template, request, Blueprint, flash, Response, make_response

import psycopg2
import psycopg2 as dbapi2
from queries import select

from psycopg2 import Error
from psycopg2 import extensions

import binascii
from werkzeug.urls import url_parse
from operator import itemgetter

import ssl
import certifi
import requests
from bs4 import BeautifulSoup

from app import app
extensions.register_type(extensions.UNICODE)
extensions.register_type(extensions.UNICODEARRAY)



app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


os.environ['DATABASE_URL'] = "dbname='postgres' user='postgres' host='localhost' password='1234' port='5432'"
initialize(os.environ.get('DATABASE_URL'))


url = os.getenv("DATABASE_URL")
print(url)
connection = dbapi2.connect(url)
cursor = connection.cursor()

r = requests.get(
    "https://biletinial.com/tiyatro?date=&thisweekend=false&filmTypeId=")

source = BeautifulSoup(r.content, "lxml")


theater = source.find_all("div", attrs={"class": "eventContents"})
for e_property in theater:
    event_title = e_property.find(
        "div", attrs={"class": "flex fluid title"})
    event_loc = e_property.find("span", attrs={"class": "ml-5 locName"})
    event_date = e_property.find("div", attrs={"class": "eventDate flex"})

    eventName = str((event_title).text)
    eventLoc = str((event_loc).text)
    eventDate = str((event_date).text)
    eventDate = eventDate.strip()

    word = "theater"
    command_select = f"SELECT event_type_id FROM event_type_id WHERE (event_type = '{word}')"
    cursor.execute(command_select)
    answer = cursor.fetchone()

    command_INSERT = f"INSERT INTO event(event_name, location, date1, event_type_number) VALUES('{eventName}','{eventLoc}','{eventDate}',(SELECT event_type_id FROM event_type_id WHERE (event_type = '{word}')))"

    try:
        cursor.execute(command_INSERT)
    except:
        pass
    connection.commit()

r = requests.get(
    "https://www.zorlupsm.com/tr/takvim?searchQuery=&types=1&places=&fromDate=&toDate=")
source = BeautifulSoup(r.content, "lxml")

music = source.find_all("div", attrs={"class": "events-carousel__item__info"})
for e_property in music:
    event_title = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__title"})
    event_loc = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__footer__right"})
    event_date = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__subtitle"})
    eventName = str((event_title).text)
    eventLoc = str((event_loc).text)
    eventDate = str((event_date).text)
    eventDate = eventDate.strip()
    word = "music"
    command_select = f"SELECT event_type_id FROM event_type_id WHERE (event_type = '{word}')"
    cursor.execute(command_select)
    answer = cursor.fetchone()

    command_INSERT = f"INSERT INTO event(event_name, location, date1, event_type_number) VALUES('{eventName}','{eventLoc}','{eventDate}',(SELECT event_type_id FROM event_type_id WHERE (event_type = '{word}')))"

    try:
        cursor.execute(command_INSERT)
    except:
        pass
    connection.commit()

r = requests.get(
    "https://www.zorlupsm.com/tr/takvim?searchQuery=&types=18&places=&fromDate=&toDate=")
source = BeautifulSoup(r.content, "lxml")

online = source.find_all(
    "div", attrs={"class": "events-carousel__item__info"})
for e_property in online:
    event_title = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__title"})
    event_loc = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__footer__right"})
    event_date = e_property.find(
        "a", attrs={"class": "events-carousel__item__info__subtitle"})
    eventName = str((event_title).text)
    eventLoc = str((event_loc).text)
    eventDate = str((event_date).text)
    eventDate = eventDate.strip()
    word = "online"
    command_select = f"SELECT event_type_id FROM event_type_id WHERE (event_type = '{word}')"
    cursor.execute(command_select)
    answer = cursor.fetchone()

    command_INSERT = f"INSERT INTO event(event_name, location, date1, event_type_number) VALUES('{eventName}','{eventLoc}','{eventDate}',(SELECT event_type_id FROM event_type_id WHERE (event_type = '{word}')))"

    try:
        cursor.execute(command_INSERT)
    except:
        pass
    connection.commit()


@ app.route("/")
@ app.route("/home_page")
def home_page():
    cursor = connection.cursor()
    user = None
    cookie = request.cookies.get("session_id")
    if cookie is not None:
        try:
            search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
            cursor.execute(search_command)
            userid = cursor.fetchone()[0]
            search_command = f"SELECT user_id FROM user_info WHERE user_id = '{userid}'"
            cursor.execute(search_command)
            user = cursor.fetchone()[0]
        except:
            pass
    select_command = "SELECT event_name,date1,location,event_id FROM event"
    cursor.execute(select_command)
    event = cursor.fetchall()
    selected_events = []
    max_value = 0
    max_value_like = 0
    i = 0
    count = None
    like_count = None
    username = []
    most_active = []
    while (i < 7):
        selected_events.append(event[i])
        i += 1
    try:
        select_command_comment = "SELECT user_id,username, COUNT(*) as comment_count FROM user_info LEFT JOIN comment as l ON l.user_number=user_id GROUP BY user_id"
        cursor.execute(select_command_comment)
        comment_count = cursor.fetchall()
        for c in comment_count:
            count = [c[2]]
            if count[0] > max_value:
                max_value = count[0]
                username.append([c[1]])
        most_active.append(username[-1])
    except:
        pass

    try:
        select_command_comment = "SELECT user_id,username, COUNT(*) as like_count FROM user_info LEFT JOIN like_info as l ON l.user_num=user_id GROUP BY user_id"
        cursor.execute(select_command_comment)
        like_count = cursor.fetchall()
        for c in like_count:
            like_count = [c[2]]
            if like_count[0] > max_value_like:
                max_value_like = like_count[0]
                username.append([c[1]])
        most_active.append(username[-1])

    except:
        pass

    return render_template("home_page.html", selected_events=selected_events, most_active=most_active, user=user)


@app.route('/login_page')
def login1():
    user = None
    cookie = request.cookies.get("session_id")
    if cookie is not None:
        try:
            search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
            cursor.execute(search_command)
            userid = cursor.fetchone()[0]
            search_command = f"SELECT user_id FROM user_info WHERE user_id = '{userid}'"
            cursor.execute(search_command)
            user = cursor.fetchone()[0]
        except:
            pass

    return render_template('login.html', user=user)


@ app.route('/profile', methods=['POST', 'GET'])
def profile():
    userid = None
    try:
        cookie = request.cookies.get("session_id")
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]

    except:
        userid = None
    user = {}
    fav_type = []
    if userid is not None:
        search_command = f"SELECT username,name,age,email,gender FROM user_info WHERE user_id = {userid}"

        cursor.execute(search_command)
        answer = cursor.fetchone()

        user["user_id"] = userid
        user["username"] = answer[0]
        user["name"] = answer[1]
        user["age"] = answer[2]
        user["email"] = answer[3]
        user["gender"] = answer[4]
        search_command2 = f"SELECT event_num FROM like_info WHERE user_num = {userid}"
        cursor.execute(search_command2)
        eventid = cursor.fetchall()
        favevent = []
        suggestion = []
        eventlist = []
        for e in eventid:

            select_command = f"SELECT event_name,date1,location FROM event WHERE (event_id = {e[0]})"
            cursor.execute(select_command)
            favevent = cursor.fetchall()
            eventlist.append(favevent)

    elif userid is None:
        return redirect('/login')
    try:
        select_fav = f"SELECT event_type_id, event_type FROM favorite_type INNER JOIN event_type_id ON event_type_id.event_type_id = favorite_type.event_type_number WHERE user_info = {userid}"
        cursor.execute(select_fav)
        fav_type = cursor.fetchall()

        for f in fav_type:
            select_suggestion = f"SELECT event_name,date1,location FROM event WHERE event_type_number={f[0]} LIMIT 1"
            cursor.execute(select_suggestion)
            suggestion.append(cursor.fetchone())

    except:
        fav_type = None

    return render_template("profile.html", user=user, eventlist=eventlist, fav_type=fav_type, suggestion=suggestion)


@ app.route('/profileDelete', methods=['POST', 'GET'])
def profileDelete():
    user_id = request.args.get("user_id")
    cookie = request.cookies.get("session_id")
    response = make_response(redirect('/home_page'))

    if cookie is not None:
        delete_command1 = None
        delete_command2 = None
        delete_command3 = None
        delete_command4 = None
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]
        if userid == int(user_id):

            delete_command2 = f"DELETE FROM comment WHERE (user_number={user_id})"
            delete_command3 = f"DELETE FROM like_info WHERE (user_num={user_id})"
            delete_command1 = f"DELETE FROM session WHERE (userid={user_id})"
            delete_command5 = f"DELETE FROM favorite_type WHERE (user_info={user_id})"
            delete_command4 = f"DELETE FROM user_info WHERE (user_id={user_id})"

        if request.method == 'POST':
            try:
                cursor.execute(delete_command2)
                cursor.execute(delete_command3)
                cursor.execute(delete_command1)
                cursor.execute(delete_command5)
                cursor.execute(delete_command4)
            except Exception as e:
                print(e)
                pass
            connection.commit()
        response.delete_cookie('session_id')
        return response
    return redirect('/signup')


@ app.route('/fav_type', methods=['POST', 'GET'])
def fav_type():
    user_id = request.args.get("user_id")
    cookie = request.cookies.get("session_id")
    if cookie is not None:
        req = request.form
        if request.method == 'POST':
            music = req.get("music")
            theater = req.get("theater")
            online = req.get("online")
            other = req.get("other")

            try:
                if music is not None:
                    command = f"INSERT INTO favorite_type(user_info,event_type_number) VALUES({user_id},{2})"
                    cursor.execute(command)
                if theater is not None:
                    command = f"INSERT INTO favorite_type(user_info,event_type_number) VALUES({user_id},{1})"
                    cursor.execute(command)
                if online is not None:
                    command = f"INSERT INTO favorite_type(user_info,event_type_number) VALUES({user_id},{3})"
                    cursor.execute(command)
                if other is not None:
                    command = f"INSERT INTO favorite_type(user_info,event_type_number) VALUES({user_id},{4})"
                    cursor.execute(command)

            except:
                pass
            connection.commit()
    else:
        return redirect('/login')
    return redirect('/profile')


@ app.route('/profileUpdate', methods=['POST', 'GET'])
def profileUpdate():
    user_id = request.args.get("user_id")
    cookie = request.cookies.get("session_id")

    if cookie is not None:
        req = request.form
        if request.method == 'POST':
            username = req.get("username")
            name = req.get("name")
            age = req.get("age")
            email = req.get("email")
            gender = req.get("gender")

            update_command = f"UPDATE user_info SET username='{username}' , name='{name}' , age='{age}' , email='{email}' , gender='{gender}' WHERE (user_id = {user_id})"

        if request.method == 'POST':
            try:
                cursor.execute(update_command)
            except Exception as e:
                print(e)
                pass
            connection.commit()
    else:
        return redirect('/login')
    return redirect("/profile")


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

        session_number = binascii.b2a_hex(
            os.urandom(15)).decode(encoding='utf-8')
        insert_command = "INSERT INTO session(session_id, userid) VALUES (%s,%s)"
        cursor.execute(insert_command, (session_number, answer[0]))
        connection.commit()

        res = make_response(redirect('/profile'))
        res.set_cookie("session_id", session_number)
        return res

    except:
        flash('Please check your login details and try again')
        return redirect('/login_page')


@ app.route('/theater')
def theater_page():

    cookie = request.cookies.get("session_id")

    user = None

    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]
        user = {"user_id": userid}
        search_command = f"SELECT role FROM user_info WHERE user_id = {userid}"
        cursor.execute(search_command)
        role = cursor.fetchone()[0]
        user = {"role": role}

    select_command = "SELECT event_name,date1,location,event_id FROM event WHERE event_type_number = %s"
    cursor.execute(select_command, ("1"))
    event = cursor.fetchall()

    return render_template("theater.html", event=event, user=user)


@ app.route('/music')
def music_page():

    cookie = request.cookies.get("session_id")

    user = None

    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]
        user = {"user_id": userid}
        search_command = f"SELECT role FROM user_info WHERE user_id = {userid}"
        cursor.execute(search_command)
        role = cursor.fetchone()[0]
        user = {"role": role}

    select_command = "SELECT event_name,date1,location,event_id FROM event WHERE event_type_number = %s"
    cursor.execute(select_command, ("2"))
    event = cursor.fetchall()

    return render_template("music.html", event=event, user=user)


@ app.route('/online')
def online_page():

    cookie = request.cookies.get("session_id")

    user = None

    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]
        user = {"user_id": userid}
        search_command = f"SELECT role FROM user_info WHERE user_id = {userid}"
        cursor.execute(search_command)
        role = cursor.fetchone()[0]
        user = {"role": role}

    select_command = "SELECT event_name,date1,location,event_id FROM event WHERE event_type_number = %s"
    cursor.execute(select_command, ("3"))
    event = cursor.fetchall()

    return render_template("online.html", event=event, user=user)


@ app.route('/updateEvent', methods=['POST', 'GET'])
def theater_pageUpdate():
    event_id = request.args.get("event_id")
    cookie = request.cookies.get("session_id")
    location = None
    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]
        search_command = f"SELECT user_id FROM user_info WHERE user_id = '{userid}' and role = 'admin'"
        cursor.execute(search_command)
        userTuple = cursor.fetchone()
        if userTuple is not None:

            req = request.form
            if request.method == 'POST':
                location = req.get("location")
                print(location)

            update_command = f"UPDATE event SET location='{location}' WHERE (event_id = {event_id})"

            if request.method == 'POST':
                try:
                    cursor.execute(update_command)
                except Exception as e:
                    print(e)
                    pass
                connection.commit()

    return redirect(f'/theater?event_id={event_id}')


@ app.route('/other')
def other_page():
    return render_template("other.html")


@ app.route('/deleteEvent', methods=['POST', 'GET'])
def theater_pageDelete():
    event_id = request.args.get("event_id")
    cookie = request.cookies.get("session_id")
    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]
        search_command = f"SELECT user_id FROM user_info WHERE user_id = '{userid}' and role = 'admin'"
        cursor.execute(search_command)
        userTuple = cursor.fetchone()
        if userTuple is not None:

            delete_command1 = f"DELETE FROM comment WHERE (event_number = {event_id})"
            delete_command2 = f"DELETE FROM like_info WHERE (event_num = {event_id})"
            delete_command3 = f"DELETE FROM event WHERE (event_id = {event_id})"

        if request.method == 'POST':
            try:
                cursor.execute(delete_command1)
                cursor.execute(delete_command2)
                cursor.execute(delete_command3)
            except Exception as e:
                print(e)
                pass
            connection.commit()

    else:
        return redirect('/login')
    return redirect(f'/theater?event_id={event_id}')


@ app.route('/signup', methods=['GET'])
def signup1():
    user = None
    try:
        cookie = request.cookies.get("session_id")
        if cookie is not None:
            search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
            cursor.execute(search_command)
            userid = cursor.fetchone()[0]
            search_command = f"SELECT user_id FROM user_info WHERE user_id = '{userid}'"
            cursor.execute(search_command)
            user = cursor.fetchone()[0]
    except:
        pass
    return render_template("signup.html", user=user)


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
        cursor.execute(insert_command, (username, password,
                                        email, name, age, gender, "user"))
        connection.commit()
    except:
        flash('Try again')
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

    response.delete_cookie('session_id')
    return response


@ app.route("/like")
def like():

    event_id = request.args.get("event_id")
    cookie = request.cookies.get("session_id")
    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        answer = cursor.fetchone()[0]

    elif cookie is None:
        return redirect('/login')
    try:
        insert_command = "INSERT INTO like_info(event_num,user_num) VALUES(%s,%s)"
        cursor.execute(insert_command, (event_id, answer))

    except:
        pass
    connection.commit()
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

    comment_id = request.args.get("comment_id")
    cookie = request.cookies.get("session_id")

    answer = None
    if cookie is not None:
        search_command = f"SELECT userid FROM session WHERE session_id = '{cookie}'"
        cursor.execute(search_command)
        userid = cursor.fetchone()[0]

        search_command = f"SELECT user_id FROM user_info WHERE user_id = '{userid}' and role = 'admin'"
        cursor.execute(search_command)
        userTuple = cursor.fetchone()

        req = request.form
        if request.method == 'POST':
            comment = req.get("comment")
            print(comment)

        if userTuple is None:
            update_command = f"UPDATE comment SET comment='{comment}' WHERE (user_number = {userid} and comment_id = {comment_id})"

        else:
            update_command = f"UPDATE comment SET comment={answer} WHERE (comment_id = {comment_id})"

        if request.method == 'POST':
            try:
                cursor.execute(update_command)
            except Exception as e:
                print(e)
                pass
            connection.commit()
    else:
        return redirect('/login')

    return redirect(f"/event?event_id={event_id}")


if __name__ == "__main__":
    app.secret_key = 'mysecretkey'
    app.run(debug=True)
