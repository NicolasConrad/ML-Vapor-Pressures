import os

#open files
ionic_compositions = open('ionic_comps.csv', 'r').readlines()
input_outline = open('outline.csv', 'r+').readlines()

#keep track of file num
curr_file_num = 1

#keep track of line # to determine ratios
line_num = 0
ratio = 1

if not os.path.exists('CSV\'s'):
    os.mkdir('CSV\'s') 

for comp in ionic_compositions:
    #loop through all the ionic compositions
    comp = comp.replace(',', ' ')
    ion_list = comp.split()

    #create the new csv file
    new_file = open('CSV\'s/' + str(curr_file_num) + '.csv', 'w+')
    
    #write the proper values to the new csv
    for line in input_outline:
        line = line.replace(',', ' ')
        line = line.split()
        
        if line_num % 5 == 0 and line_num != 0:
            ratio *= 0.75
        
        for i in range(0,9):
            ion = float(ion_list[i])
            ion *= ratio
            line[i+6] = str(ion)
            
        line_str = ','.join(line)
        new_file.write(line_str + '\n')

        line_num += 1

    #reset variables
    curr_file_num += 1
    line_num = 0
    ratio = 1
