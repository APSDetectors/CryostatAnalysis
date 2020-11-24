import numpy as np
from scipy import stats 
import matplotlib.pyplot as plt
import pandas as pd


'''

The functions below load, reformat, split, revise, and sort log files

'''

def load_107(filepath):
    '''
    Loads and reformats relevant columns of a 107 log

    Returns
    -------
    log_107 : DataFrame
        Reformatted 107 log

    '''
    #Load 107 log
    log_filepath = r'{}'.format(filepath)
    log_107 = pd.read_csv(log_filepath, usecols = [0,1,2,3,5,7,8,9,12,13,18], skiprows = [1,2], na_filter=False)
    #Reorder and rename columns
    column_order = [0,2,3,4,6,7,5,10,8,9,1]
    column_names = ['Date/Time','Hours after Start','50 mK FAA','He-3','3K Stage Diode','Magnet Diode','50K Stage Diode','Temperature Setpoint','Magnet Current','Magnet Voltage','Notes']
    log_107 = log_107[[log_107.columns[i] for i in column_order]]
    log_107.columns = column_names 
    #Convert "Date/Time" column from string to datetime 
    log_107['Date/Time'] = pd.to_datetime(log_107['Date/Time'], infer_datetime_format=True)
    return log_107

def load_102():
    '''
    Loads and reformats relevant columns of a 102 log

    Returns
    -------
    log_102 : DataFrame
        Reformatted 102 log

    '''
    #Load 102 log
    log_filepath = r'{}'.format(input('Enter filepath: ')) #Asks user for filepath. Enter filepath without quotation marks.  
    log_102=pd.read_csv(log_filepath, usecols = [0,1,2,3,5,8,10,11,12,13,15], na_filter=False)
    #Reorder and rename columns
    column_order = [0,1,6,10,8,9,7,5,4,3,2]
    column_names = ['Date/Time','Hours after Start','50 mK FAA','ADR 1K', '3K Stage Diode','Magnet Diode','60K Stage Diode','Temperature Setpoint','Magnet Current','Magnet Voltage','Notes']
    log_102 = log_102[[log_102.columns[i] for i in column_order]]
    log_102.columns = column_names 
    #Convert "Date/Time" column from string to datetime 
    log_102['Date/Time'] = pd.to_datetime(log_102['Date/Time'], infer_datetime_format=True)
    #Recalculate "Hours after Start" column from "Date/Time" column
    log_102["Hours after Start"] = (log_102['Date/Time']-log_102.iloc[0,0]).dt.total_seconds()/3600
    return log_102

def split_107(log):
    '''
    Splits a reformatted 107 log into separate logs for separate stages (i.e. cooldown, regen, reg, and warmup)
    Stores separated logs into a tuple of 3 dictionaries
    
    Parameters
    ----------
    log : DataFrame
        Entire, reformatted 107 log. Return of load_107(). 

    Returns
    -------
    logs : dict
        Dictionary of logs for all stages (i.e. cooldown, regen, reg, and warmup)
        Key names are 'log1','log2','log3',... with numbers based on chronological order
    regenfiles : dict
        Dictionary of reformatted, sorted regen logs
        Key names are 'regen1','regen2','regen3',... with numbers based on chronological order
        Logs are reformatted: index and 'Hours from Start' start at 0 for each log 
        Logs are sorted: if the magnet does not turn on or the magnet cycle is too short/long, it is excluded from this dictionary
    regfiles : dict
        Dictionary of reformatted, sorted reg logs
        Key names are 'reg1','reg2','reg3',... with numbers based on chronological order
        Logs are reformatted: index and 'Hours from Start' start at 0 for each log 
        Logs are sorted: if the magnet current is too small/large, it is excluded from this dictionary
    '''
    #Create a dictionary storing logs of all stages 
    all_booleans = log['Notes'].map(lambda x:'Start Mag Cycle' in x or 'Mag Cycle complete' in x or 'Mag Cycle Canceled' in x).to_list() #Determine ADR cycle start and completion via Notes column
    all_booleans[0] = True
    all_booleans[-1] = True
    all_indicies = log.index[all_booleans].to_list() #Create list of indicies where run starts, run completes, ADR cycle starts, and ADR cycle completes
    logs = {} #Initialize dictionary 
    for x in range(len(all_indicies)-1):
        logs['log{}'.format(x+1)]=log.iloc[all_indicies[x]:all_indicies[x+1],:] #Add each log to dictionary 
    
    
    #Create a dictionary storing regen logs
    regen_booleans = log['Notes'].map(lambda x:'Start Mag Cycle' in x).to_list() #Determine ADR cycle start via Notes column
    regen_indicies = log.index[regen_booleans].to_list() #Create list of indicies where ADR cycle starts
    regenfiles = {} #Initialize dictionary 
    regen_count = 0 #Counter variable for naming dictionary keys 
    for x in range(len(regen_indicies)):
        #Check if magnet turns on (current reaches above 15 A) and if magnet cycle lasts appropriate length of time (between 3 to 5 hours)
        if log.iloc[regen_indicies[x]:all_indicies[all_indicies.index(regen_indicies[x])+1],8].map(lambda x:x>15).any() and \
        3<((log.iloc[all_indicies[all_indicies.index(regen_indicies[x])+1],0]-log.iloc[regen_indicies[x],0]).total_seconds()/3600)<5:
            regen_count += 1 #Increase counter variable 
            regenfiles['regen{}'.format(regen_count)]=log.iloc[regen_indicies[x]:all_indicies[all_indicies.index(regen_indicies[x])+1],:].reset_index(drop=True) #Add regen log to dictionary and reset index 
            regenfiles['regen{}'.format(regen_count)]["Hours after Start"] = (regenfiles['regen{}'.format(regen_count)]['Date/Time']-regenfiles['regen{}'.format(regen_count)].iloc[0,0]).dt.total_seconds()/3600 #Reset "Hours from Start" column
    
    
    #Create a dictionary storing reg logs
    reg_booleans = log['Notes'].map(lambda x:'Mag Cycle complete' in x or 'Mag Cycle Canceled' in x).to_list() #Determine ADR cycle completion via Notes column
    reg_indicies = log.index[reg_booleans].to_list() #Create list of indicies where ADR cycle completes
    regfiles = {} #Initialize dictionary 
    reg_count = 0 #Counter variable for naming dictionary keys 
    for x in range(len(reg_indicies)):
        #Check if magnet current is reasonable (above 0.1 A and below 2 A)
        if not log.iloc[reg_indicies[x]:all_indicies[all_indicies.index(reg_indicies[x])+1],8].map(lambda x:x<0.1).all() and \
        not log.iloc[reg_indicies[x]:all_indicies[all_indicies.index(reg_indicies[x])+1],8].map(lambda x:x>2).any():
            reg_count += 1 #Increase counter variable 
            regfiles['reg{}'.format(reg_count)]=log.iloc[reg_indicies[x]:all_indicies[all_indicies.index(reg_indicies[x])+1],:].reset_index(drop=True) #Add reg log to dictionary and reset index
            regfiles['reg{}'.format(reg_count)]["Hours after Start"] = (regfiles['reg{}'.format(reg_count)]['Date/Time']-regfiles['reg{}'.format(reg_count)].iloc[0,0]).dt.total_seconds()/3600 #Reset "Hours from Start" column 
            regfiles['reg{}'.format(reg_count)]['50 mK FAA'].replace(0,np.nan,inplace=True) #Replace 0 values in "50 mK FAA" column with NaN 
    
    
    return (logs,regenfiles,regfiles)

def temp_hold(regfiles):
    '''
    Removes sections of temperature hold logs where the magnet is off (i.e. current is less than 0.085 A)
    E.g. if a temperature hold log includes a warmup, the warmup is removed 

    Parameters
    ----------
    reg_logs : dict
        Dictionary of all temperature hold phase logs of a run 

    Returns
    -------
    reg_logs : dict
        Dictionary of revised temperature regulation phase logs of a run 

    '''
    for key,reg in regfiles.items():
        #Remove parts of temperature regulation phase logs where magnet is off
        regfiles[key] = reg.loc[reg['Magnet Current']>0.085]
        #Reset index and "Hours after Start" to start at 0 
        regfiles[key].reset_index(drop=True, inplace = True)
        regfiles[key]["Hours after Start"] = (regfiles[key]['Date/Time']-regfiles[key].iloc[0,0]).dt.total_seconds()/3600
    return regfiles

def sort_reg(regfiles):
    '''
    Separates 5 hour holds from 25 hour holds in June 2020 107 log

    Parameters
    ----------
    regfiles : dict
        Dictionary containing all temperature hold logs in the run

    Returns
    -------
    poor_holds : dict
        Dictionary containing temperature hold logs where maximum magnet current is below 0.3 A
    holds : dict
        Dictionary containing temperature hold logs where maximum magnet current is above 0.3 A

    '''
    poor_holds = {k:v for k,v in regfiles.items() if v['Magnet Current'].map(lambda x:x<0.3).all()}
    holds = {k:v for k,v in regfiles.items() if v['Magnet Current'].map(lambda x:x>0.3).any()}
    for new,old in zip(range(1,4),range(10,13)):
        holds['reg{}'.format(new)] = holds.pop('reg{}'.format(old))
    return (poor_holds,holds)

'''

The functions below create plots for a single cryostat phase

'''

def cooldown_plot(cooldown_log,window):
    '''
    Creates plot for cooldown or warmup stage, showing temperatures of temperature stages versus time

    Parameters
    ----------
    cooldown_log : DataFrame
        DataFrame of cooldown or warmup data

    Returns
    -------
    cooldown_fig : figure
        Figure of temperatures of temperature stages versus time

    '''
    ax = window.canvas.fig.add_subplot(111)
    ax.plot(cooldown_log.iloc[:,1], cooldown_log.iloc[:,2], '-', label="50 mK FAA") #Plot 50 mK stage
    ax.plot(cooldown_log.iloc[:,1], cooldown_log.iloc[:,3], '-', label= cooldown_log.columns[3]) #Plot He-3 or ADR 1K stage, depending on log file type
    #Plot 3K Stage Diode or Magnet Diode depending on log file type 
    if cooldown_log.iloc[0,4]==500:
        ax.plot(cooldown_log.iloc[:,1], cooldown_log.iloc[:,5], '-', label="Magnet Diode") #Plot Magnet Diode 
    else:    
        ax.plot(cooldown_log.iloc[:,1], cooldown_log.iloc[:,4], '-', label="3K Stage Diode") #Plot 3K Stage Diode
    ax.plot(cooldown_log.iloc[:,1], cooldown_log.iloc[:,6], '-', label= cooldown_log.columns[6]) #Plot 50 K or 60 K stage, depending on log file type
    ax.set_xlabel('Time after start (hrs)')
    ax.set_ylabel('Temperature (K)')
    ax.legend(loc='upper right')

def regen_plot(regen_log,window):
    '''
    Creates two plots for a magnet cycle stage, one showing 50 mK temperature and one showing magnet current and voltage
    
    Parameters
    ----------
    regen_log : DataFrame
        DataFrame of magnet cycle data

    Returns
    -------
    regen_plot : figure
        Figure containing two subplots: 
        Temperature of cold stage and temperature setpoint versus time
        Magnet current and voltage versus time

    '''
    ax1 = window.canvas.fig.add_subplot(121)
    ax2 = window.canvas.fig.add_subplot(122)
    
    #Temperature subplot
    ax1.plot(regen_log.iloc[:,1], regen_log.iloc[:,2], '-', label='50 mK FAA') #Plot 50 mK stage
    ax1.plot(regen_log.iloc[:,1], regen_log.iloc[:,7], '-', label='Temperature Setpoint') #Plot temperature setpoint
    ax1.set_xlabel('Time after start (hrs)')
    ax1.set_ylabel('Temperature (K)')
    ax1.legend(loc='upper right')
    
    #Magnet current and voltage subplot
    PS_I=ax2.plot(regen_log.iloc[:,1], regen_log.iloc[:,8], 'g-', label='Magnet Current') #Plot magnet current 
    ax2.set_xlabel('Time after start (hrs)')
    ax2.set_ylabel('Magnet Current (A)')
    ax3 = ax2.twinx()
    PS_V=ax3.plot(regen_log.iloc[:,1], regen_log.iloc[:,9],'r-', label='Magnet Voltage') #Plot magnet voltage
    ax3.set_ylabel('Magnet Voltage (V)')
    axs = PS_I+PS_V
    labs = [l.get_label() for l in axs]
    ax2.legend(axs, labs, loc='center')

def reg_plot(reg_log,window):
    '''
    Creates two plots for temperature hold stage, one showing 50 mK temperature and one showing magnet current and voltage
    Creates same plots as regen_plot but with adjusted legend locations
    
    Parameters
    ----------
    reg_log : DataFrame
        DataFrame of temperature regulation data

    Returns
    -------
    reg_plot : figure
        Figure containing two subplots:     
        Temperature of coldstage and temperature setpoint versus time 
        Magnet current and voltage versus time

    '''
    ax1 = window.canvas.fig.add_subplot(121)
    ax2 = window.canvas.fig.add_subplot(122)
    
    #Temperature subplot
    ax1.plot(reg_log.iloc[:,1], reg_log.iloc[:,2], '-', label='50 mK FAA') #Plot 50 mK stage
    ax1.plot(reg_log.iloc[:,1], reg_log.iloc[:,7], '-', label='Temperature Setpoint') #Plot temperature setpoint
    ax1.set_xlabel('Time after start (hrs)')
    ax1.set_ylabel('Temperature (K)')
    ax1.legend()
    
    #Magnet current and voltage subplot
    PS_I=ax2.plot(reg_log.iloc[:,1], reg_log.iloc[:,8], 'g-', label='Magnet Current') #Plot magnet current
    ax2.set_xlabel('Time after start (hrs)')
    ax2.set_ylabel('Magnet Current (A)')
    ax3 = ax2.twinx()
    PS_V=ax3.plot(reg_log.iloc[:,1], reg_log.iloc[:,9],'r-', label='Magnet Voltage') #Plot magnet voltage
    ax3.set_ylabel('Magnet Voltage (V)')
    axs = PS_I+PS_V
    labs = [l.get_label() for l in axs]
    ax2.legend(axs, labs, loc='upper right')

'''

The functions below create plots for several cryostat phases (e.g. all magnet cycles in a run, all temp holds in a run)

'''

def regen_temp_plots(regenfiles):
    '''
    Creates temperature plots for all magnet cycles in a run

    Parameters
    ----------
    regenfiles : dict
        Dictionary containing magnet cycle stage logs

    Returns
    -------
    fig : figure
        Figure containing a variable number of subplots depending on the number of magnet cycles in the run
        Each subplot shows temperature of cold stage and temperature setpoint versus time
    '''
    tot = len(regenfiles)
    col = 3
    row = tot // col
    row += tot % col
    position = range(1,tot + 1)
    fig = plt.figure(1)
    maxtime = np.max([regen.iloc[-1,1] for regen in regenfiles.values()]) #Determine length of longest magnet cycle 
    for i in range(tot):
        ax = fig.add_subplot(row,col,position[i])
        ax.plot(regenfiles['regen{}'.format(i+1)].iloc[:,1], regenfiles['regen{}'.format(i+1)].iloc[:,2], '-', label='50 mK FAA') #Plot 50 mK stage
        ax.plot(regenfiles['regen{}'.format(i+1)].iloc[:,1], regenfiles['regen{}'.format(i+1)].iloc[:,7], '-', label='Temperature Setpoint') #Plot temperature setpoint
        ax.set_xlabel('Hours after Regen')
        ax.set_ylabel('Temperature (K)')
        ax.set_xlim(-0.25,maxtime+0.25) #Set x axis limits based on longest magnet cycle
        ax.set_ylim(0,6)
        ax.legend(loc='upper right')  
        plt.subplots_adjust(wspace = 0.5, hspace=0.5)
    return fig

def regen_mag_plots(regenfiles):
    '''
    Creates plots of magnet current and voltage for all magnet cycles in a run

    Parameters
    ----------
    regenfiles : dict
        Dictionary containing magnet cycle stage logs

    Returns
    -------
    fig : figure
        Figure containing a variable number of subplots depending on the number of magnet cycles in the run
        Each subplot shows magnet current and voltage versus time

    '''
    tot = len(regenfiles)
    col = 3
    row = tot // col
    row += tot % col
    position = range(1,tot + 1)
    fig = plt.figure(2)
    maxtime = np.max([regen.iloc[-1,1] for regen in regenfiles.values()]) #Determine length of longest magnet cycle 
    for i in range(tot):
        ax = fig.add_subplot(row,col,position[i])
        PS_I=ax.plot(regenfiles['regen{}'.format(i+1)].iloc[:,1], regenfiles['regen{}'.format(i+1)].iloc[:,8], 'g-', label='Magnet Current') #Plot magnet current
        ax.set_xlabel('Hours after Regen')
        ax.set_ylabel('Magnet Current (A)')
        ax.set_xlim(-0.25,maxtime+0.25) #Set x axis limits based on longest magnet cycle
        ax.set_ylim(0,20)
        ax2 = ax.twinx()
        PS_V=ax2.plot(regenfiles['regen{}'.format(i+1)].iloc[:,1], regenfiles['regen{}'.format(i+1)].iloc[:,9],'r-', label='Magnet Voltage') #Plot magnet voltage
        ax2.set_ylabel('Magnet Voltage (V)')
        ax2.set_ylim(0,3)
        axs = PS_I+PS_V
        labs = [l.get_label() for l in axs]
        ax.legend(axs, labs, loc='center')
        plt.subplots_adjust(wspace = 0.5, hspace=0.5)
    return fig

def reg_temp_plots(regfiles):
    '''
    Creates temperature plots for all temperature holds in a run 

    Parameters
    ----------
    regfiles : dict
        Dictionary containing temperature hold stage logs

    Returns
    -------
    fig : figure
        Figure containing a variable number of subplots depending on the number of temperature holds in the run
        Each subplot shows temperature of cold stage and temperature setpoint versus time

    '''
    tot = len(regfiles)
    col = 3
    row = tot // col
    row += tot % col
    position = range(1,tot + 1)
    fig = plt.figure(3)
    maxtime = np.max([reg.iloc[-1,1] for reg in regfiles.values()]) #Determine length of longest temperature hold
    for i in range(tot):
        ax = fig.add_subplot(row,col,position[i])
        ax.plot(regfiles['reg{}'.format(i+1)].iloc[:,1], regfiles['reg{}'.format(i+1)].iloc[:,2], '-', label='50 mK FAA') #Plot 50 mK stage
        ax.plot(regfiles['reg{}'.format(i+1)].iloc[:,1], regfiles['reg{}'.format(i+1)].iloc[:,7], '-', label='Temperature Setpoint') #Plot temperature setpoint
        ax.set_xlabel('Hours after Reg')
        ax.set_ylabel('Temperature (K)')
        ax.set_xlim(-1,maxtime+1) #Set x axis limits based on longest temperature hold
        ax.set_ylim(0.035,0.075)
        ax.legend(loc='upper left') 
        plt.subplots_adjust(wspace = 0.5, hspace=0.5)
    return fig

def reg_mag_plots(regfiles):
    '''
    Creates plots of magnet current and voltage for multiple temperature holds

    Parameters
    ----------
    regfiles : dict
        Dictionary containing temperature hold stage logs

    Returns
    -------
    fig : figure
        Figure containing a variable number of subplots depending on the number of DataFrames in the dictionary
        Each subplot shows magnet current and voltage versus time

    '''
    tot = len(regfiles)
    col = 3
    row = tot // col
    row += tot % col
    position = range(1,tot + 1)
    fig = plt.figure(4)
    maxtime = np.max([reg.iloc[-1,1] for reg in regfiles.values()]) #Determine length of longest temperature hold
    for i in range(tot):
        ax = fig.add_subplot(row,col,position[i])
        PS_I=ax.plot(regfiles['reg{}'.format(i+1)].iloc[:,1], regfiles['reg{}'.format(i+1)].iloc[:,8], 'g-', label='Magnet Current') #Plot magnet current
        ax.set_xlabel('Hours after Reg')
        ax.set_ylabel('Magnet Current (A)')
        ax.set_xlim(-1,maxtime+1) #Set x axis limits based on longest temperature hold
        ax.set_ylim(0,0.7)
        ax2 = ax.twinx()
        PS_V=ax2.plot(regfiles['reg{}'.format(i+1)].iloc[:,1], regfiles['reg{}'.format(i+1)].iloc[:,9],'r-', label='Magnet Voltage') #Plot magnet voltage
        ax2.set_ylabel('Magnet Voltage (V)')
        ax2.set_ylim(0,7)
        axs = PS_I+PS_V
        labs = [l.get_label() for l in axs]
        ax.legend(axs, labs, loc='upper right')
        plt.subplots_adjust(wspace = 0.5, hspace=0.75)
    return fig

def reg_3K_plots(regfiles):
    '''
    Creates temperature plots of 3K stage for all temperature hold phases of a run 

    Parameters
    ----------
    regfiles : dict
        Dictionary containing all temperature hold logs in a run 

    Returns
    -------
    fig : figure
        Figure containing a variable number of subplots depending on the number of temperature holds in a run
        Each subplot shows temperature of 3K stage versus time 

    '''
    tot = len(regfiles)
    col = 3
    row = tot // col
    row += tot % col
    position = range(1,tot + 1)
    fig = plt.figure(5)
    maxtime = np.max([reg.iloc[-1,1] for reg in regfiles.values()]) #Determine length of longest temperature hold
    for i in range(tot):
        ax = fig.add_subplot(row,col,position[i])
        ax.plot(regfiles['reg{}'.format(i+1)].iloc[:,1], regfiles['reg{}'.format(i+1)].iloc[:,4], '-', label='3K Stage Diode') #Plot 3K stage
        ax.set_xlabel('Hours after Reg')
        ax.set_ylabel('Temperature (K)')
        ax.set_xlim(-1,maxtime+1) #Set x axis limits based on longest temperature hold
        ax.set_ylim(2.3,3.7)
        ax.legend(loc='upper left') 
        plt.subplots_adjust(wspace = 0.5, hspace=0.5)
    return fig

'''

The functions below calculate various summary quantities

'''

def temp_summary(regfiles, cryostat):
    '''
    Creates dictionary of temperature-related summary quantities for all temperature stages (i.e. 50 mK, 3K, etc) 
    and all temperature hold phases of a run.

    Parameters
    ----------
    regfiles : dict
        Dictionary of all temperature hold logs of a run 

    Returns
    -------
    temp_qtys : dict
        Keys are temperatures (i.e. '50 mK', '3 K', etc)
        Values are DataFrames of summary quantities for the given temperature stage and all temperature hold phases of a run
            Index is date and time of the temperature hold 
            Columns are summary quantities for the given temperature stage (i.e. minimum, maximum, range, mean, standard deviation) 

    '''
    #Slightly different logic depending on cryostat model due to unique column names 
    if cryostat == 107:
        temps = ['50 mK','He-3','3 K','50 K']
        columns = [2,3,4,6]
    elif cryostat == 102: 
        temps = ['50 mK','1 K', 'Magnet Diode','60 K']
        columns = [2,3,5,6]
    temp_qtys = {} #Initialize dictionary 
    for i,j in zip(columns,temps): #Loop through each temperature stage
        #Create an array of lists. Each list contains the date and summary quantities for a single temperature hold. 
        qtys = np.array([[log.iloc[0,0], np.nanmin(log.iloc[:,i]), np.nanmax(log.iloc[:,i]), np.nanmax(log.iloc[:,i])-np.nanmin(log.iloc[:,i]), np.nanmean(log.iloc[:,i]), np.nanstd(log.iloc[:,i])] for log in regfiles.values()])
        #Create DataFrame from array and store in dictionary 
        temp_qtys[j] = pd.DataFrame(data=qtys[:,1:],index = qtys[:,0],columns = ['{} min'.format(j), '{} max'.format(j),'{} range'.format(j),'{} mean'.format(j),'{} std dev'.format(j)]).sort_index()
    return temp_qtys

def temp_summary_combine(temp_qtys, cryostat):
    '''
    Creates a single spreadsheet of temperature-related summary quantities for all temperature stages (i.e. 50 mK, 3K, etc)
    and all temperature holds of a run.

    Parameters
    ----------
    temp_qtys : dict
        Return of temp_summary(regfiles)

    Returns
    -------
    temp_qtys_combined : DataFrame
        DataFrame of temperature-related summary quantities for all temperature stages and all temperature holds
        Index is date and time of the temperature hold
        Columns are summary quantities for all temperature stages (i.e. 50 mK min, 50 mK max, ... 50 K mean, 50 K std dev) 

    '''
    if cryostat == 107:
        temp_qtys_combined = pd.concat([temp_qtys['50 mK'],temp_qtys['He-3'],temp_qtys['3 K'],temp_qtys['50 K']],axis=1)
    elif cryostat == 102:
        temp_qtys_combined = pd.concat([temp_qtys['50 mK'],temp_qtys['1 K'],temp_qtys['3 K'],temp_qtys['60 K']],axis=1)
    return temp_qtys_combined

def hold_summary(regfiles):
    '''
    Creates spreadsheet of magnet-related summary quantities for all temperature holds of a run.
    
    Parameters
    ----------
    regfiles : dict
        Dictionary of all temperature hold logs of a run 

    Returns
    -------
    hold_qtys : DataFrame
        DataFrame of magnet-related summary quantities for all temperature holds
        Index is date and time of temperature hold 
        Columns are summary quantities (i.e. hold time, maximum current, rate of current decrease 1, etc) 

    '''
    qtys = [] #Initialize list
    for log in regfiles.values(): #Loop through all temperature hold logs in a run 
        #Revise each log: select relevant rows, start log from when magnet reaches maximum current, and reset index and "Hours after Start" to 0
        hold = log.iloc[np.argmax(log['Magnet Current']):,[0,1,8]].reset_index(drop=True)
        hold["Hours after Start"] = (hold['Date/Time']-hold.iloc[0,0]).dt.total_seconds()/3600
        holdtime = hold.iloc[-1,1] #Hold time is last entry of "Hours after Start" column 
        maxcurrent = np.max(hold['Magnet Current']) #Calculate max current
        #Calculate rate of magnet current decrease in 3 different ways
        slope1 = stats.linregress(hold['Hours after Start'],hold['Magnet Current'])[0] #scipy linear regression
        slope2 = (hold.iloc[-1,2]-hold.iloc[0,2])/hold.iloc[-1,1] #maximum current / hold time
        slope3 = np.mean(np.diff(hold['Magnet Current'])/np.diff(hold['Hours after Start'])) #average rate of change 
        #Append list of summary quantities for a temp hold log to list
        qtys.append([log.iloc[0,0], holdtime, maxcurrent, slope1, slope2, slope3])
    qtys = np.asarray(qtys) #Convert to numpy array 
    #Create Dataframe from array 
    hold_qtys = pd.DataFrame(data=qtys[:,1:],index = qtys[:,0],columns = ['Hold Time', 'Max Current','Current Rate 1','Current Rate 2','Current Rate 3']).sort_index()
    return hold_qtys

def coolwarm_time(coolwarm_log):
    '''
    Calculates cooldown or warmup time. 

    Parameters
    ----------
    coolwarm_log : DataFrame
        Cooldown or warmup log 

    Returns
    -------
    coolwarm_time : float
        Cooldown or warmup time in hours
        Returns error message if log does not contain a full cooldown or warmup

    '''
    #Check if log includes full cooldown or warmup 
    if coolwarm_log['50 mK FAA'].between(284,286).any() and coolwarm_log['50 mK FAA'].between(3.5,4.5).any():
        #Cooldown/warmup defined as 50 mK stage above 3.5 K and below 286 K
        coolwarm_log = coolwarm_log.loc[(coolwarm_log['50 mK FAA']<286) & (coolwarm_log['50 mK FAA']>3.5)]
        coolwarm_log.reset_index(drop=True, inplace = True)
        coolwarm_log["Hours after Start"] = (coolwarm_log['Date/Time']-coolwarm_log.iloc[0,0]).dt.total_seconds()/3600
        coolwarm_time = coolwarm_log.iloc[-1,1] #Cooldown/warmup time is last entry of "Hours after Start" column 
        return coolwarm_time
    #If there is no full cooldown or warmup, return error message
    else:
        return "No full cooldown or warmup logged"
    
def regen_time(regen_log):
    '''
    Calculates magnet cycle time. 

    Parameters
    ----------
    regen_log : DataFrame
        Magnet cycle log 

    Returns
    -------
    regen_time : float
        Magnet cycle time in hours 

    '''
    regen_log = regen_log.loc[regen_log['Magnet Current']>0.006] #Select rows where magnet current is above 0.006 A
    regen_log.reset_index(drop=True, inplace = True)
    regen_log["Hours after Start"] = (regen_log['Date/Time']-regen_log.iloc[0,0]).dt.total_seconds()/3600
    regen_time = regen_log.iloc[-1,1] #Magnet cycle time is last entry of "Hours after Start" column 
    return regen_time

def regen_summary(regenfiles): 
    '''
    Creates Pandas Series of magnet cycle times for all magnet cycles in a run

    Parameters
    ----------
    regenfiles : dict
        Dictionary of all magnet cycle logs in a run

    Returns
    -------
    regen_times : Series
        Series of all magnet cycle times in a run
        Magnet cycles are in chronological order, and the index is default

    '''
    #Create array of lists, with each list containing the magnet cycle number and magnet cycle time for a magnet cycle.
    qtys = np.array([np.array([key[5:],regen_time(log)]) for key, log in regenfiles.items()])
    #Create Pandas Series from array 
    regen_times = pd.DataFrame(data=qtys[:,1],index = qtys[:,0], columns = ['Regen times']).sort_index().reset_index(drop=True)
    return regen_times

'''

The functions below create various summary quantity plots for multiple log files 
Unlike previous plot functions, these functions take no parameters and instead take user input
They are specific to 107 log files

'''

def maxcurrent_holdtime(): 
    '''
    Creates plot of maximum magnet current versus hold time for temperature holds across multiple log files. 
    Takes user input for number of log files and log filepaths
    
    Returns
    -------
    fig : figure
        Scatter plot of maximum magnet current versus hold time for temperature holds across multiple log files
        Each log file has a unique marker color; legend shows date of each log file

    '''
    fig = plt.figure(6)
    ax = fig.add_subplot(111)
    ax.set_xlabel('Hold Time (hrs)')
    ax.set_ylabel('Max Current (A)')
    num = int(input('How many log files? ')) #Ask user for number of log files 
    for i in range(num): #Loop through number of log files 
        log = load_107() #Ask user for log filepath
        label = str(log.iloc[0,0])[:10]
        dicts = split_107(log)
        regs = temp_hold(dicts[2]) #Dictionary of all, revised temperature hold logs
        hold = hold_summary(regs) #DataFrame of magnet-related summary quantities 
        #Plot max current vs. hold time 
        ax.scatter(hold.loc[:,'Hold Time'],hold.loc[:,'Max Current'], s=10, marker="s", label=label)
    ax.legend(loc = 'upper right')
    return fig

def stddev_time():
    '''
    Creates plot of 50 mK stage standard deviation versus date of temperature hold for temperature holds across multiple log files
    Takes user input for number of log files and log filepaths
        
    Returns
    -------
    fig : figure
        Scatter plot of 50 mK stage standard deviation versus date of temperature hold for temperature holds across multiple log files

    '''
    fig = plt.figure(7)
    ax = fig.add_subplot(111)
    ax.set_xlabel('Date')
    ax.set_ylabel('50 mK Std Dev')
    ax.set_ylim(-0.001,0.002) #Y-axis limits may need to be manually adjusted 
    num = int(input('How many log files? ')) #Ask user for number of log files
    for i in range(num): #Loop through number of log files
        log = load_107() #Ask user for log filepath 
        dicts = split_107(log)
        regs = temp_hold(dicts[2]) #Dictionary of all, revised temperature hold logs
        temp = temp_summary(regs)['50 mK'] #DataFrame of temperature-related summary quantities for 50 mK stage
        x = temp.index #Get date and time of each temperature hold 
        ax.scatter(x,temp.loc[:,'50 mK std dev'], s=10, marker="s") #Plot 50 mK std dev versus date of temp hold
    return fig

def temp_minmaxmean(): 
    '''
    Creates plot of min, max, and mean of a temperature stage versus date of temperature hold for temperature holds across multiple log files
    Takes user input for number of log files and log filepaths

    Returns
    -------
    fig : figure
        Stacked error bar plot of min, max, and mean of a temperature stage versus date of temperature hold for temperature holds across multiple log files

    '''
    fig = plt.figure(8)
    ax = fig.add_subplot(111)
    ax.set_xlabel('Date')
    ax.set_ylabel('Temp (K)')
    num = int(input('How many log files? ')) #Ask user for number of log files
    for i in range(num):#Loop through number of log files
        log = load_107() #Ask user for log filepath
        dicts = split_107(log)
        regs = temp_hold(dicts[2]) #Dictionary of all, revised temperature hold logs
        temps = temp_summary_combine(temp_summary(regs)) #DataFrame of temperature-related summary quantities for all temperature stages and all temperature holds
        mins = temps['50 K min'] #Manually change temperature stage by changing column names
        maxes = temps['50 K max']
        means = temps['50 K mean']
        dates = temps.index
        #Create stacked error bar plot showing min, max, and mean of temperature stage versus date of temperature hold
        ax.errorbar(dates, means, [means - mins, maxes - means], fmt='.k', ecolor='gray', lw=1)
    return fig 

#log=load_107(r"C:/Users/Goldfishy/Documents/Argonne 2020/Cyrostat Scrips/2020_06_18_17;08snout_swissx2_1BM.csv")
#print(str(log.iloc[0,0])[:10])