import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords 
from nltk.stem import PorterStemmer


#불필요한 단어를 제거해주는 함수
def se_simplify(any_list):

    stop_words = set(stopwords.words('english'))

    result = []
    for token in any_list: 
        if token not in stop_words: 
            result.append(token) 

    return result


#복수를 단수로 바꿔주는 함수
def se_stemming(any_list):
    s=PorterStemmer()
    re = [s.stem(w) for w in any_list]
    return re


# 분류_value 찾기
def se_find_category_value (any_list):
    re_cate = 'NAN'
    re_cate_value = 'NAN'
    main = ['fruit', 'meat']
    middle = ['tomato', 'grape', 'banana', 'beef', 'pork']
    for i in range(0, len(any_list)):
        for j in range(0, len(main)):
            if(any_list[i] == main[j]):
                re_cate_value = main[j]
                re_cate = 'main_cate_name'
        
    for i in range(0, len(any_list)):
        for j in range(0, len(middle)):
            if(any_list[i] == middle[j]):
                re_cate_value = middle[j]
                re_cate = 'middle_cate_name'
      
    return re_cate, re_cate_value



#어느 조건을 검색하는지 탐색 -> column 찾는 것임
def se_find_condition (any_list):
    
    re = 'NAN'

    for i in range(0, len(any_list)):
        if(any_list[i] == 'price' or any_list[i] == 'cheapest' or any_list[i] == 'cost'):  
            re = 'price'   
        elif(any_list[i] == 'rate'):
            re = 'rating'
        elif(any_list[i] == 'review'):
            re = 'number_of_reviews'
        elif(any_list[i] == 'brand'):
            re = 'brand'
        elif(any_list[i] == 'origin' or any_list[i] == 'from'):
            re = 'origin'  

    return re




#price의 value 값을 탐색 
def se_find_price_value (any_list):
    re = 'NAN'
    re_comma = 'NAN'

    for i in range(0, len(any_list)):
        if(any_list[i] == 'less'):
            re_comma = any_list[i+1]
            re = re_comma.replace(',','')

    if(re == 'NAN'):
        re = 'superlative'
      
    return re


#rating의 value 값을 탐색 
def se_find_rating_value (any_list):
    re = 'NA'
    for i in range(0, len(any_list)):
        if(any_list[i] == 'highest'):
            re = 'superlative'
  
    for i in range(0, len(any_list)):
        if(any_list[i].isdigit() == True):
            re = any_list[i]

    return re


#number_of_ratings의 value 값을 탐색 
def se_find_number_of_reviews_value (any_list):
    re = 'NAN'

    for i in range(0, len(any_list)):
        if(any_list[i] == 'highest'):
            re = 'superlative'

    if(re == 'NAN'):
        for i in range(0, len(any_list)):
            if(any_list[i].isdigit() == True):
                re = any_list[i]
                break
                return re
        
    return re


#origin의 value 값을 탐색 
def se_find_origin_value (any_list):
    re = 'NAN'
    country = ['korea', 'austrailia', 'america', 'california', 'vietnam', 'mexico', 'chile', 'us']
    for i in range(0, len(any_list)):
        for j in range(0, len(country)):
            if(any_list[i] == country[j]):
                re = country[j]
                break

    if(re == 'us'):
        re = 'america'
        
    return re


#brand의 value 값을 탐색 
def se_find_brand_value (any_list):
    re = 'NAN'
    brand = ['easy farm', 'olga', 'delmont', 'chiquita', 'dibella', 'pam cook', 'costco', 'glam cook', 'meat cut']
    for i in range(0, len(any_list)):
        for j in range(0, len(brand)):
            if(any_list[i] == brand[j]):
                re = brand[j]
                break

    return re


#조건의 value 값을 탐색 -> column의 value 값을 찾는 것임
def se_find_condition_value (any_list, condition):
    re = 'NAN'
    if(condition == 'price'):
        re = se_find_price_value(any_list)
    elif(condition == 'rating'):
        re = se_find_rating_value(any_list)
    elif(condition == 'number_of_reviews'):
        re = se_find_number_of_reviews_value(any_list)
    elif(condition == 'origin'):
        re = se_find_origin_value(any_list)
    elif(condition == 'brand'):
        re = se_find_brand_value(any_list)
    return re


#조건 sql 내보내는 함수
def select_where (some_list_stemming, some_list_simplify):

    column_name = se_find_condition (some_list_stemming)
    value_name = se_find_condition_value(some_list_simplify, column_name)
  
    if(column_name == 'price'):
        if(value_name == 'superlative'):
            sql_result = " ORDER BY " + column_name + " ASC LIMIT 1"
        else:
            sql_result = " AND " + column_name + " < " + value_name
    
    elif(column_name == 'rating' or column_name == 'number_of_reviews'):
        if(value_name == 'superlative'):
            sql_result = " ORDER BY " + column_name + " DESC LIMIT 1"
        else:
            sql_result = " AND " + column_name + " > " + value_name
    
    else:
        sql_result = " AND " + column_name + " = '" + value_name + "'"
  
    return sql_result


# 조건이 1개일때
def select_one_func(some_list):
  
    some_list_stemming = se_stemming(some_list)
    some_list_simplify = se_simplify(some_list_stemming)
  
    category = se_find_category_value(some_list_simplify)
    cate = category[0]
    cate_value = category[1]

    where_1 = select_where(some_list_stemming, some_list_simplify)

    sql_result = "SELECT * FROM product WHERE " + cate + " = '" + cate_value + "'" + where_1

    return sql_result


# 조건이 1개일때
def select_one_count_func(some_list):
  
    some_list_stemming = se_stemming(some_list)
    some_list_simplify = se_simplify(some_list_stemming)

    category = se_find_category_value(some_list_simplify)
    cate = category[0]
    cate_value = category[1]

    where_1 = select_where(some_list_stemming, some_list_simplify)

    sql_result = "SELECT COUNT(*) FROM product WHERE " + cate + " = '" + cate_value + "'" + where_1

    return sql_result


# 조건이 2개일때
def select_two_func(some_list):
  
    for i in range(0, len(some_list)):
        if(user_saying[i] == "and"):
            A = some_list[0:i]
            B = some_list[i+1:len(some_list)] 
    
    A_stemming = se_stemming(A)
    A_simplify = se_simplify(A_stemming)

    B_stemming = se_stemming(B)
    B_simplify = se_simplify(B_stemming)

    category = se_find_category_value(A_simplify)
    cate = category[0]
    cate_value = category[1]

    where_1 = select_where(A_stemming, A_simplify)
    where_2 = select_where(B_stemming, B_simplify)

    sql_result = "SELECT * FROM product WHERE " + cate + " = '" + cate_value + "'" + where_1 + where_2

    return sql_result



# 조건이 2개일때
def select_two_count_func(some_list):
  
    for i in range(0, len(some_list)):
        if(some_list[i] == "and"):
            A = some_list[0:i]
            B = some_list[i+1:len(some_list)] 
    
    A_stemming = se_stemming(A)
    A_simplify = se_simplify(A_stemming)

    B_stemming = se_stemming(B)
    B_simplify = se_simplify(B_stemming)

    category = se_find_category_value(A_simplify)
    cate = category[0]
    cate_value = category[1]

    where_1 = select_where(A_stemming, A_simplify)
    where_2 = select_where(B_stemming, B_simplify)

    sql_result = "SELECT COUNT(*) FROM product WHERE " + cate + " = '" + cate_value + "'" + where_1 + where_2

    return sql_result


#error 확인
def error_msg(se_sql):
    re = 'normal'
    if 'NAN' in se_sql:
        re = 'error'
    
    return re


def select_func(some_list):
    for i in range(0, len(some_list)):
        if(some_list[i]=='and'):
            sql = select_two_func(some_list)
            break
        else:
            sql = select_one_func(some_list)
    
    error_check = error_msg(sql)
    if(error_check == 'error'):
        return error_check
    else:
        return sql


def select_count_func(some_list):
    for i in range(0, len(some_list)):
        if(some_list[i]=='and'):
            sql = select_two_count_func(some_list)
            break
        else:
            sql = select_one_count_func(some_list)
    
    error_check = error_msg(sql)
    if(error_check == 'error'):
        return error_check
    else:
        return sql