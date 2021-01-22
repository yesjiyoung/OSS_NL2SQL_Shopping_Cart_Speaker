# column 명을 찾는 함수
def up_find_column_name (any_list):
    column_name = 'NAN'
    for i in range(0,len(any_list)):
     if (any_list[i] == 'column'):
       column_name = any_list[i-1]
       break
    return column_name

# 변경값 찾는 함수 
def find_new_value (any_list):
    new_value = 'NAN'
    for i in range(0,len(any_list)):
     if (any_list[i] == 'to'):
       new_value = any_list[i+1]
       break

    ###<추가> ★ 중요 ★ 변경 값이 문자이면, 
    if new_value.isalpha() : # '1', 'male'
      return "'" + new_value + "'" # ''male''
    return new_value # '1'

# comma 찾는 함수 (if 절과 주절을 분리시켜주는 그 ','의 위치를 뽑아내보자)
def find_comma_index(any_list):
    comma_index = 1000
    for i in range(0,len(any_list)):
     if (any_list[i] == ','):
       comma_index = i
       break
    return comma_index

# 조건에 해당하는 value 찾는 함수
def find_condition_value(any_list):
   condition_value = 'NAN'
   for i in range(0,len(any_list)):
     if (any_list[i] == 'is' or any_list[i] == 'are'):
       condition_value = any_list[i+1]
       break

        ###<추가> ★ 중요 변경 값이 문자이면, 
   if condition_value.isalpha() : 
     return "'" + condition_value + "'"
   return condition_value


# 'and'찾는 함수 ('and'의 위치를 뽑아내보자))
def find_and_index(any_list):
    and_index = 1000
    for i in range(0,len(any_list)):
     if (any_list[i] == 'and'):
       and_index = i
       break
    return and_index


def update_type1(some_list):
  table_name = find_table_name(some_list)
  column_name = up_find_column_name(some_list)
  new_value = find_new_value(some_list)

  sql_result = "UPDATE " + table_name.upper() + " SET " + column_name.upper() + " = " + new_value 
  return sql_result

def update_type2(some_list):
  comma_index = find_comma_index(some_list)
  condition_saying = some_list[:comma_index] 
  command_saying = some_list[comma_index +1 : ]
  where_output = " WHERE " + up_find_column_name(condition_saying).upper() + " = " + find_condition_value(condition_saying)
  command_output = "UPDATE " + find_table_name(condition_saying).upper() + " SET " + up_find_column_name(command_saying).upper() + " = " + find_new_value(command_saying)
  sql_result = command_output + where_output
  return sql_result

def update_type3(some_list):
  comma_index = find_comma_index(some_list)
  condition_saying = user_saying[:comma_index] 
  command_saying = user_saying[comma_index +1 : ]
  and_index = find_and_index(command_saying)
  command1_saying = command_saying[:and_index]
  command2_saying = command_saying[and_index+1:]
  where_output = " WHERE " + up_find_column_name(condition_saying).upper() + " = " + find_condition_value(condition_saying)
  command_output = "UPDATE " + find_table_name(condition_saying).upper() + " SET " + up_find_column_name(command1_saying).upper() + " = " + find_new_value(command1_saying) + ", " + up_find_column_name(command2_saying).upper() + " = " + find_new_value(command2_saying)
  sql_result = command_output + where_output

  return sql_result


def update_sql(user_saying):
  
  # Type1) 만약 'all'이라는 단어를 포함하는가? -> 1) UPDATE 테이블명 SET 컬럼명 = 변경할 값
  if 'all' in user_saying :
    sql_result = update_type1(user_saying) # Type1


  # Type2 & Type3) 만약 'If'라는 단어를 포함하는가?
  if 'If' in user_saying :    
    # 여러 개의 수정을 요청하는가 ?'and'
    if 'and' in user_saying:
      sql_result = update_type3(user_saying) # Type3
    else :
      sql_result = update_type2(user_saying) # Type2

  return sql_result 

