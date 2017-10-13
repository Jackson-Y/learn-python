# -*- coding: utf-8 -*-

def binary_search(arr, x):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (int)((low + high) / 2)
        if arr[mid] < x:
            low = mid + 1
        elif arr[mid] > x:
            high = mid - 1
        else:
            return mid
    return -1

if __name__ == '__main__':
    arr = [1, 3, 5, 7, 9, 10]
    print(binary_search(arr, 5))
    print(binary_search(arr, 6))
    print(binary_search(arr, 7))
