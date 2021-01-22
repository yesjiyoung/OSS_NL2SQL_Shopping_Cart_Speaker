def delete_sql(any_list):


# 테이블에 모든 값을 삭제할 것인지(조건이 없을 때)★경우1★과 조건이 있는 레코드들을 삭제할 때★경우2★ 분류
  if 'all' in any_list:# 테이블이 모든 값을 삭제할 때 (조건이 없을 때) ★경우 1★
     for i in range (0, len(any_list)):
        if (any_list[i]=='table'):# table 찾기
            table_name = any_list[i-1]
     return_sql = "DELETE " + "FROM " + table_name.upper() # 경우1) 결과 sql문 도출
     return return_sql

  else:# 조건이 있는 레코드들을 삭제할 때 ★경우 2★
    table_name_2 = "nan"
    colum_name = "nan"
    for i in range (0, len(any_list)):
        if (any_list[i] == 'table'):# table 찾기
            table_name_2 = any_list[i-1]
        if (any_list[i] == 'data'):# column 찾기
            column_name = any_list[i-1]
            data_index = i-1
            
    condition_value = any_list[data_index -1]# 조건 찾기
    if condition_value.isalpha():
        a = "'" + condition_value + "'"
    else:
        a = condition_value
    return_sql = "DELETE " + "FROM " + table_name_2.upper() + " WHERE " + column_name.upper() + " = " + a # 경우2) 결과 sql문 도출
    return return_sql
