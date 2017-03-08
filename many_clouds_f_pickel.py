########################################################################
# 
# many_clouds_f.py
#
#test code to compute and print to text file 
#Temperatures, Abundances, and Luminosities of the emitters CO, C+, C, O
#using NL99_GC chemistry network included DESPOTIC2
#
########################################################################

# Want to store and read pickel files?
#   note that there is no check if ranges in pickels are current chosen ranges,
#   if change ranges, or cloud file, user should delete all pickel files
pickel_use = True
#pickel_use = False



########################################################################
# Program code
########################################################################

# Import the despotic library
from despotic import cloud_f

# Import standard python libraries
from numpy import *
from matplotlib.pyplot import *
from datetime import datetime
from datetime import timedelta
#from despotic.chemistry import NL99
from despotic.chemistry import NL99_GC

###
import pickle
from copy import deepcopy
#from results import Results


#if want interactive mode:
import code
#code.interact(local=locals())

#print to text file
f = open('textfile_test', 'w')
#print textfile

#Ranges:
#a logarithmically-spaced grid of cosmic ray ionisation rates from 2e-17 to 2e-14, in steps of 0.5 dex, a logarithmically-spaced grid of column densities from 10^22 - 10^25 in steps of 0.5 dex, and a logarithmically-spaced grid of volume densities from 10^2 - 10^6 cm^-3 in steps of 0.5 dex. Record the results.

# Range in log cosmic ray ionisation rates
logionRate = np.arange(-17., -14.01, 0.5) #many
#logionRate = np.arange(-18., -14.01, 0.5) #few
#logionRate = np.arange(-17., -16.99, 0.5) #one

# Range in log column densities
logcolDen = np.arange(22., 25.01, 0.5) #many
#logcolDen = np.arange(22., 22.51, 0.5) #few


# Range in log volumn densities
logvolDen = np.arange(2., 6.01, 0.5) #many
#logvolDen = np.arange(2., 5.01, 0.5) #few

 


class Results(object):
    def __init__(self):
        # Found Vaules, Abundances, :
        self.rxCO = 0.
        self.rxCp = 0.
        self.rxC = 0.
        self.rxO = 0.
        #Luminosities:
        self.rCOlum = 0.
        self.rCplum = 0.
        self.rClum = 0.
        self.rOlum = 0.



#timing-start
t1=datetime.now()

#from despotic.chemistry import abundanceDict

# Lower the CR ionization rate so that a fully CO composition becomes
# possible
#testcloud.rad.ionRate = 2e-17

# Raise the temperature to 20 K
#testcloud.Tg = 20.0 #need to do this to converge?


#Simultaneous Chemical and Thermal Equilibria
# Loop over column densities, getting chemical composition at each one
# and recording the value
#for lNH in logNH:
#    gmc.colDen = 10.**lNH
#    gmc.setChemEq(network=NL99_GC, verbose=True)
#    abd.append(gmc.chemnetwork.abundances)
abd=[]
lum=[]
stateList = []
resultList = []
#i, j, k are indeices for these nested for-loops

#Pickel set up:
# Find desired number of outputs
nOut = len(logionRate)+len(logcolDen)+len(logvolDen) #number of iterations
#Read existing data
restart=False
if pickel_use:
    for i in arange(0, nOut, 1):
        try:
            fp = open('many_cloud{:03d}.pkl'.format(i), 'rb')
            stateList.append(pickle.load(fp))
            fp.close()

            fp = open('many_results{:03d}.pkl'.format(i), 'rb')
            resultList.append(pickle.load(fp))
            fp.close()

            restart=True
        except IOError:
            break

#Create arrays to store luminosities:
COlum = []
Cplum = []
Clum = []
Olum = []



if restart:
    # Yes: copy last state to testcloud object to initialize it
    testcloud = deepcopy(stateList[-1])
    print 'IF YES'
else:
    print 'IF NO'
    #No:
    # Read the Test Cloud file
    #testcloud = cloud(fileName='../cloudfiles/MilkyWayGMC.desp')
    testcloud = cloud_f.cloud_f2(fileName='../cloudfiles/testcloud_many.desp')
    #Do caclulations over ranges:
    for iionRate in logionRate:
        testcloud.ionRate = 10.**iionRate
        for jcolDen in logcolDen:
            testcloud.colDen = 10.**jcolDen
            for kvolDen in logvolDen:
                testcloud.volDen = 10.**kvolDen
                print "Rates: ",iionRate," ",jcolDen," ",kvolDen
                #iteration number:
                i = np.where(logionRate==iionRate) #(i[0])[0]
                j = np.where(logcolDen==jcolDen) #(i[0])[0]
                k = np.where(logvolDen==kvolDen) #(i[0])[0]
                ix = (i[0])[0]
                jx = (j[0])[0]
                kx = (k[0])[0]
                x = ix+jx+kx
                #print "x = ",x

                #initialize instance of Results class
                r = Results()

                #testcloud.setChemEq(network=NL99_GC, evolveTemp='iterateDust', verbose=True)
                testcloud.setChemEq(network=NL99_GC, evolveTemp='iterateDust')
                abd.append(testcloud.chemnetwork.abundances)
                #print abd
    
                # Compute the luminosity of the CO lines
                testcloudlineco = testcloud.lineLum('co')
                # Compute the luminosity of the c+, c, o lines
                testcloudlinecp = testcloud.lineLum('c+')
                testcloudlinec = testcloud.lineLum('c')
                testcloudlineo = testcloud.lineLum('o')
#                lum.append(testcloudlineco)


                # Save state, both locally and to disk
                stateList.append(deepcopy(testcloud))
                fp = open('many_cloud{:03d}.pkl'.format(x), 'wb')
                pickle.dump(testcloud, fp)
                fp.close()



                # Print abundance of the species C+, C, O, CO
                print ""
                print "Abundances: "
                xCO = []
                xCp = []
                xC = []
                xO = []
                for ab in abd:
                    #print ab
                    xCO.append(ab['CO'])
                    xCp.append(ab['C+'])
                    xC.append(ab['C'])
                    xO.append(ab['O'])
                r.rxCO = ab['CO']
                r.rxCp = ab['C+']
                r.rxC = ab['C']
                r.rxO = ab['O']

            
                #print "CO = ", xCO
                #print "C+ = ", xCp
                #print "C = ", xC
                #print "O = ", xO
                #print abd.abundances["CO"]
        
                # Print luminosities of the species C+, C, O, CO
                print ""
                print "Luminosities: "
                testcloudcoTBint=array([line['intTB'] for line in testcloudlineco])
                testcloudcpTBint=array([line['intTB'] for line in testcloudlinecp])
                testcloudcTBint=array([line['intTB'] for line in testcloudlinec])
                testcloudoTBint=array([line['intTB'] for line in testcloudlineo])
                #print "CO first 5 J transitions: ", testcloudcoTBint[0:5]
                #print "C+: ", testcloudcpTBint[0]
                #print "C : ", testcloudcTBint[0]
                #print "O : ", testcloudoTBint[0]
                #print testcloudlinecplus["C+"]
                #COlum = []
                #Cplum = []
                #Clum = []
                #Olum = []

                #Save luminosities for current iteration to arrays:
                COlum.append(testcloudcoTBint[0:5])
                Cplum.append(testcloudcpTBint[0])
                Clum.append(testcloudcTBint[0])
                Olum.append(testcloudoTBint[0])

                r.rCOlum = testcloudcoTBint[0:5]
                r.rCplum = testcloudcpTBint[0]
                r.rClum = testcloudcTBint[0]
                r.rOlum = testcloudoTBint[0]
                #print 'x = ',x
                #code.interact(local=locals())
                # Save state, both locally and to disk
                resultList.append(deepcopy(r))
                fp = open('many_results{:03d}.pkl'.format(x), 'wb')
                pickle.dump(r, fp)
                fp.close()


                #print found vaules
                print "Temperatures: "
                #print "Tg = ", testcloud.Tg
                #print "Td = ", testcloud.Td
                print " Tg = "+str(testcloud.Tg)
                print " Td = "+str(testcloud.Td)
                #print xCO[0]
                #code.interact(local=locals())


# Get temperature,ionRate,colDen,volDen history from saved states
Tg=array([s.Tg for s in stateList])
Td=array([s.Td for s in stateList])
#nHmany=array([s.nH for s in stateList])
ionRate=array([s.ionRate for s in stateList])
colDen=array([s.colDen for s in stateList])
volDen=array([s.volDen for s in stateList])

#Load Results from resultList or Result pickle
xCO = array([s.rxCO for s in resultList])
    # Found Vaules, Abundances, :
xCp = array([s.rxCp for s in resultList])
xC = array([s.rxC for s in resultList])
xO = array([s.rxO for s in resultList])
    # Luminosities:
COlum = array([s.rCOlum for s in resultList])
Cplum = array([s.rCplum for s in resultList])
Clum = array([s.rClum for s in resultList])
Olum = array([s.rOlum for s in resultList])


#Writing found vaules to text files:
"""
for iionRate in logionRate:
#    testcloud.ionRate = 10.**iionRate
    
    for jcolDen in logcolDen:
#        testcloud.colDen = 10.**jcolDen

        for kvolDen in logvolDen:
#            testcloud.volDen = 10.**kvolDen
            i = np.where(logionRate==iionRate) #(i[0])[0]
            j = np.where(logcolDen==jcolDen) #(i[0])[0]
            k = np.where(logvolDen==kvolDen) #(i[0])[0]
            ix = (i[0])[0]
            jx = (j[0])[0]
            kx = (k[0])[0]
            x = ix+jx+kx
            print i,j,k
            print ix,jx,kx
            #code.interact(local=locals())
            #f.write(str(logionRate[i] )+ str(logcolDen[j] )+ str(logvolDen[k] ) +"\n")
#            f.write(str(iionRate )+ " " +str(jcolDen )+ " "+str(kvolDen ) +\
#                " "+str( xCO[x])+" "+ str(xCp[x])+" "+ str(xC[x])+" "+ str(xO[x])+"\n")


#            f.write(str("%.10f" % testcloud.Tg) +\
#                str("%.10f" % testcloud.Td) +\
#                ("%.10f" % xCO) +\
#                ("%.10f" % xCp) +\
#                ("%.10f" % xC) +\
#                ("%.10f" % xO) )

#            "Tg = "+str(testcloud.Tg)+"\n\n"+\
#            "Td = "+str(testcloud.Td)+"\n\n"+\
#            "$n_{\mathrm{H }}$ = "+str(slab.nH)+"&"+"\n"\
#                    "Tg = "+str(testcloud.Tg)+"\n\n"+\
#                    "Td = "+str(testcloud.Td)+"\n\n"+\
#                    #"$n_{\mathrm{H }}$ = "+str(slab.nH)+"&"+"\n"\
#                +"    \\\hline"+"\n")
#file2 = open('logionRate', 'w')
#np.savetxt(str(logionRate),logionRate)
"""

code.interact(local=locals())

#timing-end
t2=datetime.now()
print 'Execution time = '+str(t2-t1)






































