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
    print(EndExtCuttoff_Index)
    # Fracture Point

    # Ultimate Tensile Stress

    UltTensStr_Index = df[Strain_mmPermm].loc[df[Stress_Mpa].idxmax()]

    # Yeild Strength

    YeildStr_Index = df[(df['DerivitiveForce'].index > BeginData_Index) &
                                   (df['DerivitiveForce'].notnull()) &
                                   (df['DerivitiveForce'].index < BeginExtCuttoff_Index)].idxmax()

    # Modulus
    return  DataBeginCuttoff, BeginData_Index, BeginExtCuttoff_Index, EndExtCuttoff_Index, YeildStr_Index, UltTensStr_Index


def RemoveNullData():
    None
    
    df.drop(df.index[np.r_[0 : BeginData_Index , BeginExtCuttoff_Index : EndExtCuttoff_Index]], inplace=True)
    

    # Fracture Point Data To end of Data set


dfExcel = pd.read_excel('260BrassData\\260BrassMeasurements.xlsx')
# print(dfExcel)
DataDict = {}
file = '260BrassData\\260Brass_HT4_T1.lvm'
with open(file, 'rt') as myfile:  # Open
    ind = 0
    for myline in myfile:  # read line by line
        ind += 1
        if '***End_of_Header***' in myline:  # Determine where the end of then header is
            rowsToSkip = ind + 1
    # convert lvm to pandas dataframe (good for some analysis)
    df = pd.read_csv(file, sep='\t', skiprows=rowsToSkip, header=None)

    colNames = ['Time_s', 'Ext_Disp_mm', 'Force_N',
                'Globe_Disp_1_mm', 'Globe_Disp_2_mm']
    Time_s, Ext_Disp_mm, Force_N, Globe_Disp_1_mm, Globe_Disp_2_mm = colNames
    df.columns = colNames

    # Setting Up Material Properties Dictionary
    Propertydict = {}

    # Getting More information from the File Name
    fileid = os.path.basename(myfile.name)
    f_name = fileid.replace('.lvm', '')
    material, HeatTreatment, TestNum = f_name.split('_')
    # print('mat: ' ,material, 'HeatT: ', HeatTreatment, 'Test#: ', TestNum)

    # find the row in Excel DF where Heat treatment and test match
    GeometryData = dfExcel[(dfExcel['HT'] == HeatTreatment)
                           & (dfExcel['Test_Num'] == TestNum)]
    #length, width, thickness = GeometryData['Length_mm', 'Width_mm', 'Thickness_mm']
    length = GeometryData.iloc[0]['Length_mm']
    width = GeometryData.iloc[0]['Width_mm']
    thickness = GeometryData.iloc[0]['Thickness_mm']

    # exponential smoothing
    spanval = 6
    df[Force_N] = df[Force_N].ewm(span=spanval, adjust=False).mean()
    df[Globe_Disp_1_mm] = df[Globe_Disp_1_mm].ewm(
        span=spanval, adjust=False).mean()

    # Calculation of stress and strain for the current path in question
    CSArea = width * thickness
    # Stress
    df['Stress_Mpa'] = df[Force_N].abs() / CSArea
    Stress_Mpa = 'Stress_Mpa'
    # Strain
    df['Strain_mm/mm'] = df[Globe_Disp_1_mm].abs() / length
    Strain_mmPermm = 'Strain_mm/mm'

    DataBeginCuttoff, BeginData_Index, BeginExtCuttoff_Index, EndExtCuttoff_Index, YeildStr_Index, UltTensStr_Index = IdentifyCriticalPoints()
    RemoveNullData()

    colors = []
    for item in df['DerivitiveForce']:
        if item > DataBeginCuttoff:
            colors.append('green')
        else:
            colors.append('red')

    plt.figure(9)
    ax1 = plt.subplot()
    ax1.plot(df[Strain_mmPermm], df['DerivitiveForce'], '.')
    ax1.vlines(x=df[Strain_mmPermm], ymin=-1100,
               ymax=df['DerivitiveForce'], color=colors)
    ax2 = ax1.twinx()
    ax2.plot(df[Strain_mmPermm], df[Force_N])

    plt.show()
