#from nltk.tokenize import word_tokenize

from calcpkg.select import select_sql
from calcpkg.delete import delete_sql
from calcpkg.insert import insert_sql
from calcpkg.update import update_sql



def making_sql(user_saying):
  
  select_array = ['select', 'show'] #0,1
  delete_array = ['delete', 'remove', 'erase','clear'] #2,3,4,5
  update_array = ['update', 'change', 'revise', 'modify'] #6,7,8,9
  insert_array = ['insert', 'put', 'add', 'enter'] #10,11,12,13

  command_array = select_array + delete_array + update_array + insert_array
  command_array
  
  # result 값 알아내기 ( result : 어떤 종류의 명령어인지.) 
  for i in range(0, len(command_array)):
    for j in range(0, len(user_saying)):  # ★ 01/03/20:40 코드 수정 ★ : 꼭 user_saying[0]에만 해당 명령어 있을 필요없을 거 같아서 이 부분만 수정했어요! user_saying 리스트의 요소 하나하나 체크해보기 위해, for(j)문으로 돌렸습니다. 
      if (user_saying[j] == command_array[i]):
       result = i
       break

  # result에 따라 sql문 작성하기.
  if (result == 0 or result == 1):
    return_sql =  select_sql(user_saying) # 건호 : select_sql(user_saying)

  if (result == 2 or result == 3 or result == 4 or result == 5):
    return_sql =  delete_sql(user_saying) # 석용 : delete_sql(user_saying)

  if (result == 6 or result == 7 or result == 8 or result == 9):
    return_sql =  update_sql(user_saying) # 지영 : update_sql(user_saying)

  if (result == 10 or result == 11 or result == 12 or result == 13):
    return_sql =  insert_sql(user_saying) # 유미 : insert_sql(user_saying)

  return return_sql


user_saying = ['enter', 'the', '19', ',', 'female', ',', 'and', 'A+', 'values', 'in', 'the', 'Age', ',', 'Gender', ',', 'and', 'Grade', 'columns', 'of', 'the', 'student', 'table', '.']
print(making_sql(user_saying))
