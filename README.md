# Creating neural networks as replacement for inorganic thermodynamic models
Working under professor Anthony Wexler, I am working to create neural networks to replicate inorganic thermodynamic models that will be able to be used on a GPU and make much faster calculations

## Sub Directories
### model_data
In this subdirectory are tools which I used to automate the generation of training data from professor Wexler's E-AIM thermodynamic model. 
- generate_csv.py: requires that a file "ionic_comps.csv" and "outline.csv" are provided within the same sub directory. ionic_comps.csv is a csv file containing the compositions for which you want to generate data for. From there, the python script generates different ratios of these compositions at different relative humidities and temperatures, and stores them in files of the structure outline.csv, which can be interpreted by E-AIM. 
- generate_data.py: This uses the previously generated csv files, which are in a sub directory titled "CSV's", from generate_csv.py and interacts with the E-AIM API to pass in each csv, and store the resulting output.

