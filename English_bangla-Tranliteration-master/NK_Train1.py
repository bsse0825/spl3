import NK_Model1
import environment1
import sys
import time
import string
import numpy as np
import os
from sklearn.model_selection import train_test_split
import tensorflow as tf
tf.enable_eager_execution()

if len(sys.argv) >= 2:
    env = environment1.envionmrnt_mode(sys.argv[1])
else:
    env = environment1.envionmrnt_mode("none")
training_dataset_path = env['training_dataset_path']
#TODO: need to get sample count dynamicaly
num_examples = 5401


def load_doc(filename):
  # open the file as read only
  file = open(filename, mode="r", encoding="utf-8")
  # read all text
  text = file.read()
  # close the file
  file.close()
  return text


text = load_doc("phonem_onlycharecters.txt")
splittedLines = text.splitlines()

count = 0
tar_word2idx = {}
tar_idx2word = {}
#tar_word2idx['<pad>'] = 0
for i in range(0, len(splittedLines)):
  line = splittedLines[i]
  word = line.split("\t")
  if tar_word2idx.get(word[0]) == None:
      tar_word2idx[word[0]] = int(word[1])
  count = count + 1

tar_word2idx['<start>'] = count + 1
tar_word2idx['<end>'] = count + 2

for word, index in tar_word2idx.items():
  tar_idx2word[index] = word


text2 = load_doc("englishLetter.txt")
english_splittedLines = text2.splitlines()

count = 0
inp_word2idx = {}
inp_idx2word = {}
#inp_word2idx['<pad>'] = 0
for i in range(0, len(english_splittedLines)):
  line = english_splittedLines[i]
  word = line.split("\t")

  if inp_word2idx.get(word[0]) == None:
      inp_word2idx[word[0]] = word[1]
  count = count + 1

inp_word2idx['<start>'] = count + 1
inp_word2idx['<end>'] = count + 2

for word, index in inp_word2idx.items():
  inp_idx2word[index] = word


# input_tensor = banglish word
# target_tensor = bangla word (leveling)
# max_length_inp = banglish word max length
# max_length_targ = bangla word max length
input_tensor, target_tensor, max_length_inp, max_length_targ = NK_Model1.load_dataset(
    training_dataset_path, num_examples)


print("max_length_inp = ", max_length_inp,
      " \tmax_length_targ ==", max_length_targ)

# spliting data set into training(90%) and testing(10%)
input_tensor_train, input_tensor_val, target_tensor_train, target_tensor_val = train_test_split(
    input_tensor, target_tensor, test_size=0.0)


# TODO: add coment
BUFFER_SIZE = len(input_tensor_train)
BATCH_SIZE = env["BATCH"]
N_BATCH = BUFFER_SIZE//BATCH_SIZE
embedding_dim = 256
units = 1024

# TODO: add coment
vocab_inp_size = len(inp_word2idx) + 1
vocab_tar_size = len(tar_word2idx) + 1


dataset = tf.data.Dataset.from_tensor_slices(
    (input_tensor_train, target_tensor_train)).shuffle(BUFFER_SIZE)
dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)
encoder = NK_Model1.Encoder(vocab_inp_size, embedding_dim, units, BATCH_SIZE)
decoder = NK_Model1.Decoder(vocab_tar_size, embedding_dim, units, BATCH_SIZE)
optimizer = tf.train.AdamOptimizer()

# TODO: add coment


def loss_function(real, pred):
    mask = 1 - np.equal(real, 0)
    loss_ = tf.nn.sparse_softmax_cross_entropy_with_logits(
        labels=real, logits=pred) * mask
    return tf.reduce_mean(loss_)


checkpoint_dir = env["MODEL_PATH"]
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
checkpoint = tf.train.Checkpoint(optimizer=optimizer,
                                 encoder=encoder,
                                 decoder=decoder)

# TODO: add coment
EPOCHS = env["EPOCH"]


# START TRAINING
for epoch in range(EPOCHS):
    start = time.time()

    hidden = encoder.initialize_hidden_state()
    total_loss = 0

    for (batch, (inp, targ)) in enumerate(dataset):
        loss = 0

        with tf.GradientTape() as tape:
            enc_output, enc_hidden = encoder(inp, hidden)
            dec_hidden = enc_hidden
            #dec_input = tf.expand_dims([targ_lang.word2idx['<start>']] * BATCH_SIZE, 1)
            dec_input = tf.expand_dims(
                [tar_word2idx['<start>']] * BATCH_SIZE, 1)

            # Teacher forcing - feeding the target as the next input
            for t in range(1, targ.shape[1]):
                # passing enc_output to the decoder
                predictions, dec_hidden, _ = decoder(
                    dec_input, dec_hidden, enc_output)
                loss += loss_function(targ[:, t], predictions)

                # using teacher forcing
                dec_input = tf.expand_dims(targ[:, t], 1)

        batch_loss = (loss / int(targ.shape[1]))

        total_loss += batch_loss

        variables = encoder.variables + decoder.variables
        gradients = tape.gradient(loss, variables)
        optimizer.apply_gradients(zip(gradients, variables))
        if batch % 100 == 0:
            print('Epoch {} Batch {} Loss {:.4f}'.format(epoch + 1,
                                                         batch,
                                                         batch_loss.numpy()))

    if (epoch + 1) % 10 == 0:
        checkpoint.save(file_prefix=checkpoint_prefix)

    print('Epoch {} Loss {:.4f}'.format(epoch + 1,
                                        total_loss / N_BATCH))
   # print("START TIME = ",start)
    print('Time taken for 1 epoch {} sec\n'.format(time.time() - start))
