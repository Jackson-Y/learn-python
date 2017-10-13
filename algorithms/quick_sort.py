""" Quick sort function. """
# -*- coding: utf-8 -*-
import random

def partition(arr, low, high):
    pivot = arr[high]
    pivot_index = low - 1
    for i in range(low, high):
        if arr[i] < pivot:
            pivot_index += 1
            arr[i], arr[pivot_index] = arr[pivot_index], arr[i]
    arr[pivot_index + 1], arr[high] = arr[high], arr[pivot_index + 1]
    return pivot_index + 1

def quick_sort(arr, low, high):
    if low < high:
        k = partition(arr, low, high)
        quick_sort(arr, low, k - 1)
        quick_sort(arr, k + 1, high)

if __name__ == '__main__':
    a = []
    for i in range(10):
        a.append(random.randint(1, 100))
    print(a)
    quick_sort(a, 0, len(a)-1)
    print(a)
