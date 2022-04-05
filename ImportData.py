import os
import glob
from black import diff
import numpy as np
import pandas as pd

DataDict = {}
ExcelDF = pd.read_excel('260 Brass Data\Copy of Lab 4 Data.xlsx')
print(ExcelDF)
# Getting the path for the folder containing the files
file_location = os.path.join('260 Brass Data', '*.lvm')
filenames = glob.glob(file_location) # Creating a directory ID

for file in filenames: # for each file in the folder
    with open(file, 'rt') as myfile: #Open
        ind = 0
        print('The name of file is',file)
        print('myfile is ',myfile)
        for myline in myfile: # read line by line
            ind += 1
            if '***End_of_Header***' in myline: # Determine where the end of then header is
                rowsToSkip = ind + 1
    # convert lvm to pandas dataframe (good for some analysis) 
    df = pd.read_csv(file, sep = '\t', skiprows = rowsToSkip, header = None)
    
    colNames = ['Time_s', 'Ext_Disp_mm', 'Force_N', 'Globe_Disp_1_mm', 'Globe_Disp_2_mm']
    df.columns = colNames

    # Examples 
        #dataframes I found to be useful for storing and doing simple algegra on
    TimeCol = df['Time_s'] # get the values for "column" labeled time in the dataframe "df"
    df['NEW_DATAFRAME'] = df['Time_s'].add(5) # adds a col named NEW_DATAFRAME w/ values of Time_s + 5
    DeltaForce = df['Force_N'].diff() #basically the change in force between the current and previous data points

        # Numpy arrays are great for a more matlab esk experience
    Timearray = df['Time_s'].to_numpy() # converts Dataframe to numpy array. (** = ^)
    df['Time_s'] = Timearray.tolist() # if stuff were done to the numpy array this would replace the previous col with the new values 

    
    #Unit Conversion
    #Stress
    #Strain
    #True Stress
    #True Strain


    print(df)

    name = file.replace('.lvm','')
    DataDict[name] = df

for key in DataDict:
    df = DataDict[key]
    DataArray = df.to_numpy()

#Charts 

#15 total 
#Stress Strain Curves
    #Per Material Each heat treatment has different color and alpha for each test
    #