# Lists are both subscriptable and mutable.

# Define a function to operate on an index:
def square(num_list):
    for i in range(len(num_list)):
        num_list[i] = 300



def main():
    sm = [4,232,2,1,23]
    square(sm)
    print(sm)
if __name__ == "__main__":
    main()