import numpy as np

# print(np.__version__)

# array =np.array([1,2,3])

# array = array * 2
# print(array)
# print(type(array))

# array = np.array([['A', 'B', 'C'],
#                   ['D', 'E', 'F'],
#                   ['G', 'H', 'I']])
# print(array.ndim)
# print(array.shape)
# word = array[0,0] +array[1, 2] + array[2,0 ]
# print(word)

array = np.array([[1,2,3,4],
                  [5,6,7,8],
                  [9,10,11,12],
                  [13,14,15,16]])

# array[start:end:step]

print(array[0:2, 0:2])