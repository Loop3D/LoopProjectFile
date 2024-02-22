import math


class Event:
    def __init__(self, eventId, minAge, maxAge):
        self.eventId = eventId
        self.minAge = minAge
        self.maxAge = maxAge

    def __repr__(self):
        return repr((self.eventId, self.minAge, self.maxAge))


# Check if the lst given follows the rules given
# ie. if a rules says lst[1] is always before lst[2] (1,2)
# check that this is not broken
# Input:
#   lst - a list of elements
#   rules - a list of tuples of rules tuple[0] must be before tuple[1]
#           for all rules
# Return: True if a rule is broken or if there are duplicate elements in lst
def checkBrokenRules(lst, rules):
    if len(set(lst)) != len(lst):
        return True
    for rule in rules:
        if rule[0] in lst and rule[1] in lst:
            if lst.index(rule[0]) > lst.index(rule[1]):
                return True
    return False


# Check if the lst of Events (class defined above) given follows the rules given
# ie. if a rules says lst[1] is always before lst[2] (1,2)
# check that this is not broken
# Input:
#   lst - a list of elements (as defined above)
#   rules - a list of tuples of rules tuple[0] must be before tuple[1]
#           for all rules. Tuple elements are of eventIdsuu
# Return: True if a rule is broken or if there are duplicate elements in lst
def checkBrokenEventRules(lst, rules):
    if len(set(lst)) != len(lst):
        return True
    eventIds = [a.eventId for a in lst]
    return checkBrokenRules(eventIds, rules)


# Recursive permutation calculation starting with a base number of elements
# Can add restrictions as rules
def perm(
    baseNumber,
    numberLeft=-1,
    lst=[],
    rules=[],
    current=[],
    isInvalid=checkBrokenRules,
    returnList=True,
):
    # Setup first recurse if only list only basenumber given
    if len(lst) == 0:
        numberLeft = baseNumber
        lst = range(1, baseNumber + 1)
        lst = ["{:d}".format(x) for x in lst]
    else:
        if numberLeft == -1:
            numberLeft = len(lst)

    # Quick escape for 0 or 1 rules
    if numberLeft == baseNumber and len(rules) < 2:
        count = 1
        for i in range(1, baseNumber + 1):
            count = count * i
        if len(rules) == 0:
            return count
        else:
            return count / 2

    if numberLeft == 0:
        # Base case, final element added in permutation
        if returnList:
            return [current]
        else:
            return 1
    else:
        # Standard case, recurse further with reduced remaining values
        if returnList:
            count = []
        else:
            count = 0
        for a in range(baseNumber):
            # Skip if new value will cause multiples or rules are broken
            if not isInvalid(current + [lst[a]], rules):
                count = count + perm(
                    baseNumber,
                    numberLeft=numberLeft - 1,
                    lst=[x for x in lst if x != a],
                    current=current + [lst[a]],
                    rules=rules,
                    isInvalid=isInvalid,
                    returnList=returnList,
                )
        return count


# Using averages up to 10 elements this function represents the best I could do
# at estimating the number of permutations based on the number of elements and
# the number of restrictions
# Inputs:
#   nElems - (int) the number of elements in the list to fix permutations for
#   nRules - (int) the number of restrictions/rules ie. element[2] is before
#            element[3] as (2,3)
def ApproxPerm(nElems, nRules):
    divisor = 1
    step = 1
    while nRules > 0:
        if step >= nRules:
            divisor = divisor + (nRules * math.factorial(step))
        else:
            divisor = divisor + (step * math.factorial(step))
        nRules = nRules - step
        step = step + 1
    return round(math.factorial(nElems) / divisor)


# Recursive permutation calc
# Assume sorted list of Event classes (sorted by minAge then maxAge)
# [Event(eventId, eventMinAge, eventMaxAge), ..., ...]
def CalcPermutation(eventList):
    # Define base case
    if len(eventList) <= 1:
        return 1, 1, 0

    # Larger case seek to split but otherwise do perm calc
    # look for break between minAge of element and maxAge of proceeding elements
    # minAge = eventList[1].minAge
    maxAge = eventList[0].maxAge
    workingList = eventList
    remainingList = []
    for x in range(0, len(eventList)):
        if eventList[x].minAge > maxAge:
            # Have found a break point
            workingList = eventList[0:x]
            remainingList = eventList[x:]
            break
        else:
            # Extend maxAge to compare against
            if eventList[x].maxAge > maxAge:
                maxAge = eventList[x].maxAge

    # Do calcs on worklingList
    permValue = 1
    restrictions = []
    # Case for 2 in list
    if len(workingList) == 2:
        if workingList[1].minAge < workingList[0].maxAge:
            permValue = 2
        else:
            permValue = 1
    if len(workingList) > 2:
        # Find any restrictions for permutations i.e. EventId 1 must be before eventId 3 (1<3)
        for a in range(len(workingList)):
            for b in range(a, len(workingList)):
                if workingList[a].maxAge < workingList[b].minAge:
                    restrictions.append(
                        (workingList[a].eventId, workingList[b].eventId)
                    )
        # Calc permutations with the restrictions given
        if len(workingList) > 7:
            if len(restrictions):
                permValue = ApproxPerm(len(workingList), len(restrictions))
            else:
                permValue = math.factorial(len(workingList))
        else:
            permValue = perm(
                len(workingList),
                lst=workingList,
                rules=restrictions,
                isInvalid=checkBrokenEventRules,
                returnList=False,
            )
    # Recurse with remaining list
    calcPermValue, calcWorkingLength, restValue = CalcPermutation(remainingList)
    if calcWorkingLength > len(workingList):
        return permValue * calcPermValue, calcWorkingLength, restValue
    else:
        return permValue * calcPermValue, len(workingList), len(restrictions)
