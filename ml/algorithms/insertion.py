

def insertion_sort(values):
    MAX_VALUES = 6
    NUM_NODES = len(values[0])
    # Get odd or even with bitwise opperation
    if (NUM_NODES & 1) == 0:
        # print("Even number")
        ODD_NODE_NUMBER = 0
    else:
        # print("Odd number")
        ODD_NODE_NUMBER = 1
    
    print("Number of nodes:{} batches:{}".format(NUM_NODES, len(values)))
    assert NUM_NODES <= MAX_VALUES, "This algorithm only supports sorting of at most {} values".format(MAX_VALUES)
    register = [10]*MAX_VALUES

    for row in values:
        counter = 0
        m_index = -1

        for index in range(NUM_NODES):
            value = row[index]
            temp = value
            
            current_index = 0
            temp_value = register[current_index]
            if counter > 0 and temp < temp_value:
                temp = register[current_index]
                temp_value = value
            
            register[current_index] = temp_value

            current_index += 1
            temp_value = register[current_index]
            if counter > 1 and temp < temp_value:
                temp2 = temp_value
                temp_value = temp
                temp = temp2
            
            register[current_index] = temp_value

            current_index += 1
            temp_value = register[current_index]
            if counter > 2 and temp < temp_value:
                temp2 = temp_value
                temp_value = temp
                temp = temp2
            register[current_index] = temp_value

            current_index += 1
            temp_value = register[current_index]
            if counter > 3 and temp < register[current_index]:
                temp2 = temp_value
                temp_value = temp
                temp = temp2
            register[current_index] = temp_value

            current_index += 1
            temp_value = register[current_index]
            if counter > 4 and temp < temp_value:
                temp2 = temp_value
                temp_value = temp
                temp = temp2
            register[current_index] = temp_value

            
            register[counter] = temp

            if counter*2 == NUM_NODES-1 or counter*2 == NUM_NODES:
                #print("Saving index {}".format(counter))
                m_index = counter

            counter += 1
            print("Register:{}".format(register))

        v1 = register[m_index]
        v2 = v1
        if ODD_NODE_NUMBER <= 0:
            v2 = register[m_index-1]

        print("Median is: {}+{}/2 = {}".format(v1,v2,(v1+v2)/2))
