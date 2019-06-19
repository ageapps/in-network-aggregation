def median_of_medians(values):
    MAX_VALUES = 6
    NUM_NODES = len(values[0])
    batch_number = 3
    # Get odd or even with bitwise opperation
    if (NUM_NODES & 1) == 0:
        # print("Even number")
        ODD_NODE_NUMBER = 0
    else:
        # print("Odd number")
        ODD_NODE_NUMBER = 1
    
    print("Number of nodes:{} batches:{}".format(NUM_NODES, len(values)))
    assert NUM_NODES <= MAX_VALUES, "This algorithm only supports sorting of at most {} values".format(MAX_VALUES)
    batch_register = [0]*batch_number
    median_register = [0]*MAX_VALUES

    for row in values:
        batch_counter = 0
        median_counter = 0

        for index in range(NUM_NODES):
            value = row[index]
            temp = value
            temp2 = value

            # insertion sort in batch
            current_index = 0
            temp_value = batch_register[current_index]
            if batch_counter > 0 and temp < temp_value:
                temp = batch_register[current_index]
                temp_value = value
            batch_register[current_index] = temp_value
            
            current_index += 1
            temp_value = batch_register[current_index]
            if batch_counter > 1 and temp < temp_value:
                temp2 = temp_value
                temp_value = temp
                temp = temp2
            batch_register[current_index] = temp_value

            batch_register[batch_counter]=temp
            print("Register:{}".format(batch_register))

            if batch_counter == batch_number-1:
                # batch is full, get median and reset counter
                value = batch_register[1]
                temp = value
                temp2 = value

                # insertion sort in medians batch
                current_index = 0
                temp_value = median_register[current_index]
                if median_counter > 0 and temp < temp_value:
                    temp = median_register[current_index]
                    temp_value = value
                median_register[current_index] = temp_value
                
                current_index += 1
                temp_value = median_register[current_index]
                if median_counter > 1 and temp < temp_value:
                    temp2 = temp_value
                    temp_value = temp
                    temp = temp2
                median_register[current_index] = temp_value

                median_register[median_counter]=temp
                print("Medians:{}".format(median_register))

                median_counter += 1
                batch_counter = -1
            
            batch_counter += 1 
        
        if batch_counter > 0:
            median_register[median_counter] = batch_register[batch_counter-1]
            median_counter +=1

        print("Medians:{}".format(median_register))
        if median_counter == 1:
            v1 = median_register[0]
            v2 = median_register[0]
        elif median_counter == 2:
            v1 = median_register[0]
            v2 = median_register[1]
        else:
            v1 = median_register[1]
            v2 = median_register[1]
        print("Median is: {}+{}/2 = {}".format(v1,v2,(v1+v2)/2))
