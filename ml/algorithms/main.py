import statistics
from recursive import *
from insertion import *



def main():
    values = [
        [-2, 3, 4, 1,3],
        [1, 2, 1, 3, 4]
    ]
    print("Reference medians are: {}".format([statistics.median(row) for row in values]))

    # recursive_sort(values)
    insertion_sort(values)


if __name__ == "__main__":
    main()
