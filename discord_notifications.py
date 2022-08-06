from gi.repository import GLib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import time


def notifications(bus, message):
    the_list = []
    current_time = None
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
        current_time = time.strftime('%Y-%m-%d %I:%M:%S%p', time.localtime())
        print(f"{who} / {current_time} - {message}")
        print('----------------------------')
        glib.IO_OUT = False


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()
    bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'")
    bus.add_message_filter(notifications)

    mainloop = GLib.MainLoop()
    mainloop.run()
