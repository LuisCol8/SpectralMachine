#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
*********************************************
*
* MixMakerRruff
* Mix different rruff files into a ASCII
* Files must be in RRuFF
* version: 20171208d
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************
'''
print(__doc__)

import numpy as np
import sys, os.path, getopt, glob, csv, re
from datetime import datetime, date
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 4:
        print(' Usage:\n  python3 MixMakerRruff.py <EnIn> <EnFin> <EnStep> (<threshold %>)\n')
        print(' Requires python 3.x. Not compatible with python 2.x\n')
        return
    else:
        enInit = sys.argv[1]
        enFin =  sys.argv[2]
        enStep = sys.argv[3]
        if len(sys.argv)<5:
            print("No threshold defined, setting to zero\n")
            threshold = 0
        else:
            threshold = sys.argv[4]
            print("Setting threshold to:", threshold,"%\n")

    rootMixFile = "mixture"
    dateTimeStamp = str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    mixFile = rootMixFile+"_"+dateTimeStamp+".txt"
    summaryMixFile = rootMixFile+"-summary_"+dateTimeStamp+".csv"
    plotFile = rootMixFile+"-plot_"+dateTimeStamp
    plt.figure(num=plotFile)

    with open(summaryMixFile, "a") as sum_file:
                    sum_file.write('Classification started: '+dateTimeStamp+\
                    ",enInit="+str(enInit)+",enFin="+str(enFin)+",enStep="+str(enStep)+"\n")
    index = 0
    first = True

    for ind, file in enumerate(sorted(os.listdir("."))):
        try:
            if file[:7] != "mixture" and os.path.splitext(file)[-1] == ".txt":
                with open(file, 'r') as f:
                    En = np.loadtxt(f, unpack = True, usecols=range(0,1), delimiter = ',', skiprows = 10)
                with open(file, 'r') as f:
                    R = np.loadtxt(f, unpack = True, usecols=range(1,2), delimiter = ',', skiprows = 10)
                    
                R[R<float(threshold)*np.amax(R)/100] = 0
                print(file + '\n File OK, converting to ASCII...')

                EnT = np.arange(float(enInit), float(enFin), float(enStep), dtype=np.float)
            
                if EnT.shape[0] == En.shape[0]:
                    print(' Number of points in the learning dataset: ' + str(EnT.shape[0]))
                else:
                    print('\033[1m' + ' Mismatch in datapoints: ' + str(EnT.shape[0]) + '; sample = ' +  str(En.shape[0]) + '\033[0m')

                # Interpolate to new axis
                R = np.interp(EnT, En, R, left = R[0], right = 0)
                # Renormalize offset by min R
                R = R - np.amin(R)
                # Renormalize to max of R
                R = R/np.amax(R)
                    
                if first:
                    mixR = R
                    first = False
                else:
                    mixR = (mixR*index + R)/(index+1)
                index += 1

                print('\033[1m' + ' Mismatch corrected: datapoints in sample: ' + str(R.shape[0]) + '\033[0m')
                '''
                try:
                    convertFile = os.path.splitext(file)[0] + '_ASCII.txt'
                    convertR = np.transpose(np.vstack((EnT, R)))
                    with open(convertFile, 'ab') as f:
                        np.savetxt(f, convertR, delimiter='\t', fmt='%10.6f')
                except:
                    pass
                '''
                label = re.search('(.+?)__',file).group(1)
                with open(summaryMixFile, "a") as sum_file:
                    sum_file.write(str(index) + ',,,' + label + ','+file+'\n')
    
                plt.plot(EnT,R,label=label)
        except:
            print("\n Skipping: ",file)

    try:
        newR = np.transpose(np.vstack((EnT, mixR)))
    except:
        print("No usable files found\n ")
        return
    with open(mixFile, 'ab') as f:
        np.savetxt(f, newR, delimiter='\t', fmt='%10.6f')
    print("\nMixtures saved in:",mixFile, "\n")

    plt.plot(EnT, mixR, linewidth=3, label=r'Mixture')

    plt.xlabel('Raman shift [1/cm]')
    plt.ylabel('Raman Intensity [arb. units]')
    plt.legend(loc='upper right')
    plt.savefig(plotFile+".png", dpi = 160, format = 'png')  # Save plot
    plt.show()
    plt.close()

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
