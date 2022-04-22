from cProfile import label
import os
import glob
from turtle import color
from black import diff
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, medfilt, filtfilt

# ---------------------Setup-----------------------
# A visualization of the derivitive is avalible in the the DerivitiveVisualization.py Module 
# Files must have a specific nomeculture, a tree example is shown below, names are in quotes
#   folder: '#MatData'
#       lvm datafile: '#Mat_HTx_Tx.lvm'
#       excel data file: '#MatMeasurements.xlsx' 
# See Acompannying Datafiles and folders for exact examples


    # De comment which material to process
Mat_For_Analysis = '260Brass'
#Mat_For_Analysis = '1018Steel'
#Mat_For_Analysis = '4130Steel'
#Mat_For_Analysis = '6061Aluminium'
DataBeginCuttoff = 10  # If 4130 Steel Change to 60
# -------------------------------------------------

def Derivitive(samplingPeriod): #Finding the Derivitive of Force Vs Time
    df['DerivitiveForce'] = np.NaN
    del df['DerivitiveForce']
    df['DrivitiveForce'] = np.NaN
    for i in range(samplingPeriod, len(df), samplingPeriod):
        df.loc[(i - (samplingPeriod/2)), 'DerivitiveForce'] = (df[Force_N].iloc[i - samplingPeriod]
                                                               - df[Force_N].iloc[i]) / (df[Time_s].iloc[i - samplingPeriod]
                                                                                         - df[Time_s].iloc[i])

def IdentifyCriticalPoints(): # Locating the index's of Critical Points
    # Locating the Start of Data
    samplingPeriod = 4  # must be even number
    Derivitive(samplingPeriod)

    CertantyFactor = 8
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
    print('Beginning of Data is:',BeginData_Index)
    # Extensiometer Removal NULL Data range

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
    print('Beginning of Ext Removal range is:', BeginExtCuttoff_Index)
    
    BeginExtCuttoff_Index = BeginExtCuttoff_Index - samplingPeriod
    EndExtCuttoff_Index = BeginExtCuttoff_Index + samplingPeriod

# Find Index of Ultimate Tensile Stress
    UltTensStr_Index = df[Stress_Mpa].idxmax()
    print('Ultimeate Tensile Strength is: ',UltTensStr_Index)

# Find Index of Yeild Strength
    YeildStr_Index = df['DerivitiveForce'][(df['DerivitiveForce'].index > BeginData_Index) &
                                   (df['DerivitiveForce'].notnull()) &
                                   (df['DerivitiveForce'].index < BeginExtCuttoff_Index)].idxmax() + samplingPeriod
#-----------------------Uncomment if there is a change in trend before the expected Yeild Stress Index ------------------------------------
    # YeildStr_Index = df['DerivitiveForce'][(df['DerivitiveForce'].index > YeildStr_Index) &
    #                                (df['DerivitiveForce'].notnull()) &
    #                                (df['DerivitiveForce'].index < BeginExtCuttoff_Index)].idxmax() + samplingPeriod
#------------------------------------------------------------------------------------------------------------------------------------------
    print('Yeild Strength is:', YeildStr_Index)
# Modulus
    ModulusElastic_GlobDisp = ((df[Stress_Mpa].iloc[BeginData_Index] - 
                                df[Stress_Mpa].iloc[YeildStr_Index]) /
                               (df[Strain_mmPermm].iloc[BeginData_Index] - 
                                df[Strain_mmPermm].iloc[YeildStr_Index]))
    print('Modulus due to Global Displacement',ModulusElastic_GlobDisp)
    ModulusElastic_EXT = ((df[Stress_Mpa].iloc[BeginData_Index] - 
                                df[Stress_Mpa].iloc[YeildStr_Index]) /
                               (df[EXT_Strain_mmPermm].iloc[BeginData_Index] - 
                                df[EXT_Strain_mmPermm].iloc[YeildStr_Index]))
    print('Modulus due to Extensiometer',ModulusElastic_EXT)
    return DataBeginCuttoff, BeginData_Index, BeginExtCuttoff_Index, YeildStr_Index, UltTensStr_Index, ModulusElastic_EXT, ModulusElastic_GlobDisp

    
# Importing and Smoothing Data  
DataDict = {}

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
    spanval = 6
    df[Force_N] = df[Force_N].ewm(span=spanval, adjust=False).mean()
    df[Globe_Disp_1_mm] = df[Globe_Disp_1_mm].ewm(
        span=spanval, adjust=False).mean()
    df[Ext_Disp_mm] =  df[Ext_Disp_mm].ewm(span=spanval, adjust=False).mean()

   
    # Calculation of stress and strain for the current lvm
    CSArea = width * thickness
    # Stress
    df['Stress_Mpa'] = df[Force_N].abs() / CSArea
    Stress_Mpa = 'Stress_Mpa'
    # Strain
    df['Strain_mm/mm'] = df[Globe_Disp_1_mm].abs() / length
    Strain_mmPermm = 'Strain_mm/mm'
    df['EXT_Strain_mm/mm'] = df[Ext_Disp_mm].abs() / length
    EXT_Strain_mmPermm = 'EXT_Strain_mm/mm'

    DataDict[f_name] = df # Storing the Data For Plotting




#Charts 
# plots of heat treatment in different mycolor and each test with different alpha
plt.figure(0, figsize=(8.5, 4))

myColorPalette = ['black', 'blue', 'green', 'orange', 'red']
myAlphaPalette = [1, 0.55, 0.4]
legendFigure1 = []
i = 0 
Matcolnames = ['Heat Treatment',
               'Test Number',
               'Yeild Strength',
               'Ultimate Tensile',
               'Ext Modululs',
               'Glob Modulus']
MatProps = pd.DataFrame(columns = Matcolnames)
for key in DataDict: # Plotting All Plots: iterates through each dataframe containing Manipulated data and plots it on inteded Graph
    
    i = i +1
    if i == 3:
        i = 0
    
    df = DataDict[key] # Extracting dataframe with LVM data and Stress and Strain
    print(key)
    DataBeginCuttoff, BeginData_Index, BeginExtCuttoff_Index, YeildStr_Index, UltTensStr_Index, ModulusElastic_EXT, ModulusElastic_GlobDisp = IdentifyCriticalPoints()
    
    material, HeatTreatment, TestNum = key.split('_')
    print('Mat props during',i , 'is',MatProps)

    # Storing Material Property data to a dataframe to be exported to CSV / XLS
    MatProps.loc[len(MatProps.index)] = [HeatTreatment,
                                         TestNum,
                                         df[Stress_Mpa].iloc[YeildStr_Index],
                                         df[Stress_Mpa].iloc[UltTensStr_Index],
                                         ModulusElastic_EXT,
                                         ModulusElastic_GlobDisp]
     
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
    
    plt.figure(0,figsize = (8.5, 4))# All Stress Strain Curves
    plt.plot(df[Strain_mmPermm], df[Stress_Mpa],  
    color = mycolor, alpha = myalpha, label = (HeatTreatment if i==1 else '_'))
    plt.xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    plt.ylabel('Stress (Mpa)')
    plt.title('Stress Strain Curves for ' + material)
    
    plt.figure(6, figsize = (8.5, 4))# ExtStress Strain Curve
    plt.plot(df[EXT_Strain_mmPermm].iloc[BeginData_Index: BeginExtCuttoff_Index],
             df[Stress_Mpa].iloc[BeginData_Index: BeginExtCuttoff_Index],
             color = mycolor, alpha = myalpha, label = (HeatTreatment if i==1 else '_'))
#------------------------Un Comment to plot modulus lines on exstensometer Stress Streain Curve----------------------------
    # plt.plot([df[EXT_Strain_mmPermm].iloc[BeginData_Index], df[EXT_Strain_mmPermm].iloc[YeildStr_Index]],
    #         [df[Stress_Mpa].iloc[BeginData_Index], df[Stress_Mpa].iloc[YeildStr_Index]],
    #         marker ='x', color = 'purple', label = ('Modulus of Elasticity' if i==0 else '_'))
#--------------------------------------------------------------------------------------------------------------------------
    plt.xlim(0,0.005)
    plt.ylim(0, 300)
    plt.xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    plt.ylabel('Stress (Mpa)')
    plt.title('Extensometer Stress Strain Curves for ' + material)


    plt.figure(fignum, figsize = (8.5, 4)) # Indiviual Heat Treatment Stress Strain Curves
    plt.plot(df[Strain_mmPermm], df[Stress_Mpa],  
            color = mycolor, alpha = myalpha, label = TestNum)
    plt.plot(df[Strain_mmPermm].iloc[int(UltTensStr_Index)],
            df[Stress_Mpa].iloc[int(UltTensStr_Index)],
            'x', color = 'plum', label = ('Ult Tensile' if i==0 else '_')) #
    plt.plot(df[Strain_mmPermm].iloc[YeildStr_Index],
            df[Stress_Mpa].iloc[YeildStr_Index],
            '.', color = 'purple', label = ('Yeild Strength' if i==0 else '_')) #
    plt.plot([df[Strain_mmPermm].iloc[BeginData_Index], df[Strain_mmPermm].iloc[YeildStr_Index]],
            [df[Stress_Mpa].iloc[BeginData_Index], df[Stress_Mpa].iloc[YeildStr_Index]],
            marker ='x', color = 'purple', label = ('Modulus of Elasticity' if i==0 else '_'))#
    plt.grid(True)
    plt.title('Stress Strain Curves for ' + material + ' ' + HeatTreatment)
    plt.xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    plt.ylabel('Stress (Mpa)')
    plt.title('Stress Strain Curves for ' + material + ' ' + HeatTreatment)



for fignum in range(0,6): # Applying Colors to Legends
    plt.figure(fignum)
    leg = plt.legend() 
    j = 0
    for text in leg.get_texts():
        if fignum == 0:
            text.set_color(myColorPalette[j])
        elif j <= 2:
            text.set_alpha(myAlphaPalette[j])
            text.set_color(myColorPalette[fignum-1])
        j=j+1

print(MatProps) 

# Saving Plots and Material Property Data, aswell as displaying plots on interactive Figures
fileName = 'MaterialProperties' + '\\' + f_name +'_MatProps'+'.csv'
MatProps.to_csv(fileName)
for i in range(0,7):
    plt.figure(i)
    fileName = 'MaterialProperties' + '\\' + Mat_For_Analysis +'_MatProps'+ str(i) +'.png'
    plt.savefig(fileName, bbox_inches='tight')
plt.show()


