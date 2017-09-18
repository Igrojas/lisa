from gi.repository import Notify

Notify.init("Lisa")

def notify(sentence):
    Notify.Notification.new(sentence).show()
