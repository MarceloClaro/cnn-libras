'''
@author Lucas Lacerda
@date 05/2019
'''
from keras.utils import to_categorical, plot_model
from keras.optimizers import SGD, Adam
from keras import backend
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping
from cnn import Convolucao

import datetime
import h5py
import time

def getDateStr():
        return str('{date:%d_%m_%Y_%H_%M}').format(date=datetime.datetime.now())

def getTimeMin(start, end):
        return (end - start)/60

EPOCHS = 50
CLASS = 21
FILE_NAME = 'cnn_model_LIBRAS_'

print("\n\n ----------------------INICIO --------------------------\n")
print('[INFO] [INICIO]: ' + getDateStr())
print('[INFO] Download dataset usando keras.preprocessing.image.ImageDataGenerator')

#https://www.pyimagesearch.com/2019/07/08/keras-imagedatagenerator-and-data-augmentation/

#Data augmentation encompasses a wide range of techniques used to generate “new” training samples from the original ones by applying random jitters and perturbations (but at the same time ensuring that the class labels of the data are not changed).

#Our goal when applying data augmentation is to increase the generalizability of the model.

train_datagen = ImageDataGenerator(
        rescale=1./255, #rescale: rescaling factor. Defaults to None. If None or 0, no rescaling is applied, otherwise we multiply the data by the value provided (after applying all other transformations).
        shear_range=0.2, #shear_range: Float. Shear Intensity (Shear angle in counter-clockwise direction in degrees)
        zoom_range=0.2, #zoom_range: Float or [lower, upper]. Range for random zoom. If a float, [lower, upper] = [1-zoom_range, 1+zoom_range].
        horizontal_flip=True, #Boolean. Randomly flip inputs horizontally.
        validation_split=0.25) #validation_split: Float. Fraction of images reserved for validation (strictly between 0 and 1).

'''
To reiterate the findings from researching the experts above, this section provides unambiguous definitions of the three terms.

Training Dataset: The sample of data used to fit the model.
Validation Dataset: The sample of data used to provide an unbiased evaluation of a model fit on the training dataset while tuning model hyperparameters. The evaluation becomes more biased as skill on the validation dataset is incorporated into the model configuration.
Test Dataset: The sample of data used to provide an unbiased evaluation of a final model fit on the training dataset.
'''

test_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.05)

# produz base de dados de treino gerada pelo modelo #
training_set = train_datagen.flow_from_directory(
        '../dataset/training',
        target_size=(64, 64),
        color_mode = 'rgb',
        batch_size=32,
        shuffle=True,
        #save_to_dir='../img_generator/train',
        class_mode='categorical')

#Takes the path to a directory & generates batches of augmented data.
test_set = test_datagen.flow_from_directory(
        '../dataset/test', #directory: string, path to the target directory. It should contain one subdirectory per class. Any PNG, JPG, BMP, PPM or TIF images inside each of the subdirectories directory tree will be included in the generator. See this script for more details.
        target_size=(64, 64),
        color_mode = 'rgb',
        batch_size=32,
        shuffle=True, #shuffle: Whether to shuffle the data (default: True) If set to False, sorts the data in alphanumeric order.
        #save_to_dir='../img_generator/test',
        class_mode='categorical')

# inicializar e otimizar modelo
print("[INFO] Inicializando e otimizando a CNN...")
start = time.time()

# This callback will stop the training when there is no improvement in
# the validation loss for three consecutive epochs.

#In deep learning, the loss is the value that a neural network is trying to minimize. That is how a neural network learns—by adjusting weights and biases in a manner that reduces the loss.
#loss and val_loss differ because the former is applied to the train set, and the latter the test set. As such, the latter is a good indication of how the model performs on unseen data.

#monitor	Quantity to be monitored.
#verbose	verbosity mode.
#mode	One of {"auto", "min", "max"}. In min mode, training will stop when the quantity monitored has stopped decreasing;
#patience	Number of epochs with no improvement after which training will be stopped.
early_stopping_monitor = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=15)

'''
The point of using a data set that you did not train on, is to measure how well your model is generalising to unseen records. Very often when building a predictive model, that is the main goal, and is actually more important than fitting to your training data (the fitting to data part is necessary for learning, but is not the goal). This is the case whenever you are building a model to use to make decisions on its predictions against new, previously unseen and unlabelled, data.

It is not safe to use the training data in the same role to check for generalisation. It is possible for many model types to learn the training data perfectly, but be terrible at predicting from new values that are not from the training set. This is something you will want to avoid, is often caused by overfitting, and neural networks will often overfit. Using a validation set is a way to monitor and help control against overfitting.

Neural networks (and other model types) typically use a validation set on every epoch, because training too long can cause over-fitting, and models don't recover from that, they just get worse form that point on. So it can save a lot of wasted effort to monitor validation loss, and stop training when it has not improved for a long while, or starts to get worse.
'''

#loss is the error evaluated during training a model, valloss is the error during validation. As Sibnick mentioned below, loss is compared against valloss and if loss is significantly lower the data is probably overfitted (regularization is the technique you will then used to generalize). Goal of Machine Learning is to generalize the data at the same time minimizing the loss & val_loss.

model = Convolucao.build(64, 64, 3, CLASS)

#An optimizer is one of the two arguments required for compiling a Keras model:
#Gradient descent (with momentum) optimizer.

#Categorical crossentropy is a loss function that is used for single label categorization. This is when only one category is applicable for each data point. In other words, an example can belong to one class only.
#Use categorical crossentropy in classification problems where only one result can be correct.
#​​Example:​ In the ​MNIST​​ problem where you have images of the numbers 0,1, 2, 3, 4, 5, 6, 7, 8, and 9. Categorical crossentropy gives the probability that an image of a number is, for example, a 4 or a 9.

#A metric is a function that is used to judge the performance of your model.
#Metric functions are similar to loss functions, except that the results from evaluating a metric are not used when training the model. Note that you may use any loss functions as a metric function.

model.compile(optimizer=SGD(0.01), loss="categorical_crossentropy",
              metrics=["accuracy"])

'''
By setting verbose 0, 1 or 2 you just say how do you want to 'see' the training progress for each epoch.

verbose=0 will show you nothing (silent)
verbose=1 will show you an animated progress bar
verbose=2 will just mention the number of epoch
'''
# treinar a CNN
print("[INFO] Treinando a CNN...")
classifier = model.fit_generator(
        training_set,
        #steps_per_epoch: Integer. Total number of steps (batches of samples) to yield from generator before declaring one epoch finished and starting the next epoch. It should typically be equal to ceil(num_samples / batch_size). Optional for Sequence: if unspecified, will use the len(generator) as a number of steps.
        #You can set it equal to num_samples // batch_size, which is a typical choice.
        steps_per_epoch=(training_set.n // training_set.batch_size),
        #Iteration is one time processing for forward and backward for a batch of images (say one batch is defined as 16, then 16 images are processed in one iteration). Epoch is once all images are processed one time individually of forward and backward to the network, then that is one epoch.
        epochs=EPOCHS,
        validation_data = test_set,
        validation_steps= (test_set.n // test_set.batch_size),
        #shuffle = False,
        verbose=2,
        callbacks = [early_stopping_monitor]
      )

# atualizo valor da epoca caso o treinamento tenha finalizado antes do valor de epoca que foi iniciado
EPOCHS = len(classifier.history["loss"])

print("[INFO] Salvando modelo treinado ...")

#para todos arquivos ficarem com a mesma data e hora. Armazeno na variavel
file_date = getDateStr()
model.save('../models/'+FILE_NAME+file_date+'.h5')
print('[INFO] modelo: ../models/'+FILE_NAME+file_date+'.h5 salvo!')

end = time.time()

print("[INFO] Tempo de execução da CNN: %.1f min" %(getTimeMin(start,end)))

print('[INFO] Summary: ')
model.summary()

print("\n[INFO] Avaliando a CNN...")
score = model.evaluate_generator(generator=test_set, steps=(test_set.n // test_set.batch_size), verbose=1)
print('[INFO] Accuracy: %.2f%%' % (score[1]*100), '| Loss: %.5f' % (score[0]))

print("[INFO] Sumarizando loss e accuracy para os datasets 'train' e 'test'")

plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0,EPOCHS), classifier.history["loss"], label="train_loss")
plt.plot(np.arange(0,EPOCHS), classifier.history["val_loss"], label="val_loss")
plt.plot(np.arange(0,EPOCHS), classifier.history["acc"], label="train_acc")
plt.plot(np.arange(0,EPOCHS), classifier.history["val_acc"], label="val_acc")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend()
plt.savefig('../models/graphics/'+FILE_NAME+file_date+'.png', bbox_inches='tight')

print('[INFO] Gerando imagem do modelo de camadas da CNN')
plot_model(model, to_file='../models/image/'+FILE_NAME+file_date+'.png', show_shapes = True)

print('\n[INFO] [FIM]: ' + getDateStr())
print('\n\n')
