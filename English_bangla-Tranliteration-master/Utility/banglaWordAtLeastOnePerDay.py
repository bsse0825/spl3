#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 15:32:04 2019

@author: hasan
"""


import urllib.request as ur
f = ur.urlopen("https://www.banglatangla.com/freq365n.html")
data = f.read().decode('utf-8')
#print(data)
arr =[]
li = list(data.split(" ")) 
#print(li[84999])

'''
for j in range(0, len(li)):
    print(li[j]," : ",j,"\n>>>>>>>")
'''

length= len(li)
i=0


while ( i < length):
    x = re.findall('^class="variants">', li[i])
    if(x):
        i = i+1
        while(i!= length):
            arr.append(li[i])
            x = re.findall("</div>{1}", li[i])
            if(x):
                #print(li[i],"\n>>>>>>>>>>>")
                break         
            #print(li[i],"\n==========")
            i=i+1
    i= i+1



bw_list=[]


for j in range(0, len(arr)):
    word = arr[j]
    x = re.sub("[a-zA-Z0-9\s\n()<>/]", "", word)
    if( x == ''):
        continue
    bw_list.append(x)


'''
for k in range(0, len(bw_list)):
    print(bw_list[k])
'''  
 
print("total string ",length)
print("noisy bangla length ",len(arr))
print("cleared bangla length ",len(bw_list))

output_file = open('../Data/banglaWordAtLeastOnePerDay.txt', 'w', encoding="utf-8-sig")
    
for word in bw_list:
    output_file.write(word+"\n" )

output_file.close()