import tensorflow as tf

filename_queue = tf.train.string_input_producer(["collector/changes.csv"])

reader = tf.TextLineReader()
key, value = reader.read(filename_queue)

# Default values, in case of empty columns. Also specifies the type of the
# decoded result.
record_defaults = [[""], [""], [""], [""], [""], [""]]
deletions, insertions, changeid, project, verified, accountid = tf.decode_csv(
    value, record_defaults=record_defaults)
# Stacking columns together (test)
features = tf.stack([deletions, insertions, verified])

with tf.Session() as sess:
    # Start populating the filename queue.
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    for i in range(1200):
        # Retrieve a single instance:
        example, label = sess.run([features, project])
        print(example, label)

    coord.request_stop()
    coord.join(threads)
