# SELECT XXXXXX
def se_find_column_name (any_list):
  column_name = 'NAN'
  for i in range(0, len(any_list)):
    if(any_list[i] == 'column'):  
      column_name = any_list[i-1]
      
  return column_name

# FROM XXXXXXX
def find_table_name (any_list):
  table_name = "NAN"
  for i in range(0,len(any_list)):
    if(any_list[i] == 'table'):
      table_name = any_list[i-1]
      break
  return table_name

# WHERE XXXXX
def find_condition_name (any_list):
  condition_name = "NAN"

  for i in range(0,len(any_list)):
    if(any_list[i] == 'column'):
      condition_name = any_list[i-1]
      break
  return condition_name


# WHERE XXXXXX = 'XXXXXXX'
def find_condition_result_name(any_list):
  condition_result ="NAN"
  for i in range(0, len(any_list)):
    if(any_list[i] == 'is' or any_list[i] == 'are'):
      condition_result = any_list[i+1]
      break

  if condition_result.isalpha():
    return  "'" + condition_result + "'"
  else:
    return condition_result




# 이 함수는 조건절이 포함된 문장의 함수이며 위에서 se_find_column_name , find_table_name , find_condition_name , find_condition_result_name 서브함수들이 포함된 함수
def select_type1(some_list):
  # 조건절 주절분리
  
  column_name = se_find_column_name(some_list)
  table_name = find_table_name(some_list)
  condition_name = find_condition_name(some_list)
  condition_result_name = find_condition_result_name(some_list)

  sql_result = "SELECT " + column_name .upper() + " FROM " + table_name.upper() + " WHERE " + condition_name.upper() + " = " + condition_result_name
  return sql_result


# 이 함수는 조건절이 포함되지 않은 함수이며 위에서 se_find_column_name , find_table_name 서브함수들이 필요한 함수
def select_type2(some_list):
  # 조건절 주절분리
  
  column_name = se_find_column_name(some_list)
  table_name = find_table_name(some_list)
  #condition_name = find_condition_name(some_list)
  #condition_result_name = find_condition_result_name(some_list)

  sql_result = "SELECT " + column_name.upper() + " FROM " + table_name.upper()
  return sql_result


def select_sql(user_saying):
  ## if 이라는 단어를 포함하는가
  ## 조건문이 포함된 경우 
  if 'If' in user_saying:
    sql_result = select_type1(user_saying)
  ## 조건문을 포함하지 않는 경우
  else :
    sql_result = select_type2(user_saying)

  return sql_result
  