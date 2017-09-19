from vision.darknet import look_imagenet, look_coco

def look(image):
    labels = set()
    labels.update(look_imagenet(image))
    labels.update(look_coco(image))
    return labels
