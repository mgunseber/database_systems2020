from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import app
import os
import binascii
from server import cursor
from flask_login import login_user, logout_user, login_required
import db_init


# @app.route('/loginn')
# def login():
#    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_name = request.args.get('user_name')
    passw = request.args.get('passw')
    select_command = "SELECT user_ID FROM user_info WHERE (username = %s and password = %s) "
    cursor.execute(select_command, (user_name, passw))
    answer = cursor.fetchone()
    if answer is None:
        flash('Please check your login details and try again')
        return redirect(url_for('app.login'))
    else:
        session_id = binascii.b2a_hex(os.urandom(15))
        insert_command = "INSERT INTO session(session_ID, user_ID) VALUES (%s,%s)"
        cursor.execute(insert_command, (session_id, answer))
        cursor.commit()
        return redirect(url_for('app.profile'))

    return render_template("login.html")


@ app.route('/signup', methods=['POST'])
def signup():
    email = request.args.get('email')
    username = request.args.get('username')
    password = request.args.get('password')
    name = request.args.get('name')
    age = request.args.get('age')
    gender = request.args.get('gender')

    insert_command = "INSERT INTO user(username, password, email, name,age, gender, role) VALUES (%s,%s,%s,%s,%s,%s,%s) WHERE NOT EXISTS (SELECT username FROM user_info WHERE username = %s)"
    answer = cursor.execute(insert_command, (username, password,
                                             email, name, age, gender, 'user'), username)
    cursor.commit()
    if answer is None:
        flash('Email address already exists')
        return redirect(url_for('app.signup'))
    else:
        return redirect(url_for('app.login'))

    return render_template("signup.html")


@ app.route("/logout_page")
@login_required
def logout_page():
    logout_user()
    return redirect(url_for("app.home_page"))


@app.route("/sql", methods=["GET", "POST"])
def sql():
    sql = request.args.get("sql")
    cursor.execute(sql)
    data = cursor.fetchall()
    connection.commit()
    return str(data)
