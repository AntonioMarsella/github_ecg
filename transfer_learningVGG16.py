from keras.applications import vgg16
from keras.layers.core import Flatten
from keras.models import Model
from keras.layers import Dense
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from sklearn.metrics import confusion_matrix


# create the base pre-trained model
base_model = vgg16.VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.summary()

# let's visualize layer names and layer indices to see how many layers
# we should freeze:
for i, layer in enumerate(base_model.layers):
   print(i, layer.name)

# add last layers for 2 cross-entropy classification
# standard VGG16 ones: Flatten and two fully-connected with ReLU
# final softmax for 2 classes with cross-entropy
x = base_model.output
x = Flatten()(x)
x = Dense(4096, activation='relu', name='fc1')(x)
x = Dense(4096, activation='relu', name='fc2')(x)
# and a logistic layer -- we have 2 classes
predictions = Dense(2, activation='softmax', name='predictions')(x)

# this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)

model.summary()

# transfer learning:
# freeze those layers that should not be retrained
# up to 7th layer (see visualizations)
for layer in model.layers[:7]:
   layer.trainable = False
for layer in model.layers[7:]:
   layer.trainable = True

# compile the model (should be done *after* setting layers to non-trainable)
model.compile(optimizer='Adam', loss='categorical_crossentropy')

train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0,
        zoom_range=0,
        horizontal_flip=False,
        validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
    directory="../cwt_classes/",
    target_size=(224, 224),
    color_mode="rgb",
    batch_size=32,
    class_mode="categorical",
    shuffle=True,
    seed=42,
    subset='training'
    )

valid_generator = train_datagen.flow_from_directory(
    directory="../cwt_classes/", # same directory as training data
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation') # set as validation data

STEP_SIZE_TRAIN = train_generator.samples//train_generator.batch_size
STEP_SIZE_VALID = valid_generator.samples//valid_generator.batch_size

# train the model on the new data for a few epochs
model.fit_generator(generator=train_generator,
                    steps_per_epoch=STEP_SIZE_TRAIN,
                    validation_data=valid_generator,
                    validation_steps=STEP_SIZE_VALID,
                    epochs=30)

model.save('VGG16_From7LayerModel.h5')

#Confution Matrix
Y_pred = model.predict_generator(valid_generator, valid_generator.n // valid_generator.batch_size+1)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
print(confusion_matrix(valid_generator.classes, y_pred))


