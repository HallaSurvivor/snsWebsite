"""
Allow the website to send emails to its users
"""
from flask_mail import Message
from .models import User
import config

def send_email(subject, sender, recipients, body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = body

    mail.send(msg)

def welcome_notification(user):
    subject = "Welcome to the S'n'Website!!"

    body = """
        Thanks for joining us! Come visit the website to learn about what shows we have going on,
        and to audition for shows and programs yourself!
    """

    send_email(subject, config.MAIL_ADDRESS, [user.email], body)

def audition_reminder(audition):
    subject = "Remember: You have an audition for {0} today!".format(audition.show)

    # :time: is of the form "Day date HH:MM"
    body = "Friendly reminder that you have an audition for {show}!!!\n {time}!".format(
            show=audition.show, time=audition.time_str)

    user = User.query.filter_by(id=audition.user_id).first()

    send_email(subject, config.MAIL_ADDRESS, [user.email], body)
