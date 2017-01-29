import sys
sys.path.insert(0,"..")

from database import db_read

db = db_read("../Domotion.db")

SensorValues = { 1: 0, 2: 1, 3: 0, 4: 1 }
ActValues = { 1: 0, 2: 1, 3: 0, 4: 1 }
TimerValues = {2: 745, 3: 0, 4: -1 }

val = db.FillSensorBuffer(SensorValues)

print val

val = db.FillActuatorBuffer(ActValues)

print val


val = db.FillTimerBuffer(TimerValues)

print val

sens = db.FindSensorbyCode(5,0,3)

print sens

print db.GetSensorProperties(sens)
print db.GetActuatorProperties(1)
print db.GetTimerProperties(1)

procs= db.FindProcessors(1,sens)
#procs= db.FindProcessors(0,1)

print procs

for i in procs:
	proc= db.GetProcessorProperties(i)
	print proc

comb=db.GetCombinerProperties(proc['Combiner'])

print comb

#if 'Dependency' in comb:
#	print db.GetDependencyProperties(comb['Dependency'])

print db.GetDependencyProperties(1)

#print db.GetTypeProperties(2)

del db