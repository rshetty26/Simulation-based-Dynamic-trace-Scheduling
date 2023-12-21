def commit(commitnum): 
    global robuffer, freeList, mapTable, Rstall, Commit 
    Stall = False
    for x in range(len(dispFree)):
        freeList.remove(dispFree[x]) # Removes the dispatched matches from the Free List
    dispFree = [] # Resets the dispatch list
    commitDependance = []
    count = 0

    while(count < width and (not Stall) and (len(issueQueue) > 0) and Commit > 0):
        free = issueQueue[0] 
        if ((free[0] == "R" or not free[3] in commitDependance and free[0] == "L" or (not free[1] in commitDependance and free[0] == "S") or (not free[2] in commitDependance and free[0] == "I"))) and (issueStatus[issueQueue.index(free)] and (free[0] != "S")): 
            readyTable[int(free[1])] = True # set the ready table to free 
            commitDependance.append(free[1]) # set the free index to a dependance 
        else: # If there is no match, then stall needs to occur
            Stall = True
    x = commitnum + count
    return x #return the amount to commit
    
def WB(cyclecount):
    global writeBack, readyTable, robuffer, issueQueue, Commit
    if (cyclecount > 4): # since this is the fourth stage in the list, making sure it's not going earlier than it should and stalls if called early
        Commit = 0 
        while ((Commit < width) and (len(writeBack) > 0)):
            if (issueStatus[robuffer.index(writeBack[0])]): 
                x = robuffer.index(writeBack[0]) + 1
                while (x < len(robuffer)): # runs through the read out buffer to check
                    if (writeBack[0] == robuffer[x]): # if it is in read out buffer, then return Issue and set to cycle count
                        issueStatus[x] = True
                        writebackCycle[x] = cyclecount
                    x += 1 # increment
            else:
                issueStatus[robuffer.index(writeBack[0])] = True # otherwise
                writebackCycle[robuffer.index(writeBack[0])] = cyclecount
            writeBack.remove(writeBack[0]) #remove frmo write back after running through
            Commit += 1 

def Issue(cyclecount): 
    global Rstall, readyTable, issueQueue, loadStore, writeBack, dependance, issueStatus
    index, count = 0, 0
    Issue = False
    dependance, writeBack = [], []
    if (cyclecount > 3): 
        while (count < width and index < len(robuffer)): #checking against proper width and not overflowing buffer
            currentInst = robuffer[index]
            if (not issueStatus[index]): # while there aren't any issues
                if (currentInst[0] == "R"): #check instruction type for issue
                    if(readyTable[int(currentInst[2])] and readyTable[int(currentInst[3])]) or ((currentInst[1] == currentInst[2]) or (currentInst[1] == currentInst[3])):
                        Issue = True #if WAW or WAR dependencies exist, mark issue
                elif (currentInst[0] == "I"):
                    if (readyTable[int(currentInst[2])]) or (currentInst[1] == currentInst[2]):
                        Issue = True
                elif (currentInst[0] == "L"):
                    if(readyTable[int(currentInst[3])]) or (loadStore[0] == currentInst):
                        Issue = True
                    dependance.append(currentInst[1])
                elif (currentInst[0] == "S"):
                    if (readyTable[int(currentInst[1])] and readyTable[int(currentInst[3])]) and (loadStore[0] == currentInst):
                        Issue = True
                

                if ((count > 0) and Issue):
                    if (currentInst[0] == "R"): #checking for exceptions to remove false issues calls
                        if(((currentInst[2] in dependance) or (currentInst[3] in dependance))):
                            Issue = False
                            if ((not (currentInst[2] in dependance) or not (currentInst[3] in dependance))):
                                dependance.append(currentInst[1])
                    elif (currentInst[0] == "L") and (currentInst[3] in dependance):
                        Issue = False
                        dependance.remove(currentInst[1])
                        loadStore.insert(0, currentInst)
                    elif ((currentInst[0] == "S") and ((currentInst[3] in dependance) or (currentInst[1] in dependance))) or ((currentInst[0] == "I") and (currentInst[2] in dependance)):
                        Issue = False
            
            if(Issue): # If an issue exists, add upon
                if(currentInst[0] != "S" and (not currentInst[1] in dependance)):
                    dependance.append(currentInst[1])
                writeBack.append(currentInst)
                issueCycle[index] = cyclecount
                Issue = False
                count += 1
            index += 1

def Dispatch(cyclecount): 
    global dispatchNum, robuffer, issueQueue, loadStore
    if (cyclecount > 2): # third in pipeline
        count = 0
        while (count < width) and (len(dispatchCycle) < instructionCount) and (count < Rnum):
            currentInst = instructions[dispatchNum]
            if(currentInst[0] == "L" or currentInst[0] == "S"):
                loadStore.append(currentInst) # saving L and S instructions to load store
            robuffer.append(currentInst)  #also adding instructions to buffer and issue Queue
            issueQueue.append(currentInst) 
            if(len(dispatchCycle) < instructionCount): 
                dispatchCycle.append(cyclecount) #while dispatch is less than number of instructions, add cycles to Cycle Count
            count += 1
            dispatchNum += 1

def Rename(cyclecount):
    global instructionNum, freeList, mapTable, readyTable, currentInst, Rnum, Rstall
    Rnum = 0
    if cyclecount > 1 and (len(renameCycle) < instructionCount):
        count = 0
        while (count < width and instructionNum < len(instructions)):
            currentInst = instructions[instructionNum]
            if not Rstall:
                if currentInst[0] == "L": # If it is an L type instruction, 
                    if not currentInst[3] in mapTable: #check against map table
                        mapTable.append(currentInst[3])

                    if currentInst[1] in mapTable: #check for stalls
                        if (len(freeList) < physReg - 32):
                            freeList.append(currentInst[1])
                            readyTable[int(currentInst[1])] = False
                        else:
                            Rstall = True
                    else: #otherwise add register to map table and free list
                        mapTable.append(currentInst[1])
                        freeList.append(currentInst[1])
                        readyTable[int(currentInst[1])] = False
                    instructionNum += 1
                
                elif(currentInst[0] == "R"): #continue for R
                    if (not currentInst[2] in mapTable):
                        mapTable.append(currentInst[2])
                    
                    if (not currentInst[3] in mapTable):
                        mapTable.append(currentInst[3])
                    
                    if (currentInst[1] in mapTable):
                        if(len(freeList) < (physReg - 32)):
                            freeList.append(currentInst[1])
                            readyTable[int(currentInst[1])] = False
                        else:
                            Rstall = True
                    else:
                        mapTable.append(currentInst[1])
                        freeList.append(currentInst[1])
                        readyTable[int(currentInst[1])] = False

                    instructionNum += 1

                elif (currentInst[0] == "S"): # S
                    if (not currentInst[3] in mapTable):
                        mapTable.append(currentInst[3])
                    
                    if (not currentInst[1] in mapTable):
                        mapTable.append(currentInst[1])

                    instructionNum += 1
                              
                elif(currentInst[0] == "I"): # and I 
                    if (not currentInst[2] in mapTable):
                        mapTable.append(currentInst[2])
                    
                    if (currentInst[1] in mapTable):
                        if(len(freeList) < (physReg - 32)):
                            freeList.append(currentInst[1])
                            readyTable[int(currentInst[1])] = False
                        else:
                            Rstall = True
                    else:
                        mapTable.append(currentInst[1])
                        freeList.append(currentInst[1])
                        readyTable[int(currentInst[1])] = False

                    instructionNum += 1
                    if (currentInst[1] == currentInst[2]):
                        readyTable[int(currentInst[1])] = True
                
                if (not Rstall) and (len(renameCycle) < instructionCount): #stall case
                    renameCycle.append(cyclecount)
                    Rnum += 1
            count += 1

def Decode(cyclecount):
    if (cyclecount > 0):
        for x in range(width):
            if (len(decodeCycle) < instructionCount): #while cycles less than instruction count, add to decode cycle count
                decodeCycle.append(cyclecount)

def fetch(fetchIndex, cyclecount): 
    if (fetchIndex < (instructionCount/width)): #fetch instruction while maintaining specified width
        for x in range(width):
            if (len(fetchCycle) < instructionCount):
                fetchCycle.append(cyclecount) # add fetch cycle count for all valid instructions
    return fetchIndex + 1

def EmitOutput(fetch, decode, rename, dispatch, issue, writeback, commit, instructionCount):
    out = open("out.txt", "w")
    output = ""
    for x in range(instructionCount): #return output for file
        output += str(fetch[x]) + "," + str(decode[x]) + "," + str(rename[x]) + "," + str(dispatch[x]) + "," + str(issue[x]) + "," + str(writeback[x]) + "," + str(commit[x]) + "\n"
    out.write(output)

import csv
instructions = list(csv.reader(open("test.in"), delimiter = ','))
instructionCount = len(instructions[1:])
physReg = int(instructions[0][0])
width = int(instructions[0][1])
instructionNum, dispatchNum = 1, 1
fetchCycle, decodeCycle, renameCycle, dispatchCycle, issueCycle, writebackCycle, commitCycle = [], [], [], [], [], [], []
mapTable, freeList, loadStore, issueQueue, robuffer, writeBack, dispFree, dependance, readyTable, issueStatus = [], [], [], [], [], [], [], [], [], []
Rstall = False
Rnum, Commit = 0, 0
for x in range(physReg): #count up phys Reg from input for ready table available registers
    if (x < 32):
        readyTable.append(True)
    else:
        readyTable.append(False)
for x in range(instructionCount): # set up
    issueCycle.append(0)
    writebackCycle.append(0)
    issueStatus.append(False)

if (physReg < 32):
    open("out.txt", "w").write() # if physReg is less than 32, set blank text file
else:
    committedInsts = 0
    fetchIndex = 0
    cyclecount = 0
    while(committedInsts < instructionCount and cyclecount < 15):
        committedInsts = commit(committedInsts)
        WB(cyclecount)
        Issue(cyclecount)
        Dispatch(cyclecount)
        Rename(cyclecount)
        Decode(cyclecount)
        fetchIndex = fetch(fetchIndex, cyclecount)
        cyclecount += 1
    EmitOutput(fetchCycle, decodeCycle, renameCycle, dispatchCycle, issueCycle, writebackCycle, commitCycle, instructionCount)
