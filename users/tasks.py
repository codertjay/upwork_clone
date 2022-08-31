import datetime

from celery import shared_task
from decouple import config
from post_office import mail

INSTASAW_INFO_MAIL = config("INSTASAW_INFO_MAIL")
INSTASAW_CUSTOMER_SUPPORT_MAIL = config("INSTASAW_CUSTOMER_SUPPORT_MAIL")


@shared_task
def login_notification_email(first_name, email):
    """this sends an email to the user once he logs in  """
    mail.send(
        email,
        INSTASAW_INFO_MAIL,
        subject='Login Notification',
        html_message=f"<h2>Hi {first_name},</h2> <p>We have detected a new login to your Instasaw App account as at"
                     f" {datetime.datetime.now()}</p>"
                     f"<p>For security reasons, we want to make sure it was you. If this action is done by you,"
                     f" kindly disregard this notice.</p> "
                     f"<p>If you did not login to your account, immediately change your password on the app and contact "
                     f"<a href='mailto:{INSTASAW_INFO_MAIL}'>{INSTASAW_INFO_MAIL}</a></p>",
        priority='now',
    )
    return True


@shared_task
def send_otp_to_email_task(otp, email, first_name, last_name):
    """
    This sends an email to the logged-in user for verification
    """
    mail.send(
        email,
        sender='no-reply@instasaw.co',
        subject="Instasaw App Request OTP",
        html_message=f"""
       <h3> Hello {first_name} {last_name} </h3>
       <p>
        Please use this OTP to complete your request:{otp}
        </br> If you haven't performed and action that requires an OTP please contact us
        </p>
        f"contact <a href='mailto:{INSTASAW_CUSTOMER_SUPPORT_MAIL}'>{INSTASAW_INFO_MAIL}</a></p>""",
        priority='now'
    )


