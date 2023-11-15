list1 = [1, 2, 3, 4, 5]
list2 = [6, 7, 8, 9, 0]

dict = {col: "duck" for col in list1}
print(dict)
dict.update({col: "moose" for col in list2})
print(dict)