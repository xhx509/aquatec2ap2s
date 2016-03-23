#!/usr/bin/env /anaconda/bin/python
# routine to process Aquatech 530TD data
# where it plots the record and generates output file
#

#import matplotlib.pyplot as plt
#import matplotlib.dates as dates
import os
import time
import serial
from pylab import *
from pandas import *
#from datetime import datetime

fn=event.src_path # where I have deleted the "units" row and fixed date to make it easier
print 'File belongs to: '+fn

try:
    df=read_csv(fn,sep=',',skiprows=34,skip_footer=1,parse_dates={'datet':[1]},header=None,index_col='datet')#creat a new Datetimeindex
    df['yd']=df.index.dayofyear+df.index.hour/24.+df.index.minute/60./24.+df.index.second/60/60./24.-1.0 #creates a yrday0 field
    df['depth']=(df[9]) #get depth
    df=df.ix[(df['depth']>0.90*mean(df['depth']))]  # get rid of shallow data
    for o in list(reversed(range(len(df)))):
        if (df.index[o]-df.index[o-1])>=Timedelta('0 days 00:30:00') or o==0: 
            df=df.ix[o:]
            break
    df['temp']=(df[3])#*1.8)+32.0
    df=df.ix[(df['temp']>mean(df['temp'])-3*std(df['temp'])) & (df['temp']<mean(df['temp'])+3*std(df['temp']))] # reduces time series to deep obs
    print df[['depth','temp']]
    # maxtemp
    maxtemp=str(int(round(max(df['temp'].values),2)*100))
    if len(maxtemp)<4:
        maxtemp='0'+maxtemp
    # mintemp
    mintemp=str(int(round(min(df['temp'].values),2)*100))
    if len(mintemp)<4:
        mintemp='0'+mintemp
    # sdeviatemp
    sdeviatemp=str(int(round(std(df['temp'].values),2)*100))
    for k in range(4):
      if len(sdeviatemp)<4:
        sdeviatemp='0'+sdeviatemp
    # time_len
    time_len=str(int(round((df['yd'][-1]-df['yd'][0]),3)*1000))
    for k in range(3):
        if len(time_len)<3:
            time_len='0'+time_len
    
    # meandepth
    meandepth=str(abs(int(round(mean(df['depth'].values),0))))
    for k in range(3):
        if len(meandepth)<3:
            meandepth='0'+meandepth
    
    # meantemp
    meantemp=str(int(round(mean(df['temp'].values),2)*100))
    if len(meantemp)<4:
        meantemp='0'+meantemp
    
    # rangedepth
    rangedepth=str(abs(int(round(max(df['depth'].values-min(df['depth'].values)),0))))
    for k in range(3):
        if len(rangedepth)<3:
            rangedepth='0'+rangedepth
    
    print 'meandepth: '+meandepth
    print 'rangedepth: '+rangedepth
    print 'time_len: '+time_len
    print 'meantemp: '+meantemp
    print 'sdeviatemp: '+sdeviatemp
    
except:
    print 'Error: Could not get data from the csv file.'
    #raise      

else:
    try:
        print 'Check connection...'
        ser=serial.Serial('COM16', 9600)                #   in Windows
        print 'Open serial port.'
        # send the data
        time.sleep(1)
        ser.writelines('\n')       
        time.sleep(1)
        ser.writelines('\n')
        time.sleep(1)
        ser.writelines('yab'+'\n') # Force the given message to idle.
        time.sleep(60)
        ser.writelines('\n')
        time.sleep(1)
        ser.writelines('\n')
        time.sleep(1)
        ser.writelines('ylbA'+meandepth+rangedepth+time_len+meantemp+sdeviatemp+'\n')
        time.sleep(3)
        print 'Sending data: '+meandepth+rangedepth+time_len+meantemp+sdeviatemp
        #print datetime.now()
        time.sleep(2) # 1100s 18 minutes        
        ser.close() # close port
        print 'Done sent Data.'
    except:
        print 'Error: Could not sent data to satellite.'
        #raise
