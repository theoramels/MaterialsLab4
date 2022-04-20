
from cProfile import label
import os
import glob
from turtle import color
from black import diff
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, medfilt, filtfilt


def Remove_extrainious_data():
    #Removing Data
    samplingPeriod = 10 #indexes between samples
    sampleRange = 5 #range of data to be averaged per sample
    totIndicies = len(df)
    indexRange = int(sampleRange/2)
    sampleIndicies = np.arange(indexRange, totIndicies, samplingPeriod, dtype = int)

    df['DerivitiveForce'] = np.nan
    df['AveragedSamples'] = np.nan
    for Index in sampleIndicies:
        df.loc[Index, 'AveragedSamples'] = df[Force_N].iloc[Index - indexRange: Index + indexRange].mean()
        df.loc[Index - sampleRange, 'DerivitiveForce'] = (df['AveragedSamples'].iloc[Index - samplingPeriod]
        - df['AveragedSamples'].iloc[Index]) / (df[Time_s].iloc[Index - samplingPeriod]
        - df[Time_s].iloc[Index])

    # locate index at start of elastic region
    
    strtCondition = 15
    indexStartLER = 0
    indexEndLER = 0
    indexEndNullPeriod = 0
    for ind in df.index:
        indexStartLER = df[(df['DerivitiveForce'] < strtCondition) &
                       (df.index > indexStartLER) &
                        df['DerivitiveForce'].notnull()].index[0]
        if strtCondition > df['DerivitiveForce'].iloc[indexStartLER + samplingPeriod]:
            None
        elif strtCondition > df['DerivitiveForce'].iloc[indexStartLER + samplingPeriod*2]:
            None
        else:
            break

    df.drop(df.index[0 : indexStartLER], inplace= True)
    
    df.reset_index(inplace = True)

    indexEndLER = df[(df['DerivitiveForce'] < strtCondition) &
    (df.index > indexStartLER)].index[0] -5

    indexEndNullPeriod = df[(df['DerivitiveForce'] > strtCondition) &
    (df.index > indexEndLER) &
    df['DerivitiveForce'].notnull()].index[0] + 5

    indexEndLER = df.loc[50:indexEndNullPeriod, 'DerivitiveForce'].idxmax() 
    
    df.drop(df.index[indexEndLER : indexEndNullPeriod], inplace= True)
    return [indexEndLER] 

MatPropertiesDict = {}
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
    
    # Calculation of stress and strain for the current path in question
    CSArea = width * thickness
    #Stress
    df['Stress_Mpa'] = df[Force_N].abs() / CSArea
    Stress_Mpa = 'Stress_Mpa' 
    #Strain
    df['Strain_mm/mm'] = df[Globe_Disp_1_mm].abs() / length
    Strain_mmPermm = 'Strain_mm/mm'
    # exponential smoothing
    spanval = 6
    df[Force_N] = df[Force_N].ewm(span=spanval, adjust=False).mean()
    df[Globe_Disp_1_mm] = df[Globe_Disp_1_mm].ewm(span=spanval, adjust=False).mean()
    
    if df[Force_N].iloc[0] < 1:
        ELeRegion = Remove_extrainious_data()
        
        StrainIndex_FP = 10
        StrainIndex_LP = ELeRegion[0] - 10

        GlobDisp_Modulus = ((df[Stress_Mpa].loc[StrainIndex_LP] - df[Stress_Mpa].loc[StrainIndex_FP]) /
                            (df[Strain_mmPermm].loc[StrainIndex_LP] - df[Strain_mmPermm].loc[StrainIndex_FP]))
        Propertydict['GlobDisp_Modulus']= [GlobDisp_Modulus,
                                            [df[Strain_mmPermm].loc[StrainIndex_LP], df[Strain_mmPermm].loc[StrainIndex_FP]], 
                                            [df[Stress_Mpa].loc[StrainIndex_LP], df[Stress_Mpa].loc[StrainIndex_FP]]] 
       
        df['Ext_Strain_mm/mm'] = df[Ext_Disp_mm].abs() / length
        df.loc[StrainIndex_LP: , 'Ext_Strain_mm/mm'] = np.nan
        df.loc[ :StrainIndex_FP, 'Ext_Strain_mm/mm'] = np.nan
    else:
        Propertydict['GlobDisp_Modulus']= [np.nan,
                                            [np.nan, np.nan], 
                                            [np.nan, np.nan]] 
        # plt.plot(df['Ext_Strain_mm/mm'], df[Stress_Mpa])
        # plt.show()
        
    
    #Calculate elastic modulus for each material using extenometer data
  
    #Determine yeild strength and ultimate tensile strength
    Propertydict['YeildStrength'] = [df[Stress_Mpa].loc[ELeRegion[0] - 1], [df[Strain_mmPermm].loc[ELeRegion[0] - 1]]] 
    Propertydict['UltTensileStrength'] = [df[Stress_Mpa].max(), df[Strain_mmPermm].loc[df[Stress_Mpa].idxmax()]]

    #Vickers hardness values? 
    print(HeatTreatment, 'Yeild Strength is ', Propertydict['YeildStrength'][0])
    print(HeatTreatment, 'Ult Tensile Strength is ', Propertydict['UltTensileStrength'][0])
    print(HeatTreatment, 'Global modulus is ', Propertydict['GlobDisp_Modulus'][0])

    MatPropertiesDict[f_name] = Propertydict
    fileName = 'ExportCsv' + '\\' + f_name +'.csv'
    df.to_csv(fileName)
    DataDict[f_name] = df

#Charts 
fig, axis = plt.subplots(nrows = 3, ncols = 2, figsize = (8.5 , 11))

myColorPalette = ['black', 'blue', 'green', 'orange', 'red']
myAlphaPalette = [1, 0.55, 0.4]
legendFigure1 = []



i = 0 
for key in DataDict: 

    i = i +1
    if i == 3:
        i = 0
    Propertydict = MatPropertiesDict[key]
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
        fignum = [0,1]
    elif 'HT1' in HeatTreatment:
        mycolor = myColorPalette[1]
        fignum = [1,0]

    elif 'HT2' in HeatTreatment:
        mycolor = myColorPalette[2]
        fignum = [1,1]
    elif 'HT3' in HeatTreatment:
        mycolor = myColorPalette[3]
        fignum = [2,0]
    elif 'HT4' in HeatTreatment:
        mycolor = myColorPalette[4]
        fignum = [2,1]
    
    axis[0,0].plot(dfplot[Strain_mmPermm], dfplot[Stress_Mpa],  
    color = mycolor, alpha = myalpha, label = (HeatTreatment if i==1 else '_'))
    axis[0,0].set_xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    axis[0,0].set_ylabel('Stress (Mpa)')
    axis[0,0].set_title('All Heat Treatments and Tests')

    axis[fignum[0], fignum[1]].plot(dfplot[Strain_mmPermm], dfplot[Stress_Mpa],  
    color = mycolor, alpha = myalpha, label = TestNum)
    
    axis[fignum[0], fignum[1]].plot(Propertydict['YeildStrength'][1], Propertydict['YeildStrength'][0],  
    color = mycolor, alpha = myalpha, marker = 'x' )

    axis[fignum[0], fignum[1]].plot(Propertydict['UltTensileStrength'][1], Propertydict['UltTensileStrength'][0],  
    color = mycolor, alpha = myalpha, marker = 'o' )

    axis[fignum[0], fignum[1]].plot(Propertydict['GlobDisp_Modulus'][1], Propertydict['GlobDisp_Modulus'][2],  
    color = 'purple', alpha = myalpha)
    
    axis[fignum[0], fignum[1]].set_xlabel('Strain '+ r'($\frac{mm}{mm}$)' )
    axis[fignum[0], fignum[1]].set_ylabel('Stress (Mpa)')
    axis[fignum[0], fignum[1]].set_title(HeatTreatment)

    
plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)
fig.suptitle('Stress Strain Curves for ' + material)

lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
fig.legend(lines, labels)
# for item in axis:

#     leg = item[0].legend() 
#     j = 0
#     for text in leg.get_texts():
#         if fignum == 0:
#             text.set_color(myColorPalette[j])
#         else:
#             text.set_alpha(myAlphaPalette[j])
#             text.set_color(myColorPalette[fignum-1])
#         j=j+1
plt.show()


