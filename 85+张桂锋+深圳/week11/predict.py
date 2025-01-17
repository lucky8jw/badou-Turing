import numpy as np
import utils
import cv2
from AlexNet import AlexNet
from tensorflow.keras import backend as K
K.set_image_data_format('channels_last')


if __name__ == "__main__":
    model = AlexNet()
    model.load_weights("./logs/ep036-loss0.002-val_loss1.165.h5")
    img = cv2.imread("./Test.jpg")
    img_RGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img_nor = img_RGB/255
    img_nor = np.expand_dims(img_nor,axis = 0)
    img_resize = utils.resize_image(img_nor,(224,224))
    utils.print_answer(np.argmax(model.predict(img_resize)))
    #print(utils.print_answer(np.argmax(model.predict(img_resize))))
    cv2.imshow("ooo",img)
    cv2.waitKey(0)