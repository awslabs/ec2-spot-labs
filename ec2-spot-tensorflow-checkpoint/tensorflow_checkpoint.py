 # Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy of this
 # software and associated documentation files (the "Software"), to deal in the Software
 # without restriction, including without limitation the rights to use, copy, modify,
 # merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 # permit persons to whom the Software is furnished to do so.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 # INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 # PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import tensorflow as tf
import boto3,shutil,os,re
import botocore
from botocore.exceptions import ClientError
import glob
s3 = boto3.resource('s3')

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    if not bucket_exists(bucket):
      s3.create_bucket(Bucket=bucket)
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        return False
    return True

def downloadfile(bucket,max_to_keep):
    """Download checkpoint files from an S3 bucket
    :param bucket: Bucket to upload to
    :param max_to_keep: number of checkpoints
    """
    # select bucket
    my_bucket = s3.Bucket(bucket)
    # download file into current directory
    file_list = []
    for s3_object in my_bucket.objects.all():
        # Need to split s3_object.key into path and file name, else it will give error file not found.
        path, filename = os.path.split(s3_object.key)
        if filename == 'checkpoint':
            my_bucket.download_file(s3_object.key, s3_object.key)
            f = open(s3_object.key)
            line = f.readline()
            f.close()
            batch = int(re.findall('\d+',line)[0])
            for x in range(batch-max_to_keep,batch+1):
                file_list.append(x)
        else:
            if int(re.findall('\d+',filename)[0]) in file_list:
                my_bucket.download_file(s3_object.key, s3_object.key)

class Net(tf.keras.Model):
  """A simple linear model."""

  def __init__(self):
    super(Net, self).__init__()
    self.l1 = tf.keras.layers.Dense(5)

  def call(self, x):
    return self.l1(x)

def toy_dataset():
  inputs = tf.range(10.)[:, None]
  labels = inputs * 5. + tf.range(5.)[None, :]
  return tf.data.Dataset.from_tensor_slices(
    dict(x=inputs, y=labels)).repeat().batch(2)

def train_step(net, example, optimizer):
  """Trains `net` on `example` using `optimizer`."""
  with tf.GradientTape() as tape:
    output = net(example['x'])
    loss = tf.reduce_mean(tf.abs(output - example['y']))
  variables = net.trainable_variables
  gradients = tape.gradient(loss, variables)
  optimizer.apply_gradients(zip(gradients, variables))
  return loss


def train_and_checkpoint(net, manager):
  ckpt.restore(manager.latest_checkpoint).expect_partial()
  if manager.latest_checkpoint:
    print("Restored from {}".format(manager.latest_checkpoint))
  else:
    print("Initializing from scratch.")
  for _ in range(5000):
    example = next(iterator)
    loss = train_step(net, example, opt)
    ckpt.step.assign_add(1)
    if int(ckpt.step) % 10 == 0:
        save_path = manager.save()
        list_of_files = glob.glob('tf_ckpts/*.index')
        latest_file = max(list_of_files, key=os.path.getctime)
        upload_file(latest_file, 'pythontfckpt', object_name=None)
        list_of_files = glob.glob('tf_ckpts/*.data*')
        latest_file = max(list_of_files, key=os.path.getctime)
        upload_file(latest_file, 'pythontfckpt', object_name=None)
        upload_file('tf_ckpts/checkpoint', 'pythontfckpt', object_name=None)
        print("Saved checkpoint for step {}: {}".format(int(ckpt.step), save_path))
        print("loss {:1.2f}".format(loss.numpy()))


def bucket_exists(bucket_name):
    bucket = s3.Bucket(bucket_name)
    exists = True
    try:
      s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
      # If a client error is thrown, then check that it was a 404 error.
      # If it was a 404 error, then the bucket does not exist.
      error_code = e.response['Error']['Code']
      if error_code == '404':
        exists = False
    return exists

if __name__ == '__main__':
    if bucket_exists('pythontfckpt'):
        print("Re-Launching Job")
        os.mkdir('tf_ckpts')
        downloadfile('pythontfckpt',3)
    net = Net()
    opt = tf.keras.optimizers.Adam(0.1)
    dataset = toy_dataset()
    iterator = iter(dataset)
    ckpt = tf.train.Checkpoint(step=tf.Variable(1), optimizer=opt, net=net, iterator=iterator)
    manager = tf.train.CheckpointManager(ckpt, './tf_ckpts', max_to_keep=3)
    train_and_checkpoint(net, manager)
