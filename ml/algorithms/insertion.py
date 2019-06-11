

def insertion_sort(values):
    MAX_VALUES = 5
    NUM_NODES = len(values[0])
    # Get odd or even with bitwise opperation
    if (NUM_NODES & 1) == 0:
        # print("Even number")
        ODD_NODE_NUMBER = 0
    else:
        # print("Odd number")
        ODD_NODE_NUMBER = 1
    
    print("Number of nodes:{} batches:{}".format(NUM_NODES, len(values)))
    assert NUM_NODES == MAX_VALUES, "This algorithm only supports sorting of at most {} values".format(MAX_VALUES)

    for row in values:
        register = [-1]*NUM_NODES
        counter = 0
        m_index = -1

        for index in range(MAX_VALUES):
            value = row[index]
            temp = value
            
            if counter > 0 and temp < register[0]:
                temp = register[0]
                register[0] = value

            if counter > 1 and temp < register[1]:
                temp2 = register[1]
                register[1] = temp
                temp = temp2

            if counter > 2 and temp < register[2]:
                temp2 = register[2]
                register[2] = temp
                temp = temp2

            if counter > 3 and temp < register[3]:
                temp2 = register[3]
                register[3] = temp
                temp = temp2

            register[counter] = temp

            if counter*2 == NUM_NODES-1 or counter*2 == NUM_NODES:
                print("Saving index {}".format(counter))
                m_index = counter

            counter += 1
            print("Value:{} Register:{}".format(row[index], register))

        v1 = register[m_index]
        v2 = 0
        if ODD_NODE_NUMBER <= 0:
            v2 = register[m_index-1]

        print("Median is:{}".format(v1+v2/2))
