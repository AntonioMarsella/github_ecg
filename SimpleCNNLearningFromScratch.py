# code below is based on Cats & Dogs (https://www.kaggle.com/ddt2036/cat-dog-demo)
import cv2
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import itertools
from keras import Sequential
from keras.layers import *
from keras.callbacks import *


#constant value
VALID_SPIT = 0.2
IMAGE_SIZE = 64
BATCH_SIZE = 128
CHANNEL_SIZE = 1

# Simple CNN model with 4 convolutional layers and max_pooling
model=Sequential()
model.add(Conv2D(8, (3, 3), input_shape=(IMAGE_SIZE, IMAGE_SIZE, CHANNEL_SIZE), activation='relu', padding='same'))
model.add(MaxPooling2D())

model.add(Conv2D(16, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D())

model.add(Conv2D(32, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D())

model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D())

model.add(Flatten())
model.add(Dropout(0.5))
model.add(Dense(100,activation="relu"))
model.add(Dense(1,activation="sigmoid"))

model.summary()


# Resize data to 64x64 and convert it to grayscale
# (which speeds up learning significantly)
label=[]
data=[]
counter=0
path="../cwt_classes/N"
for file in os.listdir(path):
    image_data=cv2.imread(os.path.join(path,file), cv2.IMREAD_GRAYSCALE)
    image_data=cv2.resize(image_data,(IMAGE_SIZE,IMAGE_SIZE))
    label.append(0)
    try:
        data.append(image_data/255)
    except:
        label=label[:len(label)-1]
    counter+=1
    if counter%1000==0:
        print (counter," image data retreived")

counter=0
path="../cwt_classes/A"
for file in os.listdir(path):
    image_data=cv2.imread(os.path.join(path,file), cv2.IMREAD_GRAYSCALE)
    image_data=cv2.resize(image_data,(IMAGE_SIZE,IMAGE_SIZE))
    label.append(1)
    try:
        data.append(image_data/255)
    except:
        label=label[:len(label)-1]
    counter+=1
    if counter%1000==0:
        print (counter," image data retreived")


data = np.array(data)
data = data.reshape((data.shape)[0],(data.shape)[1],(data.shape)[2],1)
label = np.array(label)
print(data.shape)
print(label.shape)

# Split in train and valid subsets
from sklearn.model_selection import train_test_split
train_data, valid_data, train_label, valid_label = train_test_split(
    data, label, test_size=0.2, random_state=42)
print(train_data.shape)
print(train_label.shape)
print(valid_data.shape)
print(valid_label.shape)

# training
model.compile(optimizer='adam',loss="binary_crossentropy", metrics=["accuracy"])

callack_saver = ModelCheckpoint(
            "model_2.h5"
            , monitor='val_loss'
            , verbose=0
            , save_weights_only=True
            , mode='auto'
            , save_best_only=True
        )

train_history = model.fit(train_data, train_label, validation_data=(valid_data, valid_label), epochs=20, batch_size=BATCH_SIZE, callbacks=[callack_saver])

def show_train_history(train_history, train, validation):
    plt.plot(train_history.history[train])
    plt.plot(train_history.history[validation])
    plt.title('Train History')
    plt.ylabel(train)
    plt.xlabel('Epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.show()

show_train_history(train_history, 'loss', 'val_loss')
show_train_history(train_history, 'acc', 'val_acc')


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


# Predict the values from the validation dataset
Y_pred = model.predict(valid_data)
predicted_label=np.round(Y_pred,decimals=2)
predicted_label=[1 if value>0.5 else 0 for value in predicted_label]
confusion_mtx = confusion_matrix(valid_label, predicted_label)
# plot the confusion matrix
plot_confusion_matrix(confusion_mtx, classes = range(2))

