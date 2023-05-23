import os
import pandas as pd
import requests

'''
Create a list to hold the relative humidities, dict to hold moles of H+, NH4+,
Na+, SO42−, NO3−, Cl−, Br−, OH−
'''
#column names for data frame
col_names = ['RH', 'N_H+(mol)', 'N_NH4+(mol)','N_Na+(mol)', 'N_SO42-(mol)',
             'N_NO3-(mol)', 'N_Cl-(mol)', 'N_OH-(mol)', 'N_NH3-(mol)',
             'Water Content(mol)', 'P_HNO3(atm)', 'P_HCL(atm)', 
             'P_NH3(atm)', 'P_H2SO4(atm)', 'P_HBr(atm)']

#names of ions being used for Model III
ions = ['H+', 'NH4+', 'Na+', 'SO42-', 'NO3-', 'Cl-', 'OH-', 'NH3']

#create a list to store relative humidities in
relative_humidities = []

#create a dictionary to store the amount of each ion for each calculation
mol_values = {}

#initialize the dictionary with keys from values of ions list
for ion in ions:
    mol_values[ion] = []

#used to indicate if the lines currently being read include values that we need
#   --> water content and pressure values
water_content_lines = False
pressure_lines = False

#create list to hold water content values
water_content = []
#create dictionary to hold pressure values
pressure_vals = {'HNO3': [], 'HCL': [], 'NH3': [], 'H2SO4': [], 'HBr': []}
gases = ['HNO3', 'HCL', 'NH3', 'H2SO4', 'HBr'] 
#temperature in Kelvin
temperature = 298.15


for filename in os.listdir('CSV\'s'):
    #open csv file, read from it
    csv = open('CSV\'s/' + filename, 'r')
    #Grab necessary input data --> relative humidities and amount of each ion
    print('Generating data from: ' + filename)
    for line in csv.readlines():
        line = line.split(',')
        relative_humidities.append(float(line[5]))
        ion_index = 6
        for ion in ions:
            mol_values[ion].append(line[ion_index])
            if ion_index == 11:
                ion_index += 2 #skip Br-
                continue
            ion_index += 1
                    
    csv.close()
                
    #reopen csv file to input to for POST request
    #replace \n with \r\n to comply with input requirements in E-AIM
    batch = open('CSV\'s/' + filename, 'r')
    batch = batch.read().rstrip()
    batch = batch.replace('\n', '\r\n')
    
    #generate a payload for the type of calculation we want in E-AIM
    payload = {'wwwUsageType': 'calculation', 'wwwInputMode': 'batch', 
            'Model': 'ModelIII', 'iCaseInorg': 1, 'ExcludeWater': 'y',
            'wwwOutputMode': 'column', 'nCompounds': 0, 'tf': batch}

    #make a POST request to calculate values for training data
    r = requests.post('http://www.aim.env.uea.ac.uk/cgi-bin/eaim', data=payload)

    count = 0
    loopcount = 0
    water_content_lines = False
    pressure_lines = False   

    #loop through the lines of the output text to grab necessary data values
    for line_bytes in r.iter_lines():
        line_str = line_bytes.decode('utf-8')
        '''
        check if the length of the line is 0
            --> if yes, continue because we don't need to do anything w/ them
        '''
        if len(line_str) == 0:
            water_content_lines = False
            pressure_lines = False   
            count = 0
            loopcount = 0
            continue

        #get the water content
        if water_content_lines:
            wordlist = line_str.split()
            #convert from string to float
            exp = int(wordlist[count][-3:])
            magnitude = float(wordlist[count][0:7])
            water_content_float = magnitude * (10 ** exp)

            #store float in list
            water_content.append(water_content_float)

        if pressure_lines:
            wordlist = line_str.split()
            loopcount = count

            #Sometimes line were missing outputs which messed up the parsing
            #this adjust variable helps adjust the indexes in case lines are missing
            adjust = 0

            if(len(wordlist) < count + 4):
                adjust = count + 5 - len(wordlist)
                #adjust count and loopcount variables for this line
                count -= adjust
                loopcount = count
                print(filename)

            while True:
                if wordlist[loopcount] != '0.00000E+00':  
                    #convert from string to float
                    exp = int(wordlist[loopcount][-3:])
                    magnitude = float(wordlist[loopcount][0:7])
                    pressure_float = magnitude * (10 ** exp)
                    
                    #determine the type of gas
                    if loopcount - count == 0:
                        pressure_vals['HNO3'].append(pressure_float)
                    elif loopcount - count == 1:
                        pressure_vals['HCL'].append(pressure_float)
                    elif loopcount - count == 2:
                        pressure_vals['NH3'].append(pressure_float)
                    elif loopcount - count == 3:
                        pressure_vals['H2SO4'].append(pressure_float)
                    elif loopcount - count == 4:
                        pressure_vals['HBr'].append(pressure_float)  
                        break  
                else:
                    if loopcount - count == 0:
                        pressure_vals['HNO3'].append(float(0))
                    elif loopcount - count == 1:
                        pressure_vals['HCL'].append(float(0))
                    elif loopcount - count == 2:
                        pressure_vals['NH3'].append(float(0))
                    elif loopcount - count == 3:
                        pressure_vals['H2SO4'].append(float(0))
                    elif loopcount - count == 4:
                        pressure_vals['HBr'].append(float(0))
                        break
                    
                loopcount += 1

            #unadjust the count for next lines
            count -= adjust

        #find the index of the water content
        #then in the next line we can use the count variable to find the value(s)
        if line_str[1] == 'I' and 'iFail' in line_str:
            wordlist = line_str.split()
            water_content_lines = True

            for header in wordlist:
                if header == 'n_H2O(aq)':
                    count -= 1
                    break
                count += 1

        if line_str[1] == 'I' and 'Density(aq)' in line_str:
            wordlist = line_str.split()
            pressure_lines = True

            for header in wordlist:
                if header == 'p_HNO3(g)':
                    break
                count += 1

data = pd.DataFrame(zip(relative_humidities, mol_values['H+'], 
                            mol_values['NH4+'], mol_values['Na+'], 
                            mol_values['SO42-'], mol_values['NO3-'],
                            mol_values['Cl-'], mol_values['OH-'],
                            mol_values['NH3'], water_content, 
                            pressure_vals['HNO3'], pressure_vals['HCL'], 
                            pressure_vals['NH3'], pressure_vals['H2SO4'], 
                            pressure_vals['HBr']), columns=col_names)
'''
tempdf = pd.DataFrame(zip(relative_humidities, mol_values['H+'], 
                            mol_values['NH4+'], mol_values['Na+'], 
                            mol_values['SO42-'], mol_values['NO3-'],
                            mol_values['Cl-'], 
                            mol_values['OH-'], water_content, 
                            pressure_vals['HNO3'], pressure_vals['HCL'], 
                            pressure_vals['NH3'], pressure_vals['H2SO4'], 
                            pressure_vals['HBr']), columns=col_names)
    data = pd.concat([data, tempdf], axis=0)
'''

data.insert(0, 'Temp(K)', 298.15)
print(data)

data.to_csv('model_data.csv')





