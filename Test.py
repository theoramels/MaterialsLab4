from ast import For
from cProfile import label
from operator import index
import os
import glob
from sqlite3 import Time
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
            print (indexStartLER)
            break

    # df.drop(df.index[0 : indexStartLER], inplace= True)
    
    df.reset_index(inplace = True)
    indexEndLER = df[(df['DerivitiveForce'] < strtCondition) &
    (df.index > indexStartLER)].index[0] -5
    print(indexEndLER)

    indexEndNullPeriod = df[(df['DerivitiveForce'] > strtCondition) &
    (df.index > indexEndLER) &
    df['DerivitiveForce'].notnull()].index[0] + 5
    
    print(indexStartLER, indexEndLER, indexEndNullPeriod)

    #df.drop(df.index[indexEndLER : indexEndNullPeriod], inplace= True)
    return indexEndLER


dfExcel = pd.read_excel('260BrassData\\260BrassMeasurements.xlsx')
#print(dfExcel)
DataDict = {}
file = '260BrassData\\260Brass_AR_T1.lvm'
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
    
    df['Ext_Stress_Mpa'] = np.nan
    
    if df[Force_N].iloc[0] < 1:
        Remove_extrainious_data()
        

    # df.drop(df.index[100:220], inplace = True)
    
    
    # indexEndLEZ = df[df['DerivitiveForce'] < 15].index[0]
    # print(indexEndLEZ)
    # dfan = df.drop(df.index[0 : indexEndLEZ], inplace= False)
    # indexStartYS = dfan[dfan['DerivitiveForce'] > 15].index[0]
    # indexStartYS = df[df['DerivitiveForce'] < strtCondition].index[50]
   
    # df.drop(df.index[indexEndLEZ : indexStartYS], inplace= True)
    
    #Calculate elastic modulus for each material using extenometer data
    # TrimmedEXTData =  df.drop(df[df[Ext_Disp_mm] < 0])
    # print(TrimmedEXTData)
    #Determine yeild strength and ultimate tensile strength    
    
    
    # for item in df['DerivitiveForce']:
    #     print(item)

    #df.drop([0 : indexStart])
    
    # for item in df[Time_s]:
    #     print(item)
    # Calculation of stress and strain for the current path in question
    CSArea = width * thickness
    #Stress
    df['Stress_Mpa'] = df[Force_N].abs() / CSArea
    Stress_Mpa = 'Stress_Mpa' 
    #Strain
    df['Strain_mm/mm'] = df[Globe_Disp_1_mm].abs() / length
    Strain_mmPermm = 'Strain_mm/mm'
    
    colors = []
    for item in df['DerivitiveForce']:
        if item > 15:
            colors.append('green')
        else:
            colors.append('red')
    
    plt.figure(9)
    ax1 = plt.subplot()
    ax1.plot(df[Time_s] , df['DerivitiveForce'], '.')
    ax1.vlines(x = df[Time_s], ymin = -1100, ymax = df['DerivitiveForce'], color = colors)
    ax2 = ax1.twinx()
    ax2.plot(df[Time_s], df['AveragedSamples'])
    ax2.plot(df[Time_s], df[Force_N])
    
    
    
    plt.show()
    
