#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 15:19:15 2019

@author: tushar
"""
from __future__ import absolute_import, division, print_function

# Import TensorFlow >= 1.10 and enable eager execution
import environment1
import time
import string
import os
import numpy as np
import re
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import tensorflow as tf
import sys

tf.enable_eager_execution()


print(tf.__version__)


if len(sys.argv) >= 2:
  env = environment1.envionmrnt_mode(sys.argv[1])
else:
    env = environment1.envionmrnt_mode("none")


#path_to_file ="data.txt"
path_to_file = env["training_dataset_path"]


def load_doc(filename):
  # open the file as read only
  file = open(filename, mode="r", encoding="utf-8")
  # read all text
  text = file.read()
  # close the file
  file.close()
  return text


#text = load_doc("phonem.txt")
text = load_doc("phonem_onlycharecters.txt")
splittedLines = text.splitlines()
#print(len(splittedLines))

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
  #if index == 1423:
  # print('hell')

text2 = load_doc("englishLetter.txt")
english_splittedLines = text2.splitlines()
#print(len(english_splittedLines))
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
  #print(type(index))
  break
  #print (word, " >> ", index)


print(" banglisg input word2idx['<start>'] >>", inp_word2idx['<start>'])
print("input word2idx['<end>'] >> ", inp_word2idx['<end>'])
print('input word2idx length >> ', len(inp_word2idx))
print("input idx2word  length >> ", len(inp_idx2word))

print("Bangla target word2idx['<start>'] >>", tar_word2idx['<start>'])
print("target word2idx['<end>'] >> ", tar_word2idx['<end>'])
print('target word2idx length >> ', len(tar_word2idx))
print("target idx2word  length >> ", len(tar_idx2word))


def bangla_word_to_sequence_transformation(w):
  word = w
  for key in tar_word2idx:
      temp_word = word.replace(key, str(tar_word2idx[key])+",")
      word = temp_word
  # After sequence generation in case any bangla character remains
  # replace this character with
  word = re.sub('[^0-9,]', '0,', word)
  return word


def english_word_to_sequence_transformation(w):
  word = w
  for key in inp_word2idx:
      temp_word = word.replace(key, str(inp_word2idx[key])+",")
      #print(key, "\t",english_encountered_words[key],"\t",word)
      word = temp_word
  #a = 'l,kdfhi123,23,আম,soe78347834 (())&/&745  '
  #result = re.sub('[^0-9,]','0,', a)
  word = re.sub('[^0-9,]', '0,', word)
  return word

# Converts the unicode file to ascii


def unicode_to_ascii(s):
  return ''.join(c for c in unicodedata.normalize('NFD', s)
                 if unicodedata.category(c) != 'Mn')


def preprocess_sentence(w):
  # w = unicode_to_ascii(w.lower().strip())

  # creating a space between a word and the punctuation following it
  # eg: "he is a boy." => "he is a boy ."
  # Reference:- https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
  #w = re.sub(r"([?.!,¿])", r" \1 ", w)
  w = re.sub(r'[" "]+', " ", w)

  # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
#    w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)

  w = english_word_to_sequence_transformation(w)

  w = w.rstrip().strip()

  # adding a start and an end token to the sentence
  # so that the model know when to start and stop predicting.
  w = '<start> ' + w + ' <end>'
  return w


def preprocess_pair_word_sentence(w):
  # w = unicode_to_ascii(w.lower().strip())

  # creating a space between a word and the punctuation following it
  # eg: "he is a boy." => "he is a boy ."
  # Reference:- https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
  #w = re.sub(r"([?.!,¿])", r" \1 ", w)
  w = re.sub(r'[" "]+', " ", w)

  word_ls = w.split("\t")
  bangla_w = '<start> ' + \
      bangla_word_to_sequence_transformation(word_ls[0]) + ' <end>'
  banglish_w = '<start> ' + \
      english_word_to_sequence_transformation(word_ls[1]) + ' <end>'

  bangla_w = bangla_w.rstrip().strip()
  banglish_w = banglish_w.rstrip().strip()

  # adding a start and an end token to the sentence
  # so that the model know when to start and stop predicting.
  #w = '<start> ' + w + ' <end>'
  arr = []
  arr.append(bangla_w)
  arr.append(banglish_w)
  return arr

# 1. Remove the accents
# 2. Clean the sentences
# 3. Return word pairs in the format: [ENGLISH, SPANISH]


def create_dataset(path, num_examples):
  lines = open(path, encoding='UTF-8').read().strip().split('\n')
  word_pairs = [preprocess_pair_word_sentence(l) for l in lines[:num_examples]]

  # word_pairs = [[preprocess_sentence(w) for w in l.split('\t')]  for l in lines[:num_examples]]
  return word_pairs


# This class creates a word -> index mapping (e.g,. "dad" -> 5) and vice-versa
# (e.g., 5 -> "dad") for each language,


def max_length(tensor):
    return max(len(t) for t in tensor)


def get_bangla_sequence(w):
  '''
  if w == '<start>' or w =='<end>':
    return word2idx[w]
  return bangla_word_to_sequence_transformation(w).split(',')
  '''
  bangla_wlist = w.split(' ')
  #print(" bangla >>>", bangla_wlist[0],"   ",bangla_wlist[1],"   ",bangla_wlist[2])
  arr = []
  #arr.append(word2idx[bangla_wlist[0]])
  arr.append(tar_word2idx['<start>'])
  #seq = bangla_word_to_sequence_transformation(bangla_wlist[1])
  seq = bangla_wlist[1]
  seq_elems = seq.split(",")
  arr2 = []
  for i in range(0, len(seq_elems)):
    if seq_elems[i] == "":
      continue
    arr2.append(int(seq_elems[i]))

  #arr.extend(seq.split(","))
  arr.extend(arr2)
  #arr.append(word2idx[bangla_wlist[2]])
  arr.append(tar_word2idx['<end>'])
  #print(arr)
  return arr


def get_banglish_sequence(w):
  '''
  if w == '<start>' or w =='<end>':
    return word2idx[w]
  return english_word_to_sequence_transformation(w).split(',')
  '''
  banglish_wlist = w.split(' ')
  #print(" banglish >>>", banglish_wlist[0],"   ",banglish_wlist[1],"   ",banglish_wlist[2])
  arr = []
  #arr.append(word2idx[banglish_wlist[0]])
  arr.append(inp_word2idx['<start>'])
  #seq = english_word_to_sequence_transformation(w).split(',')
  #seq = english_word_to_sequence_transformation(banglish_wlist[1])
  seq = banglish_wlist[1]
  seq_elems = seq.split(",")
  arr2 = []
  for i in range(0, len(seq_elems)):
    if seq_elems[i] == "":
      continue
    arr2.append(int(seq_elems[i]))

  #arr.extend(seq.split(","))
  arr.extend(arr2)
  #arr.append(word2idx[banglish_wlist[2]])
  arr.append(inp_word2idx['<end>'])
  return arr


def load_dataset(path, num_examples):
    # creating cleaned input, output pairs
    pairs = create_dataset(path, num_examples)

    # Spanish sentences
    #print("  *******  ",word2idx['1659,1671,1667'])
    #input_tensor = [[word2idx[s] for s in sp.split(' ')] for en, sp in pairs]
    #input_tensor = [[get_banglish_sequence(s) for s in sp.split(' ')] for en, sp in pairs]
    input_tensor = [get_banglish_sequence(sp) for en, sp in pairs]

    # English sentences
    #target_tensor = [[word2idx[s] for s in en.split(' ')] for en, sp in pairs]
    #target_tensor = [get_bangla_sequence(s) for s in en.split(' ') for en, sp in pairs]
    target_tensor = [get_bangla_sequence(en) for en, sp in pairs]

    # Calculate max_length of input and output tensor
    # Here, we'll set those to the longest sentence in the dataset
    max_length_inp, max_length_tar = max_length(
        input_tensor), max_length(target_tensor)

    print("max length input tensor ", max_length_inp)
    print("max length target tensor ", max_length_tar)

    # Padding the input and output tensor to the maximum length
    input_tensor = tf.keras.preprocessing.sequence.pad_sequences(input_tensor,
                                                                 maxlen=max_length_inp,
                                                                 padding='post')

    target_tensor = tf.keras.preprocessing.sequence.pad_sequences(target_tensor,
                                                                  maxlen=max_length_tar,
                                                                  padding='post')

    print("\nAFTER PADDING ")
    print("input tensor ", input_tensor[0])
    print("input tensor length ", len(input_tensor))
    print("target tensor ", target_tensor[0])
    print("target tensor length ", len(target_tensor))

    return input_tensor, target_tensor, max_length_inp, max_length_tar


num_examples = 5402
input_tensor, target_tensor,  max_length_inp, max_length_targ = load_dataset(
    path_to_file, num_examples)
print("max length input tensor =================", max_length_inp,
      "\nmax length target tensor =================", max_length_targ)


# Creating training and validation sets using an 80-20 split
input_tensor_train, input_tensor_val, target_tensor_train, target_tensor_val = train_test_split(
    input_tensor, target_tensor, test_size=0.2)

# Show length
len(input_tensor_train), len(target_tensor_train), len(
    input_tensor_val), len(target_tensor_val)

BUFFER_SIZE = len(input_tensor_train)
BATCH_SIZE = 64
N_BATCH = BUFFER_SIZE//BATCH_SIZE
print("BUFFER SIZE >>>> ", BUFFER_SIZE, "N_Batch >>> ", N_BATCH)
embedding_dim = 256
units = 1024
vocab_inp_size = len(inp_word2idx) + 1
vocab_tar_size = len(tar_word2idx) + 1

dataset = tf.data.Dataset.from_tensor_slices(
    (input_tensor_train, target_tensor_train)).shuffle(BUFFER_SIZE)
dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)


def gru(units):
  # If you have a GPU, we recommend using CuDNNGRU(provides a 3x speedup than GRU)
  # the code automatically does that.
  if tf.test.is_gpu_available():
    return tf.keras.layers.CuDNNGRU(units,
                                    return_sequences=True,
                                    return_state=True,
                                    recurrent_initializer='glorot_uniform')
  else:
    return tf.keras.layers.GRU(units,
                               return_sequences=True,
                               return_state=True,
                               recurrent_activation='sigmoid',
                               recurrent_initializer='glorot_uniform')


class Encoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, enc_units, batch_sz):
        super(Encoder, self).__init__()
        self.batch_sz = batch_sz
        self.enc_units = enc_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = gru(self.enc_units)

    def call(self, x, hidden):
        x = self.embedding(x)
        output, state = self.gru(x, initial_state=hidden)
        return output, state

    def initialize_hidden_state(self):
        return tf.zeros((self.batch_sz, self.enc_units))


class Decoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, dec_units, batch_sz):
        super(Decoder, self).__init__()
        self.batch_sz = batch_sz
        self.dec_units = dec_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = gru(self.dec_units)
        self.fc = tf.keras.layers.Dense(vocab_size)

        # used for attention
        self.W1 = tf.keras.layers.Dense(self.dec_units)
        self.W2 = tf.keras.layers.Dense(self.dec_units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, x, hidden, enc_output):
        # enc_output shape == (batch_size, max_length, hidden_size)

        # hidden shape == (batch_size, hidden size)
        # hidden_with_time_axis shape == (batch_size, 1, hidden size)
        # we are doing this to perform addition to calculate the score
        hidden_with_time_axis = tf.expand_dims(hidden, 1)

        # score shape == (batch_size, max_length, 1)
        # we get 1 at the last axis because we are applying tanh(FC(EO) + FC(H)) to self.V
        score = self.V(tf.nn.tanh(self.W1(enc_output) +
                                  self.W2(hidden_with_time_axis)))

        # attention_weights shape == (batch_size, max_length, 1)
        attention_weights = tf.nn.softmax(score, axis=1)

        # context_vector shape after sum == (batch_size, hidden_size)
        context_vector = attention_weights * enc_output
        context_vector = tf.reduce_sum(context_vector, axis=1)

        # x shape after passing through embedding == (batch_size, 1, embedding_dim)
        x = self.embedding(x)

        # x shape after concatenation == (batch_size, 1, embedding_dim + hidden_size)
        x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)

        # passing the concatenated vector to the GRU
        output, state = self.gru(x)

        # output shape == (batch_size * 1, hidden_size)
        output = tf.reshape(output, (-1, output.shape[2]))

        # output shape == (batch_size * 1, vocab)
        x = self.fc(output)

        return x, state, attention_weights

    def initialize_hidden_state(self):
        return tf.zeros((self.batch_sz, self.dec_units))


encoder = Encoder(vocab_inp_size, embedding_dim, units, BATCH_SIZE)
decoder = Decoder(vocab_tar_size, embedding_dim, units, BATCH_SIZE)


optimizer = tf.train.AdamOptimizer()


def loss_function(real, pred):
  mask = 1 - np.equal(real, 0)
  loss_ = tf.nn.sparse_softmax_cross_entropy_with_logits(
      labels=real, logits=pred) * mask
  return tf.reduce_mean(loss_)


#checkpoint_dir = './training_checkpoints'
checkpoint_dir = env["MODEL_PATH"]

checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
checkpoint = tf.train.Checkpoint(optimizer=optimizer,
                                 encoder=encoder,
                                 decoder=decoder)


def evaluate(sentence, encoder, decoder, max_length_inp, max_length_targ):
    attention_plot = np.zeros((max_length_targ, max_length_inp))
    sentence = preprocess_sentence(sentence)
    #print("\nIn evaluation preprocessed sentence ",sentence)
    inputs = get_banglish_sequence(sentence)
    #print("\nIn evaluation input ",inputs)
    inputs = tf.keras.preprocessing.sequence.pad_sequences(
        [inputs], maxlen=max_length_inp, padding='post')
    #print("\nIn evaluation input after padding ",inputs[0])
    inputs = tf.convert_to_tensor(inputs)
    #print("\nIn evaluation converted input tensor",inputs[0])

    result = ""

    hidden = [tf.zeros((1, units))]
    enc_out, enc_hidden = encoder(inputs, hidden)

    dec_hidden = enc_hidden
    dec_input = tf.expand_dims([tar_word2idx['<start>']], 0)
    #dec_input = tf.expand_dims([targ_lang.word2idx[word_to_sequence_transformation('<start>')]], 0)

    for t in range(max_length_targ):
        predictions, dec_hidden, attention_weights = decoder(
            dec_input, dec_hidden, enc_out)

        # storing the attention weigths to plot later on
        attention_weights = tf.reshape(attention_weights, (-1, ))
        attention_plot[t] = attention_weights.numpy()

        predicted_id = tf.argmax(predictions[0]).numpy()
        print(" prediction sequence >>>>>>>>> ",
              predicted_id, type(predicted_id))

        result += tar_idx2word[predicted_id]

        #print(" prediction res >>>>>>>>> ",result)

        if tar_idx2word[predicted_id] == '<end>':
            return result, sentence, attention_plot

        # the predicted ID is fed back into the model
        dec_input = tf.expand_dims([predicted_id], 0)

    return result, sentence, attention_plot


# function for plotting the attention weights
def plot_attention(attention, sentence, predicted_sentence):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.matshow(attention, cmap='viridis')

    fontdict = {'fontsize': 14}

    ax.set_xticklabels([''] + sentence, fontdict=fontdict, rotation=90)
    ax.set_yticklabels([''] + predicted_sentence, fontdict=fontdict)

 #   plt.show()


def translate(sentence, encoder, decoder,  max_length_inp, max_length_targ):
    result, sentence, attention_plot = evaluate(
        sentence, encoder, decoder,  max_length_inp, max_length_targ)

    print('Input: {}'.format(sentence))
    print('Predicted translation: {}'.format(result))

#    attention_plot = attention_plot[:len(result.split(' ')), :len(sentence.split(' '))]
 #   plot_attention(attention_plot, sentence.split(' '), result.split(' '))


# restoring the latest checkpoint in checkpoint_dir
checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))


translate(u'tui', encoder, decoder,  max_length_inp, max_length_targ)


translate(u'tora', encoder, decoder,  max_length_inp, max_length_targ)


translate(u'era', encoder, decoder,  max_length_inp, max_length_targ)


# wrong translation
#translate(u'ekhon', encoder, decoder,  max_length_inp, max_length_targ)

#print(tar_idx2word[1423])
while True:
	st = input("Enter banglish : ")
	if st == 'exit':
		break
	translate(st, encoder, decoder,  max_length_inp, max_length_targ)

# Export prediction API's for deamon


def initPredictionModel():
        #TODO initialize TF model for prediction

        # returning 0 means initialization of TF model is successfull
        return 0


def predict(banglisgWord):
	return "<TODO>"
