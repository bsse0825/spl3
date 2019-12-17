#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:58:16 2019

@author: hasan
"""

import os
import string
import re
import numpy as np

def load_doc(filename):
  # open the file as read only
  file = open(filename, mode= "r" , encoding="utf-8-sig" )
  # read all text
  text = file.read()
  # close the file
  file.close()
  return text

def getBanglaWordList(docname):
    text = load_doc(docname)
    
    word_list = text.splitlines()
    lengthOfWord_list = len(word_list)
    #print(lengthOfWord_list," , ",word_list[0],"\n======")
     
    return word_list





dataset_names = os.listdir("../Data")

bangla_word_list = []

for name in dataset_names:
    
    if (name.find(".txt") != -1):
        bwlist = getBanglaWordList("../Data/" + name)
        bangla_word_list.extend(bwlist)

print("Total bangla words >>>>",len(bangla_word_list))

unique_bangla_words = set()

for word in bangla_word_list:
    unique_bangla_words.add(word)
    
print("Total Unique bangla words >>>>",len(unique_bangla_words))


def save_unique_bangla_word_to_file(unique_bangla_words):
    
    output_file = open('../Data/data3.txt', 'w', encoding="utf-8-sig")
    
    for word in unique_bangla_words:
        output_file.write(word+"\n" )
    output_file.close()
    
save_unique_bangla_word_to_file(unique_bangla_words)


'''
import csv

with open('data2.csv', mode='w') as data_file:
    csv_writer = csv.writer(data_file, delimiter=',')

    for word in unique_bangla_words:
        csv_writer.writerow([word])
        
'''