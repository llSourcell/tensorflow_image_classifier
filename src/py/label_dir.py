import errno
import tensorflow as tf
from shutil import move
from os import listdir, makedirs
from os.path import isfile, join, isdir

def mkdir_p(path):
    try:
        makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and isdir(path):
            pass
        else:
            raise


src_dir = '/toScan'
dest_dir = '/scanned'
img_files = [f for f in listdir(src_dir) if isfile(join(src_dir, f))]

# Loads label file, strips off carriage return
label_lines = [line.rstrip() for line
                   in tf.gfile.GFile('/tf_files/retrained_labels.txt')]

# Unpersists graph from file
with tf.gfile.FastGFile('/tf_files/retrained_graph.pb', 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

with tf.Session() as sess:
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    for image_file in img_files:
        src_image_path = join(src_dir, image_file)
        image_data =  tf.gfile.FastGFile(src_image_path, 'rb').read()

        print(src_image_path)
        predictions = sess.run(softmax_tensor, \
                 {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
        firstElt = top_k[0];

        label_dest_folder = join(dest_dir, label_lines[firstElt])
        mkdir_p(label_dest_folder)

        final_file_path = join(label_dest_folder, image_file)

        print(final_file_path)

        move(src_image_path, final_file_path)

        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[0][node_id]
            print('%s (score = %.5f)' % (human_string, score))
