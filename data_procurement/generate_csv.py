import os

#open files
ionic_compositions = open('ionic_comps.csv', 'r').readlines()
input_outline = open('outline.csv', 'r+').readlines()

#keep track of file num
curr_file_num = 1
#keep track of line # to determine ratios
line_num = 0
#keep track of imbalance due to floating point multiplication error
num_imbalanced = 0

#list to hold new csv files
new_files = [] 

ratio = 1

if not os.path.exists('CSV\'s'):
    os.mkdir('CSV\'s') 

for comp in ionic_compositions:
    #loop through all the ionic compositions
    comp = comp.replace(',', ' ')
    ion_list = comp.split()
    
    for i in range(0, 4):
        new_files.append(open('CSV\'s/' + str(curr_file_num + i) + '.csv', 'w+'))
    
    #write the proper values to the new csv
    for line in input_outline:
        line = line.replace(',', ' ')
        line = line.split()
        
        if line_num % 10 == 0 and line_num != 0:
            ratio *= 0.9
        
        pos = 0
        neg = 0
        for i in range(0,9):
            ion = float(ion_list[i])
            ion *= ratio

            pos = 0
            neg = 0

            if i < 3:
                pos += ion
            else:
                if i == 3:
                    neg += ion * 2
                else:
                    neg += ion

            line[i+6] = str(ion)            

        for i in range(0, 4):
            line[0] = str(273.15 + (10 * i))
            line_str = ','.join(line)
            new_files[i].write(line_str + '\n')

        if pos != neg:
            num_imbalanced += 1

        line_num += 1
        
    #reset variables
    new_files.clear()
    curr_file_num += 4
    line_num = 0
    ratio = 1

print("Number of imbalance compounds: " + str(num_imbalanced))


