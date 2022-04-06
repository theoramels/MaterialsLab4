import os
import glob
from black import diff
import numpy as np
import pandas as pd

DataDict = {}
Mat_For_Analysis = '260Brass' #idea for later implementation
ExcelDF = pd.read_excel('260BrassData\\260BrassMeasurements.xlsx')
print(ExcelDF)

# Getting the path for the folder containing the files

file_location = os.path.join('260BrassData', '*.lvm')
filenames = glob.glob(file_location) # Creating a directory ID

for file in filenames: # for each file in the folder
    with open(file, 'rt') as myfile: #Open
        ind = 0
        for myline in myfile: # read line by line
            ind += 1
            if '***End_of_Header***' in myline: # Determine where the end of then header is
                rowsToSkip = ind + 1
    # convert lvm to pandas dataframe (good for some analysis) 
    df = pd.read_csv(file, sep = '\t', skiprows = rowsToSkip, header = None)
    
    colNames = ['Time_s', 'Ext_Disp_mm', 'Force_N', 'Globe_Disp_1_mm', 'Globe_Disp_2_mm']
    df.columns = colNames

    # Getting More information from the File Name
    fileid = os.path.basename(myfile.name)
    f_name = fileid.replace('.lvm','')
    material, HeatTreatment, TestNum = f_name.split('_')
    #print('mat: ' ,material, 'HeatT: ', HeatTreatment, 'Test#: ', TestNum)

    #find the row in Excel DF where Heat treatment and test match
    GeometryData = ExcelDF[(ExcelDF['HT'] == HeatTreatment) & (ExcelDF['Test_Num'] == TestNum)]
    #length, width, thickness = GeometryData['Length_mm', 'Width_mm', 'Thickness_mm']
    length = GeometryData.iloc[0]['Length_mm']
    width = GeometryData.iloc[0]['Width_mm']
    thickness = GeometryData.iloc[0]['Thickness_mm']
    print(length)
    print(width)
    print(thickness)
    #Unit Conversion
    #Stress
    #Strain
    #True Stress
    #True Strain


    

   
    DataDict[f_name] = df

for key in DataDict:
    df = DataDict[key]
    DataArray = df.to_numpy()

#Charts 

#15 total 
#Stress Strain Curves
    #Per Material Each heat treatment has different color and alpha for each test
    #