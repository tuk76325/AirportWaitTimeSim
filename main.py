import random
import simpy
from statistics import mean

totalPass = 0 #num Passengers
boardTimes = []
scanTimes = []
totalTimes = []
arrivalRate = 50
checkRate = 0.75
scanMin = 0.5
scanMax = 1.0
simTime = 360
numBoard = 35
numScans = 35
numRep = 6

class CheckQueue(object): #CheckQueue = Carwash
    def __init__(self, env, numScans, numBoard):
        self.env = env
        self.scans = []
        for i in range(numScans):
            self.scans.append(simpy.Resource(env,1)) #this many scanners each having only 1 in at a time
        self.boarders = simpy.Resource(env, numBoard)

    def boardCheck(self, passenger): #board pass check process
        yield self.env.timeout(random.expovariate(1/checkRate))

    def scanCheck(self, passenger): #scanner check process
        yield self.env.timeout(random.uniform(scanMin, scanMax))

def passenger(env, name, CheckQ, numScans):
    global boardTimes
    global scanTimes
    global totalTimes

    arrivalTime = env.now
    boardTime = 0 #total time for boarding
    scanTime = 0 #total time spent getting scanning


    #check boarding time
    with CheckQ.boarders.request() as request:
        yield request
        btimeIn = env.now #time at start of boarding check
        yield env.process(CheckQ.boardCheck(name))
        btimeOut = env.now #time at end of boarding check
        boardTime = btimeOut - btimeIn #time spent boarding

    #pick shortest queue for scanning
    minScan = 0
    for i in range(1, numScans):
        if (len(CheckQ.scans[i].queue) < len(CheckQ.scans[minScan].queue)):
            minScan = i

    #check scanning time
    with CheckQ.scans[minScan].request() as request:
        yield request
        timeIn = env.now #time at start of boarding check
        yield env.process(CheckQ.scanCheck(name))
        timeOut = env.now #time at end of boarding check
        scanTime = timeOut - timeIn #time spent scanning

    leavingTime = env.now #time at leaving the entire process
    boardTimes.append(boardTime)
    scanTimes.append(scanTime)
    totalTimes.append(leavingTime-arrivalTime)

    # print('arrival Time: {}, board Time: {}, scan Time: {}, leaving Time: {}'.format(arrivalTime, boardTime, scanTime, leavingTime))

def passengerArrival(env, CheckQ, arrivalRate, numScans):
    global totalPass

    #internal tracker for each rep
    numPass = 0

    while True:
        yield env.timeout(random.expovariate(arrivalRate)) #arrival time

        numPass+=1
        totalPass+=1

        #passenger creation after arrival time is initiated
        env.process(passenger(env, f'pass {numPass}', CheckQ, numScans))



for i in range(numRep):

    env = simpy.Environment()
    checkQ = CheckQueue(env, numScans=numScans, numBoard=numBoard)

    #start simulation by pass arriving
    env.process(passengerArrival(env, checkQ, arrivalRate=arrivalRate, numScans=numScans))

    #run sim for 6 hrs
    env.run(simTime)

# print(boardTimes[:5])
# print('------------------------------')
# print(scanTimes[:5])
# print('------------------------------')
# print(totalTimes[:5])

totalWaitTime = [] #each index is a passenger and their times boarding/scanning/waiting
for i in range(len(boardTimes)):
    totalWaitTime.append((totalTimes[i] - scanTimes[i] - boardTimes[i]))

print('The average wait time is: {}'.format(mean(totalWaitTime)))