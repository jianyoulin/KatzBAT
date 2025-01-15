
"""
Only be used for Med-associates Davis Rig
Hard code IPImin and IPImax to 10000 and 30000, respectively
Hard code Version=5.30 || not sure if this will impact the running of rig program
No-retries
log
2023/11/20 adding option of using variable inter-presentation intervals (VAR name: v_ipis)

"""
import numpy as np
import os, platform
import easygui


def build_bottle_sequence(bottle_positions, num_blocks = None, block = False):
    num_bottles = len(bottle_positions)
    tot_trials = num_bottles * num_blocks
    if block:
        trials = [np.random.choice(bottle_positions, num_bottles, replace=False) for _ in range(num_blocks)]
        trials = np.concatenate(trials)
    else:
        trials = list(bottle_positions) * num_blocks
        np.random.shuffle(trials)
    return trials


# Open a file to save BAT Rig params
# Gathering info from the experimenter
# subj_id = easygui.multenterbox(msg = 'What is the rat number?', fields = ['Rat ID'])
params_file_name = easygui.multenterbox(msg = 'Please provide file name?', 
                                        fields = ['File name (e.g., OR_HAB2)'])
try:
    if os.uname()[1][-2:] == 'pi':
        positions = np.arange(2, 16+1, 2)
except:
    print('Assuming you are running on a Windows machine')
    positions = np.arange(1, 16+1, 1)

n_positions = len(positions)  

fluids = easygui.multenterbox(msg = 'Please provide solution types?',
                              fields = ['Position {}'.format(i) for i in positions])
print(fluids)

bottle_positions = [positions[i] for i in range(len(positions)) if len(fluids[i]) > 0]
print(bottle_positions)

block = easygui.ynbox(msg = 'Do you want to use BLOCK design for trial arangement?', title = 'Answer: ')

v_itis = easygui.ynbox(msg = 'Do you want to use VARIABLE inter-trial intervals?', title = 'Answer: ')

num_blocks = easygui.multenterbox(msg = 'Please provide number of presentation per bottle?',
                                  fields = ['Number of Presentations per bottle'])
num_blocks = int(num_blocks[0])

tubseq = build_bottle_sequence(bottle_positions, num_blocks = num_blocks, block = block)
print(tubseq)

tubseq_str = ""
for i in range(len(tubseq)):
    if i < len(tubseq)-1:
        tubseq_str=tubseq_str+str(tubseq[i])+','
    else:
        tubseq_str=tubseq_str+str(tubseq[i])
        
fluids = [f for f in fluids if len(f) > 0] # in bottle_positions] #easygui.multenterbox(msg = 'Please provide solution types?',
                              #fields = ['Bottle {}'.format(i) for i in bottle_positions])
solutions = ""
for i in range(n_positions): 
    if i+1 in bottle_positions:
        fl_name = fluids[bottle_positions.index(i+1)]
        if i == n_positions-1:
            solutions = solutions + "{}".format(fl_name)
        else: solutions = solutions + "{},".format(fl_name)
    else:
        solutions = solutions + ","
    
fluid_concs = easygui.multenterbox(msg = 'Please provide solution concentrations (in molarity)?',
                              fields = ['Bottle {}_{}'.format(i, j) \
                                         for i, j in zip(bottle_positions, fluids)])
concentrations = ""
for i in range(n_positions): 
    if i+1 in bottle_positions:
        conc = fluid_concs[bottle_positions.index(i+1)]
        if i == n_positions-1:
            concentrations = concentrations + "{}".format(conc)
        else: concentrations = concentrations + "{},".format(conc)
    else:
        concentrations = concentrations + ","

#Other params

params = easygui.multenterbox(msg = 'Please provide info for the following params',
                              fields = ['[0] LickTime (sec)',
                                        '[1] IPITimes (sec)',
                                        '[2] MaxWaitTime (sec)',
                                        '[3] NumRetries',
                                        '[4] SessionTimeLimit (MINUTES)',
                                        '[5] MaxRetries'],
                              values = ['', '', '', 0, '', 0])

#icktime = int(params[0]) * 1000
licktime = ""
for i in range(len(tubseq)):
    if i < len(tubseq)-1:
        licktime=licktime+str(int(params[0]) * 1000)+','
    else:
        licktime=licktime+str(int(params[0]) * 1000)
        
#pitime = int(params[1]) * 1000
mean_ipi = int(params[1])
if v_itis:
    lower_bound = int(mean_ipi - mean_ipi*0.15)
    upper_bound = int(mean_ipi + mean_ipi*0.15)
    rand_ipis = np.random.choice(np.arange(lower_bound, upper_bound), size = len(tubseq), replace=True)
    print(lower_bound, upper_bound)
    print(rand_ipis)
else:
    rand_ipis = [mean_ipi] * len(tubseq)
    
ipitime = ""
for i in range(len(tubseq)):
    if i < len(tubseq)-1:
        ipitime=ipitime+str(rand_ipis[i] * 1000)+','
        #ipitime=ipitime+str(int(params[1]) * 1000)+','
    else:
        ipitime=ipitime+str(rand_ipis[i] * 1000)
        #pitime=ipitime+str(int(params[1]) * 1000)
        
print(ipitime)        
MaxWaitTime = int(params[2]) * 1000
NumRetries = int(params[3])
SessionTimeLimit = int(params[4]) * 1000 * 60
MaxReTries = int(params[5])


param_path = "C:\\ProgramData\\MED Associates\\Davis Rig\\Parameters\\"
f = open('{}{}.pro'.format(param_path, params_file_name[0]), 'w')
# f = open(file_path, 'w')
print("[Trial Parameters]", file=f)
print("NumberOfTubes={}".format(len(bottle_positions)), file=f)
print("Solutions={}".format(solutions), file=f)
print("Concentrations={}".format(concentrations), file=f)
print("NumberOfPres={}".format(len(tubseq)), file=f)
print("LickTime={}".format(licktime), file=f)
print("TubeSeq={}".format(tubseq_str), file=f)
print("IPITimes={}".format(ipitime), file=f)
print("IPIMin=20000", file=f)
print("IPIMax=30000", file=f)
print("MaxWaitTime={}".format(MaxWaitTime), file=f)
print("Version=5.30", file=f)
print("MaxReTries={}".format(MaxReTries), file=f)
print("SessionTimeLimit={}".format(SessionTimeLimit), file=f)


f.close()


