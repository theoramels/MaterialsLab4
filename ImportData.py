import os
import glob
from black import diff
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


DataDict = {}
Mat_For_Analysis = '260Brass' #idea for later implementation
dfExcel = pd.read_excel('260BrassData\\260BrassMeasurements.xlsx')
print(dfExcel)

# Getting the path for the folder containing the files

file_location = os.path.join('260BrassData', '260Brass_HT3_T1.lvm')
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
    Time_s, Ext_Disp_mm, Force_N, Globe_Disp_1_mm, Globe_Disp_2_mm = colNames
    df.columns = colNames

    # Getting More information from the File Name
    fileid = os.path.basename(myfile.name)
    f_name = fileid.replace('.lvm','')
    material, HeatTreatment, TestNum = f_name.split('_')
    #print('mat: ' ,material, 'HeatT: ', HeatTreatment, 'Test#: ', TestNum)

    #find the row in Excel DF where Heat treatment and test match
    GeometryData = dfExcel[(dfExcel['HT'] == HeatTreatment) & (dfExcel['Test_Num'] == TestNum)]
    #length, width, thickness = GeometryData['Length_mm', 'Width_mm', 'Thickness_mm']
    length = GeometryData.iloc[0]['Length_mm']
    width = GeometryData.iloc[0]['Width_mm']
    thickness = GeometryData.iloc[0]['Thickness_mm']
    # print(length)
    # print(width)
    # print(thickness)

    #Trim The Data 
        # Usable Data throughout data set has force above 3 N & where the following force decreases by atmost 2
    #df = df.loc[df[Force_N] > 4] #Delete Rows where Force_N is less than 3
    df.drop(df[df[Force_N] < 6].index, inplace= True)


    #filter maybe?
    #df.diff().iloc
    print(df[Force_N].diff(periods = 5))
    print(df[df[Force_N].diff(periods = 5) > 0.08].index)

    df.drop(df[df[Force_N].diff(periods = 5) < 0.08].index, inplace= True)
    # dfDiff = df[Force_N].diff()
    # Indices = dfDiff[dfDiff < 0].index
    # df.drop(df.index[Indices - 1], inplace = True)
    #df = dfDiff.loc[dfDiff[Force_N].index < 0]
    


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
for key in DataDict:
    dfChart = DataDict[key]

dfChart = DataDict['260Brass_HT3_T1']
plt.figure(1)
plt.plot(dfChart[Time_s], dfChart[Force_N])
plt.show()
#15 total 
#Stress Strain Curves
    #Per Material Each heat treatment has different color and alpha for each test
    #