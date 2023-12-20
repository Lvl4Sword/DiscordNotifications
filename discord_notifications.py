import datetime
import smtplib
import ssl
from email.headerregistry import Address
from email.message import EmailMessage
import dbus
import pytz
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from jinja2 import Template


alert_email = 'WOAH THERE BUDDY'
email_password = 'NO WAY JOSE'
send_email_here = ['PUT', 'EMAILS', 'HERE']
email_domain = 'mail.example.com'
email_port = 465


def get_timezone():
    with open('/etc/timezone', 'r') as timezone_file:
        the_system_timezone = timezone_file.read()
    return the_system_timezone


def email_this(the_time, the_person, the_message):
    to_these = send_email_here
    msg = EmailMessage()
    msg.set_content = ''
    jinja_email_template = """<html>
        <head></head>
        <body>
            <b>Time:</b> {{the_time}}</br>
            <b>Who:</b> {{the_person}}</br>
            <b>What:</b> {{the_message}}</br>
        <body>
    </html>
    """
    message_body = jinja_email_template
    data = {'the_time': the_time,
            'the_person': the_person,
            'the_message': the_message}
    prep_template = Template(message_body)
    msg.add_alternative(prep_template.render(data), subtype='html')
    msg['Subject'] = f'[ALERT: Discord]'
    msg['From'] = alert_email
    msg['To'] = [Address(to_these[index],
                         each.split('@')[0],
                         each.split('@')[1]) for index, each in enumerate(to_these)]
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    # No need to set verify_mode, it's done for us:
    # https://docs.python.org/3/library/ssl.html#ssl.create_default_context
    ssl_context.check_hostname = True
    ssl_context.set_ciphers('ECDHE-RSA-AES256-GCM-SHA384')
    ssl_context.options |= ssl.HAS_SNI
    ssl_context.options |= ssl.OP_NO_COMPRESSION
    # No need to explicitly disable SSLv* as it's already been done
    # https://docs.python.org/3/library/ssl.html#id7
    # ssl_context.options |= ssl.OP_NO_TLSv1
    # ssl_context.options |= ssl.OP_NO_TLSv1_1
    ssl_context.options |= ssl.OP_SINGLE_DH_USE
    ssl_context.options |= ssl.OP_SINGLE_ECDH_USE
    with smtplib.SMTP_SSL(email_domain, port=email_port, context=ssl_context) as conn:
        conn.esmtp_features['auth'] = 'PLAIN'
        conn.login(alert_email, email_password)
        conn.send_message(msg)


def notifications(bus, message):
    the_list = []
    current_time_raw = datetime.datetime.now().astimezone(pytz.timezone(the_timezone))
    current_time = current_time_raw.strftime(f'%Y-%m-%d %I:%M:%S%p')
    for arg in message.get_args_list():
        if isinstance(arg, dbus.String):
            if arg != '':
                if len(the_list) == 0:
                    if arg == 'discord':
                        the_list.append(arg)
                else:
                    the_list.append(arg)
    if len(the_list) == 3:
        who = the_list[1]
        message = the_list[2].replace('\n', ' -- ')
        print(f"{current_time} / {who} - {message}")
        email_this(current_time, who, message)
        glib.IO_OUT = False
        the_list = []


if __name__ == '__main__':
    the_timezone = get_timezone().strip()
    try:
        DBusGMainLoop(set_as_default=True)

        bus = dbus.SessionBus()
        bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications'")
        bus.add_message_filter(notifications)

        mainloop = GLib.MainLoop()
        mainloop.run()
    except Exception as e:
        current_time_raw = datetime.datetime.now().astimezone(pytz.timezone(the_timezone))
        current_time = current_time_raw.strftime(f'%Y-%m-%d %I:%M:%S%p')
        print(f"Exception occured @ {current_time} -- Return code: {e.returncode} / Output: {e.output}")
