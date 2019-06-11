

def sort_array(register, value_counter, check_counter, value, max_counter):

    temp = value
    # stop condition
    # - if we have iterated through all elements (NUM_NODES)
    # - if the check reference is higher or eq to the las value index
    if check_counter >= max_counter or check_counter >= value_counter:
        # print("Finished recursive")
        return register, temp

    # print("Register: {}, VC:{}, C:{}, V:{}".format(register, value_counter, check_counter, value))

    # if the new element is lower than the last value stored
    if temp < register[check_counter]:
        # if the last value stored is the first, just rewrite it, save old value in temp
        if check_counter == 0:
            temp = register[check_counter]
            register[check_counter] = value

        # save the last value stored, rewrite it, save old value in temp
        else:
            temp2 = register[check_counter]
            register[check_counter] = temp
            temp = temp2

    # call recursively increasing the index to check and the new temp variable
    return sort_array(register, value_counter, check_counter+1, temp, max_counter)


def recursive_sort(values):
    NUM_NODES = len(values[0])
    # Get odd or even with bitwise opperation
    if (NUM_NODES & 1) == 0:
        # print("Even number")
        ODD_NODE_NUMBER = 0
    else:
        # print("Odd number")
        ODD_NODE_NUMBER = 1
    
    print("Number of nodes:{} batches:{}".format(NUM_NODES, len(values)))

    for row in values:
        register = [-1]*NUM_NODES
        counter = -1
        m_index = -1

        for index in range(NUM_NODES):
            value = row[index]
            counter += 1

            if counter == 0:
                register[0] = value
                continue

            arr, finish = sort_array(register, counter, 0, value, NUM_NODES)
            arr[counter] = finish
            # print("Reg: {}".format(arr))

            if counter*2 == NUM_NODES-1 or counter*2 == NUM_NODES:
                # print("Saving index {}".format(counter))
                m_index = counter

            print("Value:{} Register:{}".format(row[index], register))

        v1 = register[m_index]
        v2 = v1
        if ODD_NODE_NUMBER <= 0:
            v2 = register[m_index-1]

        print("V1:{} V2:{} => Median is:{}".format(v1, v2, (v1+v2)/2))
