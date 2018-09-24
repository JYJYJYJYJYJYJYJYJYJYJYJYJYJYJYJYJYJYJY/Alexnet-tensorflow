from alexnet import alexnet
import tensorflow as tf
import readdata
from tensorflow.contrib import slim
from tool_util import logger
import cv2
import time

#only support 224 in this alexnet
tf.app.flags.DEFINE_integer('input_size', 224, '')
tf.app.flags.DEFINE_string('test_image_path', './kaggle/test/','test images to use')
tf.app.flags.DEFINE_string('gpu_list', '0', '')
tf.app.flags.DEFINE_string('checkpoint_path', './classify/', '')
tf.app.flags.DEFINE_input_size('num_classes', 2, '')

FLAGS = tf.app.flags.FLAGS

def main(argv=None):
    import os
    os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu_list

    with tf.get_default_graph().as_default():
        input_images = tf.placeholder(tf.float32, shape=[None, None, None, 3], name = 'input_images')
        # global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable = False)
        saver = tf.train.Saver
        input_images = readdata.mean_image_subtraction(input_images)
        with slim.arg_scope(alexnet.alexnet_v2_arg_scope()):
            outputs, _ = alexnet.alexnet_v2(input_images, num_classes=FLAGS.num_classes)

            with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
                ckpt_state = tf.train.get_checkpoint_state(FLAGS.checkpoint_path)
                logger.info('Restore from {}'.format(FLAGS.checkpoint_path))
                saver.restore(sess, ckpt_state)

                image_list = readdata.get_images(FLAGS.test_image_path)
                for image_name in image_list:
                    im = cv2.imread(image_name)[:,:,::-1]

                    img = im.copy()

                    im_resized=cv2.resize(img, (FLAGS.input_size, FLAGS.input_size))
                    start_time = time.time()
                    outputs = sess.run([outputs], feed_dict={input_images:im_resized})

                    logger.info('detection time:{.0f}ms result:(cat:{.3f} dog:{.3f})'.format(
                        (time.time()-start_time)*1000, outputs[0], outputs[1]))

if __name__=='__main__':
    tf.app.run()






