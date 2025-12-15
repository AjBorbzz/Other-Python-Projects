def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]          # element to insert
        j = i - 1
        
        # shift elements greater than key to the right
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        # insert key at the correct position
        arr[j + 1] = key

    return arr


data = [8, 3, 5, 2]
# print(insertion_sort(data))

# another insertion code
def insert_sorted(arr, idx):
    value = arr.pop(idx)

    # find insertion position
    for i, x in enumerate(arr):
        if value < x:
            arr.insert(i, value)
            break
    else:
        arr.append(value)

    return arr


t = insert_sorted([2, 7, 15, 24, 10, 3, 4, 1, 0], 4)
print(t)