# -*- coding: utf-8 -*-
"""0518_update.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qSWPhKlBgmtqjaVuGOUSsV-T-0xc5av7
"""


import nltk
from nltk.tokenize import word_tokenize

#id를 찾는 함수
def se_find_id(any_list):
    re = 'NAN'
    for i in range(0, len(any_list)):
        if(any_list[i] == 'id'):
            re = any_list[i+1]

    return re

#바뀔 수량을 찾는 함수
def se_find_quantity(any_list):
    re = 'NAN'
    for i in range(0, len(any_list)):
        if(any_list[i] == 'to'):
            re = any_list[i+1]
    
    return re

#error 확인
def error_msg(se_sql):
    re = 'normal'
    if 'NAN' in se_sql:
        re = 'error'
    
    return re

# error나면 "error"라고 리턴합니다!
def update_func(some_list):
    
    cart_id = se_find_id(some_list)
    quantity = se_find_quantity(some_list)
    
    sql = "UPDATE cart SET quantity = " + quantity + " WHERE " + "cart_id = " + cart_id
    
    error_check = error_msg(sql)
    
    if (error_check == 'error'):
        return error_check
    else:
        return sql