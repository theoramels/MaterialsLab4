from ast import For
from cProfile import label
import os
import glob
from turtle import color
from black import diff
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, medfilt, filtfilt


DataDict = {}
# De comment which material to process
Mat_For_Analysis = '260Brass' 
#Mat_For_Analysis = '1018Steel'
#Mat_For_Analysis = '4130Steel'
#Mat_For_Analysis = '6061Aluminum'

ExcelFileLoc = Mat_For_Analysis + 'Data' + '\\' + Mat_For_Analysis + 'Measurements' + '.xlsx'
#ExcelFileLoc = '260BrassData\\260BrassMeasurements.xlsx'
dfExcel = pd.read_excel(ExcelFileLoc)
#print(dfExcel)

# Getting the path for the folder containing the files
FolderName = Mat_For_Analysis + 'Data'
file_location = os.path.join(FolderName, '*.lvm')
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

    # filtering data for nicer plots
    
    
    #exponential smoothing
    spanval = 6
    df[Force_N] = df[Force_N].ewm(span=spanval, adjust=False).mean()
    df[Globe_Disp_1_mm] = df[Globe_Disp_1_mm].ewm(span=spanval, adjust=False).mean()

    
   

    # Calculation of stress and strain for the current path in question
    CSArea = width * thickness
    #Stress
    df['Stress_Mpa'] = df[Force_N].abs() / CSArea
    Stress_Mpa = 'Stress_Mpa' 
    #Strain
    df['Strain_mm/mm'] = df[Globe_Disp_1_mm].abs() / length
    Strain_mmPermm = 'Strain_mm/mm'
    #True Stress
    #True Strain


    # Triming and Aligning The Data 
    
    #locate the modulus of elasticiy by finding the segment where the second derivitive is 0
    # draw a line where the slope is greater than X then take the second derivitive and if 
   

    # df.drop(df[(df[Stress_Mpa].diff() < 1) & 
    # (df[Stress_Mpa].index < 400)].index, inplace= True)
    # & (df[Strain_mmPermm].index > 100)
    #df[Strain_mmPermm] = df[Strain_mmPermm].subtract(df[Strain_mmPermm].iloc[0]) # calibrate data to start strain at 0
    
    #df[Force_N] = df[Force_N].subtract(df[Force_N].iloc[0]) # calibrate stress data to start stress at 0
    #df.drop(df[(df[Force_N].diff() < 10) & (df[Force_N].index < 100)].index, inplace= True) # trim data with less than 3 N
    
    DataDict[f_name] = df

#Charts 
plt.figure(1) # plots of heat treatment in different mycolor and each test with different alpha
myColorPalette = ['black', 'blue', 'green', 'orange', 'red']
myAlphaPalette = [1, 0.55, 0.4]
legendFigure1 = []
i = 0 
for key in DataDict: 
    
    i = i +1
    if i == 3:
        i = 0
    
    dfplot = DataDict[key]
    material, HeatTreatment, TestNum = key.split('_')
    
    if 'T1' in TestNum:
        myalpha = myAlphaPalette[0]
    elif 'T2' in TestNum:
        myalpha = myAlphaPalette[1]
    elif 'T3' in TestNum:
        myalpha = myAlphaPalette[2]
    
    if 'AR' in HeatTreatment:
        mycolor = myColorPalette[0]
        fignum = 1
    elif 'HT1' in HeatTreatment:
        mycolor = myColorPalette[1]
        fignum = 2
    elif 'HT2' in HeatTreatment:
        mycolor = myColorPalette[2]
        fignum = 3
    elif 'HT3' in HeatTreatment:
        mycolor = myColorPalette[3]
        fignum = 4
    elif 'HT4' in HeatTreatment:
        mycolor = myColorPalette[4]
        fignum = 5
    
    plt.figure(0)
    plt.plot(dfplot[Strain_mmPermm], dfplot[Stress_Mpa],  
    color = mycolor, alpha = myalpha, label = (HeatTreatment if i==1 else '_'))
    plt.xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    plt.ylabel('Stress (Mpa)')
    plt.title('Stress Strain Curves for ' + material)
    
    plt.figure(fignum)
    plt.plot(dfplot[Strain_mmPermm], dfplot[Stress_Mpa],  
    color = mycolor, alpha = myalpha, label = TestNum)
    plt.xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    plt.ylabel('Stress (Mpa)')
    plt.title('Stress Strain Curves for ' + material + ' ' + HeatTreatment)

for fignum in range(0,6):
    plt.figure(fignum)
    leg = plt.legend() 
    j = 0
    for text in leg.get_texts():
        if fignum == 0:
            text.set_color(myColorPalette[j])
        else:
            text.set_alpha(myAlphaPalette[j])
            text.set_color(myColorPalette[fignum-1])
        j=j+1
    
    

plt.show()

