import NK_Model
import environment
import sys
import time
import numpy as np
import os
from sklearn.model_selection import train_test_split
import tensorflow as tf
tf.enable_eager_execution()

env = environment.envionmrnt_mode('RELEASE')
checkpoint_dir = env["MODEL_PATH"]
training_dataset_path = env['training_dataset_path']
#TODO: need to get sample count dynamicaly

embedding_dim = 1024
units = 1024
def initModel():

    num_examples = 7280

    # input_tensor = banglish word
    # target_tensor = bangla word (leveling)
    # max_length_inp = banglish word max length
    # max_length_targ = bangla word max length
    input_tensor, target_tensor, inp_lang, targ_lang, max_length_inp, max_length_targ = NK_Model.load_dataset(training_dataset_path, num_examples)


    # spliting data set into training(90%) and testing(10%)
    input_tensor_train, input_tensor_val, target_tensor_train, target_tensor_val = train_test_split(input_tensor, target_tensor, test_size=0.1)


# TODO: add coment

    BUFFER_SIZE = len(input_tensor_train)


    BATCH_SIZE = env["BATCH"]
    N_BATCH = BUFFER_SIZE//BATCH_SIZE
# TODO: add coment
    vocab_inp_size = len(inp_lang.word2idx)
    vocab_tar_size = len(targ_lang.word2idx)


    dataset = tf.data.Dataset.from_tensor_slices((input_tensor_train, target_tensor_train)).shuffle(BUFFER_SIZE)
    dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)
    encoder = NK_Model.Encoder(vocab_inp_size, embedding_dim, units, BATCH_SIZE)
    decoder = NK_Model.Decoder(vocab_tar_size, embedding_dim, units, BATCH_SIZE)
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
    input_len = inp_lang
    terget_len = targ_lang
    max_input_len = max_length_inp
    max_terget_len = max_length_targ

# TODO: add coment
def evaluate(sentence, encoder, decoder, inp_lang, targ_lang, max_length_inp, max_length_targ):

    attention_plot = np.zeros((max_length_targ, max_length_inp))
    sentence = NK_Model.preprocess_sentence(sentence)
    inputs = [inp_lang.word2idx[i] for i in sentence.split(' ')]
    inputs = tf.keras.preprocessing.sequence.pad_sequences( [inputs], maxlen=max_length_inp, padding='post')
    inputs = tf.convert_to_tensor(inputs)
    result = ''
    hidden = [tf.zeros((1, units))]
    enc_out, enc_hidden = encoder(inputs, hidden)
    dec_hidden = enc_hidden
    dec_input = tf.expand_dims([targ_lang.word2idx['<start>']], 0)

    for t in range(max_length_targ):
        predictions, dec_hidden, attention_weights = decoder(dec_input, dec_hidden, enc_out)
        # storing the attention weigths to plot later on
        attention_weights = tf.reshape(attention_weights, (-1, ))
        attention_plot[t] = attention_weights.numpy()
        predicted_id = tf.argmax(predictions[0]).numpy()
        result += targ_lang.idx2word[predicted_id] + ' '
        if targ_lang.idx2word[predicted_id] == '<end>':
            return result, sentence, attention_plot
        # the predicted ID is fed back into the model
        dec_input = tf.expand_dims([predicted_id], 0)

    return result, sentence, attention_plot


def translate(sentence, encoder, decoder, inp_lang, targ_lang, max_length_inp, max_length_targ):
    result, sentence, attention_plot = evaluate(sentence, encoder, decoder, inp_lang, targ_lang, max_length_inp, max_length_targ)
    #print('Input: {}'.format(sentence))
    #print('Predicted translation: {}'.format(result))
    return result



def getPrediction(banglish_word):
    print("Request: "+banglish_word)
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
    model_ckpt.restore(tf.train.latest_checkpoint(checkpoint_dir))
    try:
        st = translate(banglish_word, encode, decode, input_len,
                       terget_len, max_input_len, max_terget_len)
    except:
        st = '***'+banglish_word+'***'
    banglisgWord = st.replace('<end>', '')
    return banglisgWord
