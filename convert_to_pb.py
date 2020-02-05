import tensorflow as tf
from nets.mobilenet import mobilenet_v2
from tensorflow.contrib import slim
from tensorflow.python.framework import graph_util
from tool_util import logger
import readdata

tf.app.flags.DEFINE_integer('num_classes', 2, '')
tf.app.flags.DEFINE_string('checkpoint_path', './classify/', '')

FLAGS = tf.app.flags.FLAGS


def freeze_graph(input_checkpoint: str, output_node: str = "output", output_pb: str = './test.pb'):
    '''
    :param input_checkpoint:
    :param output_node: output node name
    :param output_pb: save pb path
    :return:
    '''
    # output node name
    output_node_names = output_node
    with tf.get_default_graph().as_default():
        input_images = tf.placeholder(tf.float32, shape=[None, None, None, 3], name = 'input_images')

        input_images = readdata.mean_image_subtraction(input_images)

        # with slim.arg_scope(alexnet.alexnet_v2_arg_scope()):
        #     outputs, _ = alexnet.alexnet_v2(input_images, num_classes=FLAGS.num_classes, is_training=False)
        with slim.arg_scope(mobilenet_v2.training_scope()):
            outputs, end_points = mobilenet_v2.mobilenet(input_images, is_training=False, num_classes=FLAGS.num_classes)
        # with slim.arg_scope(resnet_v1.resnet_arg_scope(weight_decay=1e-5)):
            # outputs, end_points = resnet_v1.resnet_v1_50(input_images,  is_training=False, scope='resnet_v1_50', num_classes=FLAGS.num_classes)
            probs = tf.squeeze(end_points['Predictions'], name = 'mobilenet_output')

            saver = tf.train.Saver()
            with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
                ckpt_state = tf.train.get_checkpoint_state(FLAGS.checkpoint_path)
                saver.restore(sess, ckpt_state.model_checkpoint_path)
                graph = tf.get_default_graph()
                input_graph_def = graph.as_graph_def()
                logger.debug(input_graph_def)
                output_graph_def = graph_util.convert_variables_to_constants(sess=sess,
                                                                                input_graph_def=input_graph_def,
                                                                                output_node_names=output_node_names.split(","))
    
                with tf.gfile.GFile(output_pb, "wb") as f:
                    f.write(output_graph_def.SerializeToString())
                logger.debug("convert complete")

if __name__ == '__main__':
    input_checkpoint = FLAGS.checkpoint_path
    freeze_graph(input_checkpoint)