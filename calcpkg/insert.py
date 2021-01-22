# insert 함수 내부 함수 정의
# table 찾는 함수
def find_table_name (any_list):
  table_name = "NAN"
  for i in range(0,len(any_list)):
    if(any_list[i] == 'table'):
      table_name = any_list[i-1]
      break
  return table_name
# value 찾는 함수
def in_find_values_name(any_list) :
  values_name = ''
  a = ''
  b = ''
  for i in range(0, len(any_list)):
    if(any_list[i] == 'values'):
      for j in range(1,i):
        if(any_list[i-j]=='the' or any_list[i-j] == 'of'):
          break
        if(any_list[i-j] != 'and'):
          a = any_list[i-j]
          if a.isalpha():
            b = "'" + a + "'"
          else:
            b = a
          values_name = values_name + b + ' '  
  return values_name  


# column 찾는 함수
def in_find_columns_name(any_list) :
  columns_name = ''
  num = 0
  for i in range(0, len(any_list)):
    if(any_list[i] == 'columns'):
      num = 1
      for j in range(1,i):
        if(any_list[i-j] == 'the' or any_list[i-j] == 'of'):
          break
        else:
          if(any_list[i-j] != 'and'):
            columns_name = columns_name + any_list[i-j] + ' '
  return columns_name, num

# insert 함수 만들기
def insert_sql(user_saying) :

  table_name = find_table_name(user_saying)
  
  values_name = in_find_values_name(user_saying)

  columns_name, num = in_find_columns_name(user_saying)

  

  # column이 있을 경우 (num == 1일 때)와 그렇지 않을 경우 결과 값 나누기
  if(num == 1):
    return_insert_sql = 'INSERT INTO ' + table_name.upper() + '(' + columns_name + ') ' + 'VALUES (' + values_name + ')'
  else:
    return_insert_sql = 'INSERT INTO ' + table_name.upper() + ' VALUES (' + values_name + ')'

  return return_insert_sql