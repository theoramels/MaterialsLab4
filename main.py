from cProfile import label
import os
import glob
from turtle import color
from black import diff
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, medfilt, filtfilt


def Derivitive(samplingPeriod):
    df['DerivitiveForce'] = np.NaN
    del df['DerivitiveForce']
    df['DrivitiveForce'] = np.NaN
    for i in range(samplingPeriod, len(df), samplingPeriod):
        df.loc[(i - (samplingPeriod/2)), 'DerivitiveForce'] = (df[Force_N].iloc[i - samplingPeriod]
                                                               - df[Force_N].iloc[i]) / (df[Time_s].iloc[i - samplingPeriod]
                                                                                         - df[Time_s].iloc[i])


def IdentifyCriticalPoints():
    # Locating the Start of Data
    samplingPeriod = 4  # must be even number
    Derivitive(samplingPeriod)
    DataBeginCuttoff = 10  # lower limit for derivite value
    CertantyFactor = 10
    for i in range(0, len(df)):
        BeginData_Index = df[(df['DerivitiveForce'] > DataBeginCuttoff) & 
                              df['DerivitiveForce'].notnull()].index[i]  # for the first index where the derivitive is above 0
        IsTrue = 0
        for j in range(0, CertantyFactor):# Check the next Certanty Factor # of derivitives to see if BeginData_Index is the first datapoint
            IndexedVal = df['DerivitiveForce'].loc[BeginData_Index +
                                                   j*samplingPeriod]
            if IndexedVal > DataBeginCuttoff:
                IsTrue = IsTrue + 1
            else:
                break
        if IsTrue >= CertantyFactor:
            break
    # Extensiometer Removal Data
    for i in range(0, len(df)):
        BeginExtCuttoff_Index = df[(df['DerivitiveForce'] < DataBeginCuttoff) &
                                   (df['DerivitiveForce'].notnull()) &
                                   (df['DerivitiveForce'].index > BeginData_Index)].index[i]  # for the first index where the derivitive is above 0
        IsTrue = 0
        # Check the next Certanty Factor # of derivitives to see if BeginData_Index is the first datapoint
        for j in range(0, CertantyFactor):
            IndexedVal = df['DerivitiveForce'].loc[BeginExtCuttoff_Index + j*samplingPeriod]
            if IndexedVal < DataBeginCuttoff:
                IsTrue = IsTrue + 1
            else:
                break
        if IsTrue >= CertantyFactor:
            break
    
    for i in range(0, len(df)):
        EndExtCuttoff_Index = df[(df['DerivitiveForce'] > DataBeginCuttoff) &
                                   (df['DerivitiveForce'].notnull()) &
                                   (df['DerivitiveForce'].index > BeginExtCuttoff_Index)].index[i]  # for the first index where the derivitive is above 0
        IsTrue = 0
        # Check the next Certanty Factor # of derivitives to see if BeginData_Index is the first datapoint
        for j in range(0, CertantyFactor):
            IndexedVal = df['DerivitiveForce'].loc[EndExtCuttoff_Index + j*samplingPeriod]
            if IndexedVal > DataBeginCuttoff:
                IsTrue = IsTrue + 1
            else:
                break
        if IsTrue >= CertantyFactor:
            break

    BeginExtCuttoff_Index = BeginExtCuttoff_Index - samplingPeriod
    EndExtCuttoff_Index = EndExtCuttoff_Index + samplingPeriod

    #Remove Null Data

    # Fracture Point

# Ultimate Tensile Stress
    UltTensStr_Index = df[Stress_Mpa].idxmax()
    print('Ultimeate Tensile Strength is: ',UltTensStr_Index)
# Yeild Strength
    Derivitive(2)
    YeildStr_Index = df['DerivitiveForce'][(df['DerivitiveForce'].index > BeginData_Index) &
                                   (df['DerivitiveForce'].notnull()) &
                                   (df['DerivitiveForce'].index < BeginExtCuttoff_Index)].idxmax() + samplingPeriod
    print('Yeild Strength is:', YeildStr_Index)
# Modulus
    ModulusElastic = None


    return  DataBeginCuttoff, BeginData_Index, BeginExtCuttoff_Index, EndExtCuttoff_Index, YeildStr_Index, UltTensStr_Index


def RemoveNullData():
    None
    
    #df.drop(df.index[np.r_[0 : BeginData_Index , BeginExtCuttoff_Index : EndExtCuttoff_Index]], inplace=True)
    

    # Fracture Point Data To end of Data set

    
  
DataDict = {}
# De comment which material to process
Mat_For_Analysis = '260Brass' 
#Mat_For_Analysis = '1018Steel'
#Mat_For_Analysis = '4130Steel'
#Mat_For_Analysis = '6061Aluminium'

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

    # Setting Up Material Properties Dictionary
    Propertydict = {}

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

    # exponential smoothing
    spanval = 10
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

    DataDict[f_name] = df # Storing the Data For Plotting




#Charts 
plt.figure(1) # plots of heat treatment in different mycolor and each test with different alpha
plt.figure(0, figsize=(8.5, 4))
myColorPalette = ['black', 'blue', 'green', 'orange', 'red']
myAlphaPalette = [1, 0.55, 0.4]
legendFigure1 = []
i = 0 
for key in DataDict: 
    
    i = i +1
    if i == 3:
        i = 0
    
    df = DataDict[key]
    print(key)
    DataBeginCuttoff, BeginData_Index, BeginExtCuttoff_Index, EndExtCuttoff_Index, YeildStr_Index, UltTensStr_Index = IdentifyCriticalPoints()
    RemoveNullData()
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
    plt.plot(df[Strain_mmPermm], df[Stress_Mpa],  
    color = mycolor, alpha = myalpha, label = (HeatTreatment if i==1 else '_'))
    plt.xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    plt.ylabel('Stress (Mpa)')
    plt.title('Stress Strain Curves for ' + material)
    


    plt.figure(fignum, figsize=(4.25, 3.66))
    plt.plot(df[Strain_mmPermm], df[Stress_Mpa],  
    color = mycolor, alpha = myalpha, label = TestNum)
    plt.plot(df[Strain_mmPermm].iloc[int(UltTensStr_Index)], df[Stress_Mpa].iloc[int(UltTensStr_Index)], 'x', color = 'red')
    plt.plot(df[Strain_mmPermm].iloc[YeildStr_Index], df[Stress_Mpa].iloc[YeildStr_Index], 'o', color = 'orange')
    plt.plot([df[Strain_mmPermm].iloc[BeginData_Index], df[Strain_mmPermm].iloc[YeildStr_Index]], [df[Stress_Mpa].iloc[BeginData_Index], df[Stress_Mpa].iloc[YeildStr_Index]], marker ='x', color = 'purple')
    plt.xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    plt.ylabel('Stress (Mpa)')
    plt.title('Stress Strain Curves for ' + material + ' ' + HeatTreatment)

for fignum in range(0,6):
    plt.figure(fignum, figsize=(4.25, 3.66))
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


