from psychopy import visual, data, logging
from psychopy.misc import fromFile
import itertools
from math import log
from copy import deepcopy
import pandas as pd
from pandas import DataFrame
import pylab, scipy
import numpy as np

def agrestiCoull95CI(x, nTrials):
    #Calculate 95% confidence interval with Agresti-Coull method for x of nTrials
    #http://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Agresti-Coull_Interval
    nTilde = nTrials + 1.96**2
    pTilde = 1/nTilde*(x + 0.5*1.96**2)
    plusMinus = 1.96*np.sqrt(1/nTilde*pTilde*(1-pTilde))
    return pTilde - plusMinus, pTilde + plusMinus

def plotDataAndPsychometricCurve(df, dataFileName):
    """
    Plot data, and fit and plot psychometric curve
    If df is not None then get data from dataFileName
    """
    if df is None:
        if type(dataFileName) is not str:
            print 'dataFileName = ', dataFileName
            raise Exception("No df supplied and no string dataFileName supplied")
        if dataFileName.endswith('.pickle'):
            df = fromFile(dataFileName)
        elif dataFileName.endswith('.txt'):
            df = pd.read_csv(dataFileName, delimiter='\t')
        elif dataFileName.endswith('.psydat'):
            trialHandler = fromFile(dataFileName)
            #raise Exception('Cant handle .psydat file, because first Alex has to write a toDataFrame function for experimentHandler, so that its data can be analyzed.')
            #Alternatively save to save trialHandler saveAsWideText to dummy file, and use returned dataframe
            df = trialHandler.saveAsWideText("temp.txt")
        #dat = tools.filetools.fromFile(dataFileName) #<class 'psychopy.data.DataHandler'>
    if not isinstance(df, pd.core.frame.DataFrame):
        raise Exception("Don't have viable DataFrame still")

    if np.all(df.dtypes==object):
        raise Exception("I thought you'd give me some numbers to work with, but everything in this dataframe is an object")
    #Need to convert_     s.convert_objects(convert_numeric=True)

    
    #tilt = df.loc[:,'tilt']
        
    #test plotting of data
    usePsychopy_ext = False
    if usePsychopy_ext:
        #have to use psychopy_ext to aggregate
        ag = psychopy_ext.stats.aggregate(df, values="respLeftRight", cols="tilt") #, values=None, subplots=None, yerr=None, aggfunc='mean', order='natural')
        print "ag = \n", ag
        plt = psychopy_ext.plot.Plot()
        plt.plot(ag, kind='line')
        print "Showing plot with psychopy_ext.stats.aggregate"
        plt.show()
        
    #dataframe aggregate
    print "df inside plotDataAndPsychometricCurve=", df
    grouped = df.groupby(['cueLeadTime']) #,'objToCueQuadrant'])
    quadrantCueleadtime = grouped.mean() #this is a dataframe, not a DataFrameGroupBy
    print "mean at eachquadrant, cueLeadTime =\n", quadrantCueleadtime
    quadrantCueleadtime = quadrantCueleadtime.reset_index() #flatten MultiIndex back into columns with rows (simple dataframe)
    
    ax1 = pylab.subplot(121)
    pylab.scatter(quadrantCueleadtime['cueLeadTime'], quadrantCueleadtime['correct'],
                          edgecolors=(1,0,0), facecolor=(1,0,0), label='leftward saccade')
    #pylab.scatter(rightwardM['tilt'], rightwardM['respLeftRight'],
    #                      edgecolors=(0,1,0), facecolor=(0,1,0), label='rightward saccade')
    pylab.legend()
    print 'Overall proportion correct =' , str( round( 100*df['correct'].mean(), 2) )
    #msg = 'proportn overCorrected at 0 tilt = ' +  str( round( 100*df['overCorrected'].mean(), 2) ) + \
    #                  '% of ' + str( df['overCorrected'].count() ) + ' trials' 
    #msg2= ' 95% Agresti-Coull CI = ' + \
    #                   str( np.round( agrestiCoull95CI(df['overCorrected'].sum(), df['overCorrected'].count()), 2) )
    #pylab.text(0.52, 0.85, msg, horizontalalignment='left', fontsize=12)
    #pylab.text(0.52,0.75, msg2, horizontalalignment='left', fontsize=12)
    
    #pylab.ylim([-0.01,1.01])
    pylab.xlabel("cueLeadTime")
    pylab.ylabel("correct")
    
    #pylab.savefig('figures/Alex.png') #, bbox_inches='tight')    
    return pylab.gcf() #return current figure
        
def plotStaircaseDataAndPsychometricCurve(fit,IV_name,DV_name,intensities,resps,descendingPsycho,threshCriterion):
    #Expects staircase, which has intensities and responses in it
    #May or may not be log steps staircase internals
    #Plotting with linear axes
    #Fit is a psychopy data fit object. Assuming that it couldn't handle descendingPsycho so have to invert the values from it
    #IV_name independent variable name
    #DV_name dependent variable name
    intensLinear= intensities
    if fit is not None:
        #generate psychometric curve
        intensitiesForCurve = np.arange(min(intensLinear), max(intensLinear), 0.01)
        thresh = fit.inverse(threshCriterion)
        if descendingPsycho:
            intensitiesForFit = 100-intensitiesForCurve
            thresh = 100 - thresh
        ysForCurve = fit.eval(intensitiesForFit)
        #print('intensitiesForCurve=',intensitiesForCurve)
        #print('ysForCurve=',ysForCurve) #debug
    if descendingPsycho:
        thresh = 100-thresh
    #plot staircase in left hand panel
    pylab.subplot(121)
    #plot psychometric function on the right.
    ax1 = pylab.subplot(122)
    figure_title = "threshold "
    if fit is None:
        figure_title += "unknown because fit was not provided"
    else:
        figure_title += 'threshold (%.2f) = %0.2f' %(threshCriterion, thresh) + '%'
        pylab.plot(intensitiesForCurve, ysForCurve, 'k-') #fitted curve
        pylab.plot([thresh, thresh],[0,threshCriterion],'k--') #vertical dashed line
        pylab.plot([0, thresh],[threshVal,threshCriterion],'k--') #horizontal dashed line
    #print thresh proportion top of plot
    pylab.text(0, 1.11, figure_title, horizontalalignment='center', fontsize=12)
    if fit is None:
        pylab.title('Fit failed')
    
    #Use pandas to calculate proportion correct at each level
    df= DataFrame({IV_name: intensLinear, DV_name: resps})
    #print('df='); print(df) #debug
    grouped = df.groupby(IV_name)
    groupMeans= grouped.mean() #a groupBy object, kind of like a DataFrame but without column names, only an index?
    intensitiesTested = list(groupMeans.index)
    pCorrect = list(groupMeans[DV_name])  #x.iloc[:]
    ns = grouped.sum() #want n per trial to scale data point size
    ns = list(ns[DV_name])
    print('df mean at each intensity\n'); print(  DataFrame({IV_name: intensitiesTested, 'pCorr': pCorrect, 'n': ns })   )
    #data point sizes. One entry in array for each datapoint

    pointSizes = 5+ 40 * np.array(ns) / max(ns) #the more trials, the bigger the datapoint size for maximum of 6
    #print('pointSizes = ',pointSizes)
    points = pylab.scatter(intensitiesTested, pCorrect, s=pointSizes, 
        edgecolors=(0,0,0), facecolors= 'none', linewidths=1,
        zorder=10, #make sure the points plot on top of the line
        )
    pylab.ylim([-0.01,1.01])
    pylab.xlim([-2,102])
    pylab.xlabel("%noise")
    pylab.ylabel("proportion correct")
    #save a vector-graphics format for future
    #outputFile = os.path.join(dataFolder, 'last.pdf')
    #pylab.savefig(outputFile)
    createSecondAxis = False
    if createSecondAxis: #presently not used, if fit to log would need this to also show linear scale
        #create second x-axis to show linear percentNoise instead of log
        ax2 = ax1.twiny()
        ax2.set(xlabel='%noise', xlim=[2, 102]) #not quite right but if go to 0, end up with -infinity? and have error
        #ax2.axis.set_major_formatter(ScalarFormatter()) #Show linear labels, not scientific notation
        #ax2 seems to be the wrong object. Why am I using pylab anyway? Matplotlib documentation seems more clear
        #for programming it is recommended that the namespaces be kept separate, http://matplotlib.org/api/pyplot_api.html
        #http://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
        ax2.set_xscale('log')
        ax2.tick_params(axis='x',which='minor',bottom='off')
        
#    #save figure to file
#    outputFile = os.path.join(dataDir, 'test.pdf')
#    pylab.savefig(outputFile)

if __name__=='__main__':  #Running this helper file, must want to test functions in this file
    #dataFileName="data/raw/Alex/Alex_spatiotopicMotion_15Dec2014_16-25_DataFrame.pickle"
    dataFileName="data/raw/Alex/Alex_spatiotopicMotion_15Dec2014_16-25_PSYCHOPY.txt"
    #dataFileName='data/raw/LK/LK100_spatiotopicMotion_02Jan2015_15-46.txt'
    #dataFileName='data/raw/LK/LK100_spatiotopicMotion_02Jan2015_15-46.psydat'
    fig = plotDataAndPsychometricCurve(None, dataFileName)
    pylab.savefig('figures/examples/AlexResults.png') #, bbox_inches='tight')
    print('The plot has been saved, as figures/examples/AlexResults.png')
    pylab.show() #pauses until window manually closed. Have to save before calling this, because closing the window loses the figure


