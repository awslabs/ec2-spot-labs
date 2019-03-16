import mxnet as mx

import numpy as np

import argparse

##Argument parser to take the input image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Predict image using mxnet on EI')
    parser.add_argument('--image', help='location of the image to be predicted', type=str, required=True)
    args = parser.parse_args()
    print ("Image: %s" % args.image )

image = args.image

#path='http://data.mxnet.io/models/imagenet/'

#[mx.test_utils.download(path+'resnet/50-layers/resnet-50-0000.params'),

#mx.test_utils.download(path+'resnet/50-layers/resnet-50-symbol.json'),

#mx.test_utils.download(path+'synset.txt')]


path = 'http://data.dmlc.ml/models/imagenet/squeezenet/'

[mx.test_utils.download(path+'squeezenet_v1.1-0000.params'),

mx.test_utils.download(path+'squeezenet_v1.1-symbol.json')]


ctx = mx.eia()



with open('synset.txt', 'r') as f:

  labels = [l.rstrip() for l in f]



sym, args, aux = mx.model.load_checkpoint('resnet-50', 0)



img = mx.image.imread(image)
<<<<<<< HEAD

=======
                                                                                                                                                      1,1           Top
>>>>>>> a9b1aae82201851ad741900b32ddf8ec2436676d
# convert into format (batch, RGB, width, height)

img = mx.image.imresize(img, 224, 224) # resize

img = img.transpose((2, 0, 1)) # Channel first

img = img.expand_dims(axis=0) # batchify

img = img.astype(dtype='float32')

args['data'] = img



softmax = mx.nd.random_normal(shape=(1,))

args['softmax_label'] = softmax



exe = sym.bind(ctx=ctx, args=args, aux_states=aux, grad_req='null')



exe.forward()

prob = exe.outputs[0].asnumpy()

# print the top-5

prob = np.squeeze(prob)

a = np.argsort(prob)[::-1]

for i in a[0:5]:

  print('probability=%f, class=%s' %(prob[i], labels[i]))
  