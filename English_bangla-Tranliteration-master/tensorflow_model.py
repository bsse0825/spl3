#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 11:57:11 2019

@author: srbd
"""


import os
import string
import re
import numpy as np


import tensorflow as tf
from tensorflow.contrib import rnn

def load_doc(filename):
  # open the file as read only
  file = open(filename, mode= "r" , encoding="utf-8-sig" )
  # read all text
  text = file.read()
  # close the file
  file.close()
  return text

def isEnglishSentence(sentence):
    
    if len(sentence) == 0:
        return False
    
    numberOfEnglishChars = 0

    for c in sentence:
        isEnglishLetter = re.match(r'[a-zA-Z0-9]', c)
        if (isEnglishLetter is None) == False:
            numberOfEnglishChars += 1
    
    if numberOfEnglishChars == 0:
        return False
    
    #print((numberOfEnglishChars/len(sentence)*100))
    if ((numberOfEnglishChars/len(sentence)*100) > 50):
        return True
    
    return False


#I don't know how to detect this.
def isBanglaSentence(sentence):
    
    
    if isEnglishSentence(sentence) == False:
        numberOfChar = 0
        
        for c in sentence:
            if c.isalpha():
                numberOfChar += 1
        
        if numberOfChar == 0:
            return False
        
        if (len(sentence)/numberOfChar)*100 > 10:
            return True
    else:
        return False
    
    
def getEnglishAndBanglaSentences(splittedLines):
    #prepare english and bangla sentences
    english_sentence_list = []
    bangla_sentence_list = []
    
    eng_sentence = ""
    bng_sentence = ""
    
    for line in splittedLines:
        if isEnglishSentence(line):
            eng_sentence = line
        elif isBanglaSentence(line):
            bng_sentence = line
            
        if len(eng_sentence) > 0 and len(bng_sentence) > 0:
            english_sentence_list.append(eng_sentence)
            bangla_sentence_list.append(bng_sentence)
            eng_sentence = ""
            bng_sentence = ""
    
    return english_sentence_list, bangla_sentence_list



# Get english and bangla sentences first
text = load_doc("./Dataset/chat-1.txt")
splittedLines = text.splitlines()

eng_s, ban_s = getEnglishAndBanglaSentences(splittedLines=splittedLines)


#Get English and Bangla word list from a docname
def getEnglishAndBanglaWordList(docname):
    text = load_doc(docname)
    
    splittedLines = text.splitlines()
    lengthOfSplittedLines = len(splittedLines)
    eng_sentence, bng_sentence = getEnglishAndBanglaSentences(splittedLines=splittedLines)
    
#    print(eng_sentence, bng_sentence)
    if (len(eng_sentence) == len(bng_sentence)) == False:
        print("This is a case that should not occur")
    
    engWords = []
    bngWords = []
    
#     print(eng_sentence)
    
    for i in range(0, len(eng_sentence)):
#         print(i, eng_sentence[i], bng_sentence[i])
        ew = eng_sentence[i].split(";")
        bw = bng_sentence[i].split(";")
        
        if (len(ew) != len(bw)):
            print("English - %s, bangla - %s, Count %d %d" % (ew, bw, len(ew), len(bw)))
        engWords.extend(ew)
        bngWords.extend(bw)
        
    return engWords, bngWords


ewlist, bwlist = getEnglishAndBanglaWordList("./Dataset/" + "chat-15.txt")


dataset_names = os.listdir("./Dataset")

english_word_list = []
bangla_word_list = []

for name in dataset_names:
    
    if (name.find(".txt") != -1):
        ewlist, bwlist = getEnglishAndBanglaWordList("./Dataset/" + name)
        english_word_list.extend(ewlist)
        bangla_word_list.extend(bwlist)
        
print(len(english_word_list))
print(len(bangla_word_list))


#Verify if the indexing is alright
print(english_word_list[40], bangla_word_list[40])
print(english_word_list[505], bangla_word_list[505])
print(english_word_list[5225], bangla_word_list[5225])
print(english_word_list[15000], bangla_word_list[15000])
print(english_word_list[22077], bangla_word_list[22077])


#CLEAN THE DATA
def cleanWord(word, isBangla):
    cleaned = ""
    for c in word:
        if c == '\ufeff' or c == '\u200c':
            continue
        if isBangla and not(re.match(r'[a-zA-Z৷।]', c) == None):
            continue
        if(re.match(r'[’‘“\'\":\-!@#$%^&?*\_/+,."("")"\\–” ]', c) == None):
            cleaned += c
            
    return cleaned
    
def shouldIncludeWord(word):
    if len(word) > 0:
        return True
    return False


def clean_word_list(current_ew_word_list, current_bw_word_list):
    cleaned_english_word_list = []
    cleaned_bangla_word_list = []
    encountered_words = {}

    for ew, bw in zip(current_ew_word_list, current_bw_word_list):
        if encountered_words.get(ew) == None:
            encountered_words[ew] = True
        else:
            continue

        if shouldIncludeWord(ew):
            cleaned_ew = cleanWord(ew, False).lower()
            cleaned_bw = cleanWord(bw, True)

            cleaned_english_word_list.append(cleaned_ew)
            cleaned_bangla_word_list.append(cleaned_bw)
    
    return cleaned_english_word_list, cleaned_bangla_word_list


cleaned_english_words, cleaned_bangla_words = clean_word_list(english_word_list, bangla_word_list)


all_characters_set = set([])

for ew, bw in zip(cleaned_english_words, cleaned_bangla_words):
    
    ec_array = list(ew)
    _ = [all_characters_set.add(c) for c in ec_array]
    
    bc_array = list(bw)
    _ = [all_characters_set.add(c) for c in bc_array]
    
all_characters_set.add('')



#Character encoding

chars_i_to_c = dict((i, c) for i, c in enumerate(all_characters_set))
chars_c_to_i = dict((c, i) for i, c in enumerate(all_characters_set))


def getMaxWordLength(wordArray):
    maxLen = 0
    for w in wordArray:
        if len(w) > maxLen:
            maxLen = len(w)

    return maxLen


maxBanglaWordLength = getMaxWordLength(cleaned_bangla_words)
maxEnglishWordLength = getMaxWordLength(cleaned_english_words)


def getVectorizedWord(word, encoder, maxLength):
    vectorized_word = []
    
    for c in word:
        cv = encoder[c]
        vectorized_word.append(cv)
        
    #Add Padding
    vectorized_word.extend([encoder['']] * (maxLength - len(word)))
    
    return vectorized_word


def reverseVectorization(vectorized_word, decoder):
    mainWord = ""
    
    for i in vectorized_word:
        mainWord += decoder[i]
        
    return mainWord


from keras.utils.np_utils import to_categorical

def convert_vector_to_one_hot_encoded_array(vector, total_classes):
    #one_hot_encoded_vector = to_categorical(vector, num_classes=total_classes)
    one_hot_encoded_vector = np.eye(total_classes)[vector]
    return one_hot_encoded_vector
    
def convert_one_hot_encoded_to_vector(one_hot_encoded):
    vectorized = []
    
    for one_hot_array in one_hot_encoded:
        vectorized.append(np.argmax(one_hot_array))
    
    return vectorized


def wordToOneHotEncode(word, encoder, vector_max_length, total_one_hot_classes):
    vectorRepresentation = getVectorizedWord(word, encoder, vector_max_length)
    one_hot_encoded = convert_vector_to_one_hot_encoded_array(vectorRepresentation, total_one_hot_classes)
    return one_hot_encoded

def oneHotEncodeToWord(one_hot, decoder):
    vectorRepresentation = convert_one_hot_encoded_to_vector(one_hot)
    word = reverseVectorization(vectorRepresentation, decoder)
    return word


banglish_word_train_set = []
bangla_word_result_set = []
banglish_word_max_length = 22
bangla_word_max_length = 21
total_one_hot_classes = 98

for ew in cleaned_english_words:
    banglish_word_train_set.append(wordToOneHotEncode(ew, chars_c_to_i, banglish_word_max_length, total_one_hot_classes))

for bw in cleaned_bangla_words:
    bangla_word_result_set.append(wordToOneHotEncode(bw, chars_c_to_i, bangla_word_max_length, total_one_hot_classes))
    
banglish_word_train_set = np.asarray(banglish_word_train_set)
bangla_word_result_set = np.asarray(bangla_word_result_set)

#TRAIN TEST SPLIT
from sklearn.model_selection import train_test_split

train_x, test_x, train_y, test_y = train_test_split(banglish_word_train_set, bangla_word_result_set, test_size=0.20, random_state=42)


print(oneHotEncodeToWord(train_x[0], chars_i_to_c), oneHotEncodeToWord(train_y[0], chars_i_to_c))
print(oneHotEncodeToWord(train_x[95], chars_i_to_c), oneHotEncodeToWord(train_y[95], chars_i_to_c))
print(oneHotEncodeToWord(train_x[1500], chars_i_to_c), oneHotEncodeToWord(train_y[1500], chars_i_to_c))
print(oneHotEncodeToWord(train_x[3871], chars_i_to_c), oneHotEncodeToWord(train_y[3871], chars_i_to_c))


#########################################################
#############################################
#############################################
    

def randomize(x, y):
    """ Randomizes the order of data samples and their corresponding labels"""
    permutation = np.random.permutation(y.shape[0])
    shuffled_x = x[permutation, :]
    shuffled_y = y[permutation]
    return shuffled_x, shuffled_y

def get_next_batch(x, y, start, end):
    x_batch = x[start:end]
    y_batch = y[start:end]
    return x_batch, y_batch
# weight and bais wrappers
def weight_variable(shape):
    """
    Create a weight variable with appropriate initialization
    :param name: weight name
    :param shape: weight shape
    :return: initialized weight variable
    """
    initer = tf.truncated_normal_initializer(stddev=0.01)
    return tf.get_variable('W',
                           dtype=tf.float32,
                           shape=shape,
                           initializer=initer)

def bias_variable(shape):
    """
    Create a bias variable with appropriate initialization
    :param name: bias variable name
    :param shape: bias variable shape
    :return: initialized bias variable
    """
    initial = tf.constant(0., shape=shape, dtype=tf.float32)
    return tf.get_variable('b',
                           dtype=tf.float32,
                           initializer=initial)
 
def BiRNN(x, weights, biases, timesteps, num_hidden):
    # Prepare data shape to match `rnn` function requirements
    # Current data input shape: (batch_size, timesteps, n_input)
    # Required shape: 'timesteps' tensors list of shape (batch_size, num_input)

    # Unstack to get a list of 'timesteps' tensors of shape (batch_size, num_input)
    x = tf.unstack(x, timesteps, 1)

    # Define lstm cells with tensorflow
    # Forward direction cell
    lstm_fw_cell = rnn.BasicLSTMCell(num_hidden, forget_bias=1.0)
    # Backward direction cell
    lstm_bw_cell = rnn.BasicLSTMCell(num_hidden, forget_bias=1.0)

    # Get BiRNN cell output
    outputs, _, _ = rnn.static_bidirectional_rnn(lstm_fw_cell, lstm_bw_cell, x,
                                                 dtype=tf.float32)

    # Linear activation, using rnn inner loop last output
    return tf.matmul(outputs[-1], weights) + biases
 




def tfmodel():
    
    learning_rate = 0.001 # The optimization initial learning rate
    epochs = 10           # Total number of training epochs
    batch_size = 64     # Training batch size
    display_freq = 100 
    num_hidden_units = 256  # Number of hidden units of the RNN
    timesteps = 21
    x = tf.placeholder(tf.float32, shape=[None, timesteps, 98], name='X')
    y = tf.placeholder(tf.float32, shape=[None,98], name='Y')

# create weight matrix initialized randomely from N~(0, 0.01)
    W  = tf.Variable(tf.truncated_normal([num_hidden_units*2, int(y.get_shape()[1])]))

# create bias vector initialized as zero
    b = bias_variable(shape=[98])

    output_logits = BiRNN(x, W, b, timesteps, num_hidden_units)
   # y_pred = tf.nn.softmax(output_logits)
# Model predictions
   # cls_prediction = tf.argmax(output_logits, axis=1, name='predictions')

# Define the loss function, optimizer, and accuracy
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=output_logits), name='loss')
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate, name='Adam-op').minimize(loss)
    correct_prediction = tf.equal(tf.argmax(output_logits, 1), tf.argmax(y, 1), name='correct_pred')
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name='accuracy')
# Creating the op for initializing all variables
    init = tf.global_variables_initializer()

    sess = tf.InteractiveSession()
    sess.run(init)
    global_step = 0

    num_tr_iter = int(len(train_y) / batch_size)
    for epoch in range(epochs):
        print('Training epoch: {}'.format(epoch + 1))
        x_train, y_train = randomize(train_x, train_y)
        for iteration in range(num_tr_iter):
            global_step += 1
            start = iteration * batch_size
            end = (iteration + 1) * batch_size
            x_batch, y_batch = get_next_batch(x_train, y_train, start, end)
            x_batch = x_batch.reshape((batch_size,21, 98))
        # Run optimization op (backprop)
            feed_dict_batch = {x: x_batch, y: y_batch}
            sess.run(optimizer, feed_dict=feed_dict_batch)

            if iteration % display_freq == 0:
            # Calculate and display the batch loss and accuracy
                loss_batch, acc_batch = sess.run([loss, accuracy],
                                             feed_dict=feed_dict_batch)

                print("iter {0:3d}:\t Loss={1:.2f},\tTraining Accuracy={2:.01%}".
                      format(iteration, loss_batch, acc_batch))

    # Run validation after every epoch

        feed_dict_valid = {x: test_x.reshape((-1, timesteps, 98)), y: test_y}
        loss_valid, acc_valid = sess.run([loss, accuracy], feed_dict=feed_dict_valid)
        print('---------------------------------------------------------')
        print("Epoch: {0}, validation loss: {1:.2f}, validation accuracy: {2:.01%}".
              format(epoch + 1, loss_valid, acc_valid))
        print('---------------------------------------------------------')







def getWordForVector(one_hot):
    for r in one_hot:
        vs = np.argmax(r, axis=1)
        rv = reverseVectorization(vs, chars_i_to_c)
    return rv


def getResultForOneWord(model, one_hot):
    results = model.predict(one_hot, batch_size=32)
    for r in results:
        vs = np.argmax(r, axis=1)
        rv = reverseVectorization(vs, chars_i_to_c)
    return rv


import statistics as s
import tensorflow as tf

class LossHistory(tf.keras.callbacks.Callback):
    
    def __init__(self, train_x, train_y, test_x, test_y):
        self.epoch_count = 0
        self.train_acc = []
        self.train_loss = []
        self.validation_acc = []
        self.validation_loss = []
        #self.filename = filename
        self.train_x = train_x
        self.train_y = train_y
        self.test_x = test_x
        self.test_y = test_y
        #self.f = open(filename,"w+")
    
    def computeResultForTwoWords(self, wTrue, wPred):
        totalMatch = 0
        for i in range(0,len(wTrue)):
            if i < len(wPred):
                if wTrue[i] == wPred[i]:
                    totalMatch += 1
        
        if len(wTrue) == 0:
            return 0
        
        return totalMatch/len(wTrue)
    
    def summaryOfValidationData(self):
        x_val, y_val = self.validation_data[0], self.validation_data[1]
        self.evaluateModel(self.model, x_val, y_val, shouldPrint=True)
        
    def evaluateModel(self, model, x_val, y_val, shouldPrint=False):
        allResults = []
        for i in range(0, x_val.shape[0]):
            wPred = getResultForOneWord(model, x_val[i:i+1])
            wTrue = getWordForVector(y_val[i:i+1])
            
            if shouldPrint:
                print(getWordForVector(x_val[i:i+1]), wPred, wTrue)
            
            result = self.computeResultForTwoWords(wTrue, wPred)
            
            allResults.append(result)
            
        return s.mean(allResults)

    def on_epoch_end(self, batch, logs={}):
        
        train_result = self.evaluateModel(self.model, self.train_x, self.train_y)
        test_result = self.evaluateModel(self.model, self.test_x, self.test_y)
        
        #train_acc = logs.get('acc')
        train_loss = logs.get('loss')
        #val_acc = logs.get('val_acc')
        val_loss = logs.get('val_loss')
        
        #self.train_acc.append(train_acc)
        self.train_loss.append(train_loss)
        #self.validation_acc.append(val_acc)
        self.validation_loss.append(val_loss)
        
        self.epoch_count += 1
        #self.f.write("%.2f %.2f %.2f %.2f\n " % (train_acc, train_loss, val_acc, val_loss))
        print("Epoch %d [Train Result] - Acc %.3f, Loss %.3f, [Validation Result] - Acc %.3f, Loss %.3f" % (self.epoch_count, train_result, train_loss, test_result, val_loss))


#Bidirectional LSTM(CPU)
from tensorflow.keras.models import *
from tensorflow.keras.layers import *
from tensorflow.keras import regularizers


def createTestBidirectionalModelCPU(summary):
    model = Sequential()
    model.add(Bidirectional(LSTM(256), input_shape=(banglish_word_max_length, total_one_hot_classes)))
    model.add(RepeatVector(bangla_word_max_length))
    model.add(Dropout(0.5))
    model.add(Bidirectional(LSTM(256, return_sequences=True)))
    model.add(Dropout(0.5))
#     model.add(TimeDistributed(Reshape((-1, 256))))
#     model.add(TimeDistributed(Reshape((-1, 512))))
    model.add(TimeDistributed(Dense((512))))
    model.add(TimeDistributed(Dense((256))))
    model.add(TimeDistributed(Dense((128))))
    model.add(TimeDistributed(Dense(total_one_hot_classes, activation= 'softmax')))
    model.compile(loss= 'kullback_leibler_divergence' , optimizer= 'adam')

    if(summary):
        print(model.summary())
    
    return model



'''
cpuModel = createTestBidirectionalModelCPU(summary = True)
        
history = LossHistory(train_x, train_y, test_x, test_y)

#Should get about 74% validation accuracy. Can take about 4-5 hours depending on CPU
cpuModel.fit(train_x, train_y, validation_data=(test_x, test_y), epochs=100, batch_size=64, callbacks=[history], verbose = 0)




#from tensorflow.keras.models import load_model


# import tensorflow as tf

# keras_file = "bdmodel1.h5"

# tf.keras.models.save_model(cpuModel, keras_file)


#IGNORE THIS PART. Mobile conversion does not work.
# converter = tf.contrib.lite.TFLiteConverter.from_keras_model_file(keras_file)
# tflite_model = converter.convert()
# open("bdmodel.tflite", "wb").write(tflite_model)

getWordForVector(train_y[9:10])


getResultForOneWord(cpuModel, train_x[9:10])



# Note that chars_c_to_i, banglish_word_max_length, total_one_hot_classes are defined above. 
# so, no need to anything for that
# But make sure that previous statements were executed
def getPrediction(model, word):
    oneHotEncodedWord = wordToOneHotEncode(word, chars_c_to_i, banglish_word_max_length, total_one_hot_classes)
    oneHotEncodedWord = oneHotEncodedWord.reshape((1,oneHotEncodedWord.shape[0],oneHotEncodedWord.shape[1]))
    return getResultForOneWord(model, oneHotEncodedWord)



#Usage
#getPrediction(cpuModel, "aacchaa")
    
getPrediction(cpuModel, "tumi")

'''
tfmodel()
