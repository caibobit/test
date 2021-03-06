import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
from PIL import Image

train_epochs = 35  ## int(1e5+1)

INPUT_HEIGHT = 28
INPUT_WIDTH = 28

batch_size = 256

noise_factor = 0.5  ## (0~1)

## 原始输入是28×28*3
input_x = tf.placeholder(tf.float32, [None, INPUT_HEIGHT * INPUT_WIDTH], name='input_with_noise')
input_matrix = tf.reshape(input_x, shape=[-1, INPUT_HEIGHT, INPUT_WIDTH, 1])
input_raw = tf.placeholder(tf.float32, shape=[None, INPUT_HEIGHT * INPUT_WIDTH], name='input_without_noise')

## 1 conv layer
## 输入28*28*3
## 经过卷积、激活、池化，输出14*14*64
weight_1 = tf.Variable(tf.truncated_normal(shape=[3, 3, 1, 64], stddev=0.1, name = 'weight_1'))
bias_1 = tf.Variable(tf.constant(0.0, shape=[64], name='bias_1'))
conv1 = tf.nn.conv2d(input=input_matrix, filter=weight_1, strides=[1, 1, 1, 1], padding='SAME')
conv1 = tf.nn.bias_add(conv1, bias_1, name='conv_1')
acti1 = tf.nn.relu(conv1, name='acti_1')
pool1 = tf.nn.max_pool(value=acti1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME', name='max_pool_1')

## 2 conv layer
## 输入14*14*64
## 经过卷积、激活、池化，输出7×7×64
weight_2 = tf.Variable(tf.truncated_normal(shape=[3, 3, 64, 64], stddev=0.1, name='weight_2'))
bias_2 = tf.Variable(tf.constant(0.0, shape=[64], name='bias_2'))
conv2 = tf.nn.conv2d(input=pool1, filter=weight_2, strides=[1, 1, 1, 1], padding='SAME')
conv2 = tf.nn.bias_add(conv2, bias_2, name='conv_2')
acti2 = tf.nn.relu(conv2, name='acti_2')
pool2 = tf.nn.max_pool(value=acti2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME', name='max_pool_2')

## 3 conv layer
## 输入7*7*64
## 经过卷积、激活、池化，输出4×4×32
## 原始输入是28*28*3=2352，转化为4*4*32=512，大量噪声会在网络中过滤掉
weight_3 = tf.Variable(tf.truncated_normal(shape=[3, 3, 64, 32], stddev=0.1, name='weight_3'))
bias_3 = tf.Variable(tf.constant(0.0, shape=[32]))
conv3 = tf.nn.conv2d(input=pool2, filter=weight_3, strides=[1, 1, 1, 1], padding='SAME')
conv3 = tf.nn.bias_add(conv3, bias_3)
acti3 = tf.nn.relu(conv3, name='acti_3')
pool3 = tf.nn.max_pool(value=acti3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME', name='max_pool_3')

## 1 deconv layer
## 输入4*4*32
## 经过反卷积，输出7*7*32
deconv_weight_1 = tf.Variable(tf.truncated_normal(shape=[3, 3, 32, 32], stddev=0.1), name='deconv_weight_1')
deconv1 = tf.nn.conv2d_transpose(value=pool3, filter=deconv_weight_1, output_shape=[batch_size, 7, 7, 32], strides=[1, 2, 2, 1], padding='SAME', name='deconv_1')

## 2 deconv layer
## 输入7*7*32
## 经过反卷积，输出14*14*64
deconv_weight_2 = tf.Variable(tf.truncated_normal(shape=[3, 3, 64, 32], stddev=0.1), name='deconv_weight_2')
deconv2 = tf.nn.conv2d_transpose(value=deconv1, filter=deconv_weight_2, output_shape=[batch_size, 14, 14, 64], strides=[1, 2, 2, 1], padding='SAME', name='deconv_2')

## 3 deconv layer
## 输入14*14*64
## 经过反卷积，输出28*28*64
deconv_weight_3 = tf.Variable(tf.truncated_normal(shape=[3, 3, 64, 64], stddev=0.1, name='deconv_weight_3'))
deconv3 = tf.nn.conv2d_transpose(value=deconv2, filter=deconv_weight_3, output_shape=[batch_size, 28, 28, 64], strides=[1, 2, 2, 1], padding='SAME', name='deconv_3')

## conv layer
## 输入28*28*64
## 经过卷积，输出为28*28*1
weight_final = tf.Variable(tf.truncated_normal(shape=[3, 3, 64, 1], stddev=0.1, name = 'weight_final'))
bias_final = tf.Variable(tf.constant(0.0, shape=[1], name='bias_final'))
conv_final = tf.nn.conv2d(input=deconv3, filter=weight_final, strides=[1, 1, 1, 1], padding='SAME')
conv_final = tf.nn.bias_add(conv_final, bias_final, name='conv_final')

## output
## 输入28*28*1
## reshape为28*28
output = tf.reshape(conv_final, shape=[-1, INPUT_HEIGHT * INPUT_WIDTH])

## loss and optimizer
loss = tf.reduce_mean(tf.pow(tf.subtract(output, input_raw), 2.0))
optimizer = tf.train.AdamOptimizer(0.01).minimize(loss)


with tf.Session() as sess:

    mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
    n_samples = int(mnist.train.num_examples)
    print('train samples: %d' % n_samples)
    print('batch size: %d' % batch_size)
    total_batch = int(n_samples / batch_size)
    print('total batchs: %d' % total_batch)
    init = tf.global_variables_initializer()
    sess.run(init)
    for epoch in range(train_epochs):
        for batch_index in range(total_batch):
            batch_x, _ = mnist.train.next_batch(batch_size)
            noise_x = batch_x + noise_factor * np.random.randn(*batch_x.shape)
            noise_x = np.clip(noise_x, 0., 1.)
            _, train_loss = sess.run([optimizer, loss], feed_dict={input_x: noise_x, input_raw: batch_x})
            print('epoch: %04d\tbatch: %04d\ttrain loss: %.9f' % (epoch + 1, batch_index + 1, train_loss))

    ## 训练结束后，用测试集测试，并保存加噪图像、去噪图像
    n_test_samples = int(mnist.test.num_examples)
    test_total_batch = int(n_test_samples / batch_size)
    for i in range(test_total_batch):
        batch_test_x, _ = mnist.test.next_batch(batch_size)
        noise_test_x = batch_test_x + noise_factor * np.random.randn(*batch_test_x.shape)
        noise_test_x = np.clip(noise_test_x, 0., 1.)
        test_loss, pred_result = sess.run([loss, conv_final], feed_dict={input_x: noise_test_x, input_raw: batch_test_x})
        print('test batch index: %d\ttest loss: %.9f' % (i + 1, test_loss))
        for index in range(batch_size):
            array = np.reshape(pred_result[index], newshape=[INPUT_HEIGHT, INPUT_WIDTH])
            array = array * 255
            image = Image.fromarray(array)
            if image.mode != 'L':
                image = image.convert('L')
            image.save('./pred/' + str(i * batch_size + index) + '.png')
            array_raw = np.reshape(noise_test_x[index], newshape=[INPUT_HEIGHT, INPUT_WIDTH])
            array_raw = array_raw * 255
            image_raw = Image.fromarray(array_raw)
            if image_raw.mode != 'L':
                image_raw = image_raw.convert('L')
            image_raw.save('./pred/' + str(i * batch_size + index) + '_raw.png')
