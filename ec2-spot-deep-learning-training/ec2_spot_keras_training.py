#%% Import packages
import numpy as np
import os
import keras
from keras.callbacks import ModelCheckpoint, CSVLogger
from keras.layers import Input, Dense, Flatten
from keras.models import Model, load_model
from download_cifar10 import load_data
import shutil
import datetime
import time
import requests
import glob


#%% Load and prepare datasets
def load_prepare_dataset(dataset_path):

    # Utility function that downloads and then loads if data doesn't already exist
    (x_train, y_train), (x_test, y_test) = load_data(dataset_path)

    # Normalize data.
    x_train = x_train.astype('float32') / 255
    x_test = x_test.astype('float32') / 255

    # Subtract pixel mean
    x_train_mean = np.mean(x_train, axis=0)
    x_train -= x_train_mean
    x_test -= x_train_mean

    # Convert class vectors to binary class matrices.
    y_train = keras.utils.to_categorical(y_train, len(np.unique(y_test)))
    y_test = keras.utils.to_categorical(y_test, len(np.unique(y_test)))

    return (x_train, y_train), (x_test, y_test)

#%% Define model
def cifar10_model(input_shape):

    input_tensor = Input(shape=input_shape)
    base_model = keras.applications.resnet50.ResNet50(include_top=False,
                                                      weights='imagenet',
                                                      input_tensor=input_tensor,
                                                      input_shape=input_shape,
                                                      classes=None)

    x = base_model.output
    x = Flatten()(x)
    predictions = Dense(10, activation='softmax')(x)
    mdl = Model(inputs=base_model.input, outputs=predictions)
    mdl.summary()
    return mdl


#%%
def load_checkpoint_model(checkpoint_path, checkpoint_names):
    list_of_checkpoint_files = glob.glob(os.path.join(checkpoint_path, '*'))
    checkpoint_epoch_number = max([int(file.split(".")[1]) for file in list_of_checkpoint_files])
    checkpoint_epoch_path = os.path.join(checkpoint_path,
                                         checkpoint_names.format(epoch=checkpoint_epoch_number))
    resume_model = load_model(checkpoint_epoch_path)
    return resume_model, checkpoint_epoch_number

#%%
def define_callbacks(volume_mount_dir, checkpoint_path, checkpoint_names, today_date):

    # Model checkpoint callback
    if not os.path.isdir(checkpoint_path):
        os.makedirs(checkpoint_path)
    filepath = os.path.join(checkpoint_path, checkpoint_names)
    checkpoint_callback = ModelCheckpoint(filepath=filepath,
                                          save_weights_only=False,
                                          monitor='val_loss')

    # Loss history callback
    epoch_results_callback = CSVLogger(os.path.join(volume_mount_dir, 'training_log_{}.csv'.format(today_date)),
                                       append=True)

    class SpotTermination(keras.callbacks.Callback):
        def on_batch_begin(self, batch, logs={}):
            status_code = requests.get("http://169.254.169.254/latest/meta-data/spot/instance-action").status_code
            if status_code != 404:
                time.sleep(150)
    spot_termination_callback = SpotTermination()

    callbacks = [checkpoint_callback, epoch_results_callback, spot_termination_callback]
    return callbacks


#%%
def main():

    # Training parameters
    batch_size = 512
    epochs = 50
    volume_mount_dir = '/dltraining/'
    dataset_path = os.path.join(volume_mount_dir, 'datasets')
    checkpoint_path = os.path.join(volume_mount_dir, 'checkpoints')
    checkpoint_names = 'cifar10_model.{epoch:03d}.h5'
    today_date = datetime.datetime.today().strftime('%Y-%m-%d')

    # Load dataset
    (x_train, y_train), (x_test, y_test) = load_prepare_dataset(dataset_path)
    input_shape = x_train.shape[1:]

    # Load model
    if os.path.isdir(checkpoint_path) and any(glob.glob(os.path.join(checkpoint_path, '*'))):
        model, epoch_number = load_checkpoint_model(checkpoint_path, checkpoint_names)
    else:
        model = cifar10_model(input_shape)
        epoch_number = 0

    # Define Callbacks
    callbacks = define_callbacks(volume_mount_dir, checkpoint_path, checkpoint_names, today_date)

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, initial_epoch=epoch_number, callbacks=callbacks)

    # Score trained model.
    scores = model.evaluate(x_test, y_test, verbose=1)
    print('Test loss:', scores[0])
    print('Test accuracy:', scores[1])

    # Backup terminal output once training is complete
    shutil.copy2('/var/log/cloud-init-output.log', os.path.join(volume_mount_dir,
                                                                'cloud-init-output-{}.log'.format(today_date)))


if __name__ == "__main__":
    main()


