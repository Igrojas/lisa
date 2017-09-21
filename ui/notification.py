from gi.repository import Notify, GdkPixbuf

name = "Lisa"
Notify.init(name)

def notify(sentence):
    notification = Notify.Notification.new(sentence)
    image = GdkPixbuf.Pixbuf.new_from_file("data/avatar/img.png")
    notification.set_image_from_pixbuf(image)
    notification.show()
