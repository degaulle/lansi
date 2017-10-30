from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from flask import jsonify
from functools import wraps
from flask_mail import Mail, Message


#sends a confirmation email to a given user_email
def sendConfirmationEmail(mail, user_email, ability, time, essay_text):
    msg = Message('Lansi | Your Request Has Been Submitted', sender = 'peerifybot@gmail.com', recipients = [user_email])
    msg.html = "<p>Congratulations, your request was successfully submitted! Here are the details we received from you:</p>" + \
    "<p>Level of Chinese ability:" + ability + "</p>" + \
    "<p>Requested Time: " + time + "</p>" + \
    "<p>Info about yourself:</p>" + \
    essay_text + \
    "<br><p>You should receive a response as soon as there is someone within your time interval. We will pair you with a suitable match soon!</p>" + \
    "<p>With Love,</p>" + \
    "<p>Lansi</p>"
    mail.send(msg)


#sends a email notification upon pairing to a given emailAddress given mail (initiated Mail(app)), topic, and requested return date.
def sendPairingEmail(mail, email_address, topic, return_date):
    msg = Message('Peerify | You Have Been Matched!', sender = 'peerifybot@gmail.com', recipients = [email_address])
    msg.html = "<p>We have matched your essay on " + topic + " with a suitable peer!</p>" + \
    "<p>Your partner requests that you read and leave feedback on their essay by <b>" + return_date + "</b> (and they will also read yours by the designated date!).</p>" + \
    "<p>Happy reading!</p>" +\
    "<p>With Love,</p>" + \
    "<p>Peerify Bot</p>"
    mail.send(msg)
