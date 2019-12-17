# Return model
from __future__ import absolute_import, division, print_function
import environment1

import re
import numpy as np
import os
import time
import string
import tensorflow as tf

tf.enable_eager_execution()


################ ENCODER
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


################## DECODER

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
        #context_vector =   enc_output
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


def preprocess_sentence(w):
  # w = unicode_to_ascii(w.lower().strip())
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


def create_dataset(path, num_examples):
  lines = open(path, encoding='UTF-8').read().strip().split('\n')
  word_pairs = [preprocess_pair_word_sentence(l) for l in lines[:num_examples]]

  # word_pairs = [[preprocess_sentence(w) for w in l.split('\t')]  for l in lines[:num_examples]]
  return word_pairs


########################### Utilities
def max_length(tensor):
    return max(len(t) for t in tensor)


def get_bangla_sequence(w):
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

    # Padding the input and output tensor to the maximum length
    input_tensor = tf.keras.preprocessing.sequence.pad_sequences(input_tensor,
                                                                 maxlen=max_length_inp,
                                                                 padding='post')

    target_tensor = tf.keras.preprocessing.sequence.pad_sequences(target_tensor,
                                                                  maxlen=max_length_tar,
                                                                  padding='post')

    return input_tensor, target_tensor, max_length_inp, max_length_tar


'''

def preprocess_sentence(w):
    # w = unicode_to_ascii(w.lower().strip())
    # creating a space between a word and the punctuation following it
    # eg: "he is a boy." => "he is a boy ."
    # Reference:- https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
    w = re.sub(r"([?.!,¿])", r" \1 ", w)
    w = re.sub(r'[" "]+', " ", w)

    # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
    #    w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)
    w = w.rstrip().strip()

    # adding a start and an end token to the sentence
    # so that the model know when to start and stop predicting.
    w = '<start> ' + w + ' <end>'
    return w


# 1. Remove the accents
# 2. Clean the sentences
# 3. Return word pairs in the format: [BANGLA, BANGLISH]
def create_dataset(path, num_examples):
    lines = open(path, encoding='UTF-8').read().strip().split('\n')
    word_pairs = [[preprocess_sentence(w) for w in l.split('\t')]  for l in lines[:num_examples]]
    return word_pairs



# This class creates a word -> index mapping (e.g,. "dad" -> 5) and vice-versa
# (e.g., 5 -> "dad") for each language,
class LanguageIndex():
    def __init__(self, lang):
        self.lang = lang
        self.word2idx = {}
        self.idx2word = {}
        self.vocab = set()

        self.create_index()

    def create_index(self):
        for phrase in self.lang:
            self.vocab.update(phrase.split(' '))
        self.vocab = sorted(self.vocab)
        self.word2idx['<pad>'] = 0
        for index, word in enumerate(self.vocab):
            self.word2idx[word] = index + 1
        for word, index in self.word2idx.items():
            self.idx2word[index] = word

def load_dataset(path, num_examples):
    # creating cleaned input, output pairs
    pairs = create_dataset(path, num_examples)
 # index language using the class defined above
    inp_lang = LanguageIndex(sp for en, sp in pairs)
    targ_lang = LanguageIndex(en for en, sp in pairs)

    # Vectorize the input and target languages

    # BANGLISH sentences
    input_tensor = [[inp_lang.word2idx[s] for s in sp.split(' ')] for en, sp in pairs]

    # BANGLA sentences
    target_tensor = [[targ_lang.word2idx[s] for s in en.split(' ')] for en, sp in pairs]

    # Calculate max_length of input and output tensor
    # Here, we'll set those to the longest sentence in the dataset
    max_length_inp, max_length_tar = max_length(input_tensor), max_length(target_tensor)

    # Padding the input and output tensor to the maximum length
    input_tensor = tf.keras.preprocessing.sequence.pad_sequences(input_tensor,
                                                             maxlen=max_length_inp,
                                                             padding='post')

    target_tensor = tf.keras.preprocessing.sequence.pad_sequences(target_tensor,
                                                              maxlen=max_length_tar,
                                                              padding='post')

    return input_tensor, target_tensor, inp_lang, targ_lang, max_length_inp, max_length_tar




######################### #Utilitiei th the size of that dataset
'''
