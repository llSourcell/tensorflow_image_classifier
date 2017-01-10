import tensorflow as tf
import sys

# change this as you see fit
#image_path = sys.argv[1]

# Read in the image_data
#image_data = tf.gfile.FastGFile(image_path, 'rb').read()
import os
import shutil
from os import listdir
from os import mkdir
from shutil import copyfile
from os.path import isfile, join
var_path = '/toScan'
dest_dir = '/scanned'
img_files = [f for f in listdir(var_path) if isfile(join(var_path, f))]


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
    #try:
    #    shutil.rmtree(dest_dir)
    #except:
    #    None
    #mkdir ('scanned')

    for image_file in img_files:
        src_image_path = join(var_path, image_file)
        image_data =  tf.gfile.FastGFile(src_image_path, 'rb').read()

        print src_image_path
        predictions = sess.run(softmax_tensor, \
                 {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
        firstElt = top_k[0];

        new_file_name = label_lines[firstElt] +'--'+ str(predictions[0][firstElt])[2:7]+'.jpg'
        print(new_file_name)
        copyfile(src_image_path, join(dest_dir, new_file_name))

        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[0][node_id]
            #print (node_id)
            print('%s (score = %.5f)' % (human_string, score))
