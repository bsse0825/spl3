import NK_Model1
import environment1
import sys
import string
import time
import numpy as np
import os
from sklearn.model_selection import train_test_split
import tensorflow as tf
tf.enable_eager_execution()

env = environment1.envionmrnt_mode('RELEASE')
checkpoint_dir = env["MODEL_PATH"]
training_dataset_path = env['training_dataset_path']
#TODO: need to get sample count dynamicaly


def load_doc(filename):
  # open the file as read only
  file = open(filename, mode= "r" , encoding="utf-8" )
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
  line= splittedLines[i]
  word = line.split("\t")
  if tar_word2idx.get(word[0]) == None:
      tar_word2idx[word[0]] = int(word[1])
  count = count +1

tar_word2idx['<start>'] = count +1
tar_word2idx['<end>'] = count +2

for word, index in tar_word2idx.items():
  tar_idx2word[index] = word


text2 = load_doc("englishLetter.txt")
english_splittedLines = text2.splitlines()

count =0
inp_word2idx ={}
inp_idx2word ={}
#inp_word2idx['<pad>'] = 0
for i in range(0, len(english_splittedLines)):     
  line= english_splittedLines[i]
  word = line.split("\t")
  
  if inp_word2idx.get(word[0]) == None:
      inp_word2idx[word[0]] = word[1]
  count = count +1

inp_word2idx['<start>'] = count + 1
inp_word2idx['<end>'] = count +2

for word, index in inp_word2idx.items():
  inp_idx2word[index] = word


embedding_dim = 256
units = 1024
def initModel():

    num_examples = 5401

    # input_tensor = banglish word
    # target_tensor = bangla word (leveling)
    # max_length_inp = banglish word max length
    # max_length_targ = bangla word max length
    input_tensor, target_tensor, max_length_inp, max_length_targ = NK_Model1.load_dataset(training_dataset_path, num_examples)


    # spliting data set into training(90%) and testing(10%)
    input_tensor_train, input_tensor_val, target_tensor_train, target_tensor_val = train_test_split(input_tensor, target_tensor, test_size=0.01)


# TODO: add coment

    BUFFER_SIZE = len(input_tensor_train)


    BATCH_SIZE = env["BATCH"]
    N_BATCH = BUFFER_SIZE//BATCH_SIZE
# TODO: add coment
    vocab_inp_size = len(inp_word2idx) +1
    vocab_tar_size = len(tar_word2idx) +1


    dataset = tf.data.Dataset.from_tensor_slices((input_tensor_train, target_tensor_train)).shuffle(BUFFER_SIZE)
    dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)
    encoder = NK_Model1.Encoder(vocab_inp_size, embedding_dim, units, BATCH_SIZE)
    decoder = NK_Model1.Decoder(vocab_tar_size, embedding_dim, units, BATCH_SIZE)
    optimizer = tf.train.AdamOptimizer()




    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
    checkpoint = tf.train.Checkpoint(optimizer=optimizer,
                                 encoder=encoder,
                                 decoder=decoder)
    checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))
    global model_ckpt, encode, decode, input_len, terget_len, max_input_len, max_terget_len
    model_ckpt = checkpoint
    encode = encoder
    decode = decoder
    max_input_len = max_length_inp
    max_terget_len = max_length_targ




def evaluate(sentence, encoder, decoder, max_length_inp, max_length_targ):
    attention_plot = np.zeros((max_length_targ, max_length_inp))
    #sentence = preprocess_sentence(sentence)
    sentence = NK_Model1.preprocess_sentence(sentence)
    #print("\nIn evaluation preprocessed sentence ",sentence)
    inputs = NK_Model1.get_banglish_sequence(sentence)
    #print("\nIn evaluation input ",inputs)
    inputs = tf.keras.preprocessing.sequence.pad_sequences([inputs], maxlen=max_length_inp, padding='post')
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
        predictions, dec_hidden, attention_weights = decoder(dec_input, dec_hidden, enc_out)
        
        # storing the attention weigths to plot later on
        attention_weights = tf.reshape(attention_weights, (-1, ))
        attention_plot[t] = attention_weights.numpy()

        predicted_id = tf.argmax(predictions[0]).numpy()
        #print(" prediction sequence >>>>>>>>> ",predicted_id,type(predicted_id))

        result += tar_idx2word[predicted_id] 
        
        #print(" prediction res >>>>>>>>> ",result)
        
        if tar_idx2word[predicted_id] == '<end>':
            return result, sentence, attention_plot
        
        # the predicted ID is fed back into the model
        dec_input = tf.expand_dims([predicted_id], 0)

    return result, sentence, attention_plot


def translate(sentence, encoder, decoder, max_length_inp, max_length_targ):
    result, sentence, attention_plot = evaluate(sentence, encoder, decoder, max_length_inp, max_length_targ)
    #print('Input: {}'.format(sentence))
    #print('Predicted translation: {}'.format(result))
    return result



def getPrediction(banglish_word):
    print("Request: "+banglish_word)
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
    model_ckpt.restore(tf.train.latest_checkpoint(checkpoint_dir))
    try:
        st = translate(banglish_word, encode, decode, max_input_len, max_terget_len)
    except:
        st = '***'+banglish_word+'***'
    banglisgWord = st.replace('<end>', '')
    return banglisgWord
