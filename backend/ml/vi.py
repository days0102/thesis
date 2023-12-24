'''
Author       : Outsider
Date         : 2023-12-21 20:07:44
LastEditors  : Outsider
LastEditTime : 2023-12-21 20:07:53
Description  : In User Settings Edit
FilePath     : \thesis\backend\ml\vi.py
'''
# Variation of information (VI)
#
# Meila, M. (2007). Comparing clusterings-an information
#   based distance. Journal of Multivariate Analysis, 98,
#   873-895. doi:10.1016/j.jmva.2006.11.013
#
# https://en.wikipedia.org/wiki/Variation_of_information


from math import log

def variation_of_information(X, Y):
  n = float(sum([len(x) for x in X]))
  sigma = 0.0
  for x in X:
    p = len(x) / n
    for y in Y:
      q = len(y) / n
      r = len(set(x) & set(y)) / n
      if r > 0.0:
        sigma += r * (log(r / p, 2) + log(r / q, 2))
  return abs(sigma)

if __name__=='__main__':

    # Identical partitions
    X1 = [ [1,2,3,4,5], [6,7,8,9,10] ]
    Y1 = [ [1,2,3,4,5], [6,7,8,9,10] ]
    print(variation_of_information(X1, Y1))
    # VI = 0

    # Similar partitions
    X2 = [ [1,2,3,4], [5,6,7,8,9,10] ]
    Y2 = [ [1,2,3,4,5,6], [7,8,9,10] ]
    print(variation_of_information(X2, Y2))
    # VI = 1.102

    # Dissimilar partitions
    X3 = [ [1,2], [3,4,5], [6,7,8], [9,10] ]
    Y3 = [ [10,2,3], [4,5,6,7], [8,9,1] ]
    print(variation_of_information(X3, Y3))
    # VI = 2.302

    # Totally different partitions
    X4 = [ [1,2,3,4,5,6,7,8,9,10] ]
    Y4 = [ [1], [2], [3], [4], [5], [6], [7], [8], [9], [10] ]
    print(variation_of_information(X4, Y4))
    # VI = 3.322 (maximum VI is log(N) = log(10) = 3.322)