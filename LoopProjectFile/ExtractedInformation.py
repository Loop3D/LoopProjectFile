# import netCDF4
import LoopProjectFile
import LoopProjectFile.LoopProjectFileUtils as LoopProjectFileUtils

# import numpy


# Check Extracted Information valid if present
def CheckExtractedInformationValid(rootGroup, verbose=False):
    """
    **CheckExtractedInformationValid** - Checks for valid extracted information
    given a netCDF root node

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
    bool
        True if valid extracted information in project file, False otherwise.

    """
    valid = True
    if "ExtractedInformation" in rootGroup.groups:
        if verbose:
            print("  Extracted Information Group Present")
        eiGroup = rootGroup.groups.get("ExtractedInformation")
        if verbose:
            print(eiGroup)
    else:
        if verbose:
            print("No Extracted Information Group Present")
    return valid


def GetExtractedInformationGroup(rootGroup, verbose=False):
    return LoopProjectFileUtils.GetGroup(rootGroup, "ExtractedInformation", verbose)


def GetStratigraphicInformationGroup(rootGroup, verbose=False):
    resp = GetExtractedInformationGroup(rootGroup, verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(
            resp["value"], "StratigraphicInformation", verbose
        )


def GetDrillholeDescriptionGroup(rootGroup, verbose=False):
    resp = GetExtractedInformationGroup(rootGroup, verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(
            resp["value"], "DrillholeInformation", verbose
        )


def GetEventLogGroup(rootGroup, verbose=False):
    resp = GetExtractedInformationGroup(rootGroup, verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"], "EventLog", verbose)


def GetEventRelationshipsGroup(rootGroup, verbose=False):
    resp = GetExtractedInformationGroup(rootGroup, verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(
            resp["value"], "EventRelationships", verbose
        )


def CreateEventLogGroup(extractedInformationGroup):
    elGroup = extractedInformationGroup.createGroup("EventLog")
    elGroup.setncattr("faultEventIndex_MaxValid", -1)
    elGroup.setncattr("foldEventIndex_MaxValid", -1)
    elGroup.setncattr("foliationEventIndex_MaxValid", -1)
    elGroup.setncattr("discontinuityEventIndex_MaxValid", -1)
    elGroup.createDimension("faultEventIndex", None)
    elGroup.createDimension("foldEventIndex", None)
    elGroup.createDimension("foliationEventIndex", None)
    elGroup.createDimension("discontinuityEventIndex", None)
    faultEventType_t = elGroup.createCompoundType(
        LoopProjectFile.faultEventType, "FaultEvent"
    )
    elGroup.createVariable(
        "faultEvents", faultEventType_t, ("faultEventIndex"), zlib=True, complevel=9
    )
    foldEventType_t = elGroup.createCompoundType(
        LoopProjectFile.foldEventType, "FoldEvent"
    )
    elGroup.createVariable(
        "foldEvents", foldEventType_t, ("foldEventIndex"), zlib=True, complevel=9
    )
    foliationEventType_t = elGroup.createCompoundType(
        LoopProjectFile.foliationEventType, "FoliationEvent"
    )
    elGroup.createVariable(
        "foliationEvents",
        foliationEventType_t,
        ("foliationEventIndex"),
        zlib=True,
        complevel=9,
    )
    discontinuityEventType_t = elGroup.createCompoundType(
        LoopProjectFile.discontinuityEventType, "DiscontinuityEvent"
    )
    elGroup.createVariable(
        "discontinuityEvents",
        discontinuityEventType_t,
        ("discontinuityEventIndex"),
        zlib=True,
        complevel=9,
    )
    return elGroup


# Set fault log
def SetEventLog(root, data, indexName, variableName, append=False, verbose=False):
    response = {"errorFlag": False}
    resp = GetExtractedInformationGroup(root)
    if resp["errorFlag"]:
        # Create  Extracted Information Group as it doesn't exist
        eiGroup = root.createGroup("ExtractedInformation")
    else:
        eiGroup = resp["value"]

    resp = GetEventLogGroup(root)
    if resp["errorFlag"]:
        elGroup = CreateEventLogGroup(eiGroup)
    else:
        elGroup = resp["value"]

    if elGroup:
        eventLocation = elGroup.variables[variableName]
        index = 0
        if append:
            index = elGroup.dimensions[indexName].size
        for i in data:
            eventLocation[index] = i
            index += 1
        elGroup.setncattr(indexName + "_MaxValid", index)
    else:
        errStr = "(ERROR) Failed to create event log group"
        if verbose:
            print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    return response


def SetFaultLog(root, data, append=False, verbose=False):
    return SetEventLog(root, data, "faultEventIndex", "faultEvents", append, verbose)


def SetFoldLog(root, data, append=False, verbose=False):
    return SetEventLog(root, data, "foldEventIndex", "foldEvents", append, verbose)


def SetFoliationLog(root, data, append=False, verbose=False):
    return SetEventLog(
        root, data, "foliationEventIndex", "foliationEvents", append, verbose
    )


def SetDiscontinuityLog(root, data, append=False, verbose=False):
    return SetEventLog(
        root, data, "discontinuityEventIndex", "discontinuityEvents", append, verbose
    )


def GetEventLog(
    root, indexName, variableName, indexList=[], indexRange=(0, 0), verbose=False
):
    response = {"errorFlag": False}
    resp = GetEventLogGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        elGroup = resp["value"]
        data = []
        maxValidIndex = min(
            elGroup.dimensions[indexName].size,
            elGroup.getncattr(indexName + "_MaxValid"),
        )
        # Select all option
        if (
            indexList == []
            and len(indexRange) == 2
            and indexRange[0] == 0
            and indexRange[1] == 0
        ):
            # Select all
            for i in range(0, maxValidIndex):
                data.append((elGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((elGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on indices range option
        elif (
            len(indexRange) == 2
            and indexRange[0] >= 0
            and indexRange[1] >= indexRange[0]
        ):
            for i in range(indexRange[0], indexRange[1]):
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((elGroup.variables.get(variableName)[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose:
                print(errStr)
            response = {"errorFlag": True, "errorString": errStr}
    return response


def GetFaultLog(root, indexList=[], indexRange=(0, 0), verbose=False):
    return GetEventLog(
        root, "faultEventIndex", "faultEvents", indexList, indexRange, verbose
    )


def GetFoldLog(root, indexList=[], indexRange=(0, 0), verbose=False):
    return GetEventLog(
        root, "foldEventIndex", "foldEvents", indexList, indexRange, verbose
    )


def GetFoliationLog(root, indexList=[], indexRange=(0, 0), verbose=False):
    return GetEventLog(
        root, "foliationEventIndex", "foliationEvents", indexList, indexRange, verbose
    )


def GetDiscontinuityLog(root, indexList=[], indexRange=(0, 0), verbose=False):
    return GetEventLog(
        root,
        "discontinuityEventIndex",
        "discontinuityEvents",
        indexList,
        indexRange,
        verbose,
    )


# Set stratigraphic log
def SetStratigraphicLog(root, data, append=False, verbose=False):
    """
    **SetStratigraphicLog** - Saves a list of strata in (formation,
    thickness) format into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: list of (formation, thickness)
        The data to save
    append: bool
        Flag of whether to append new data to existing log
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetExtractedInformationGroup(root)
    if resp["errorFlag"]:
        # Create Extracted Information Group as it doesn't exist
        eiGroup = root.createGroup("ExtractedInformation")
    else:
        eiGroup = resp["value"]

    resp = GetStratigraphicInformationGroup(root)
    if resp["errorFlag"]:
        siGroup = eiGroup.createGroup("StratigraphicInformation")
        siGroup.setncattr("index_MaxValid", -1)
        siGroup.createDimension("index", None)
        stratigraphicLayerType_t = siGroup.createCompoundType(
            LoopProjectFile.stratigraphicLayerType, "StratigraphicLayer"
        )
        siGroup.createVariable(
            "stratigraphicLayers",
            stratigraphicLayerType_t,
            ("index"),
            zlib=True,
            complevel=9,
        )
    else:
        siGroup = resp["value"]

    if siGroup:
        stratigraphicLayersLocation = siGroup.variables["stratigraphicLayers"]
        index = 0
        if append:
            index = siGroup.dimensions["index"].size
        for i in data:
            stratigraphicLayersLocation[index] = i
            index += 1
        siGroup.setncattr("index_MaxValid", index)
    else:
        errStr = "(ERROR) Failed to create stratigraphic log group for strata setting"
        if verbose:
            print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    return response


def GetStratigraphicLog(root, indexList=[], indexRange=(0, 0), verbose=False):
    response = {"errorFlag": False}
    resp = GetStratigraphicInformationGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        siGroup = resp["value"]
        data = []
        maxValidIndex = min(
            siGroup.dimensions["index"].size, siGroup.getncattr("index_MaxValid")
        )
        # Select all option
        if (
            indexList == []
            and len(indexRange) == 2
            and indexRange[0] == 0
            and indexRange[1] == 0
        ):
            # Select all
            for i in range(0, maxValidIndex):
                data.append((siGroup.variables.get("stratigraphicLayers")[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((siGroup.variables.get("stratigraphicLayers")[i]))
            response["value"] = data
        # Select based on indices range option
        elif (
            len(indexRange) == 2
            and indexRange[0] >= 0
            and indexRange[1] >= indexRange[0]
        ):
            for i in range(indexRange[0], indexRange[1]):
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((siGroup.variables.get("stratigraphicLayers")[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose:
                print(errStr)
            response = {"errorFlag": True, "errorString": errStr}
    return response


# Set drillhole log
def SetDrillholeLog(root, data, append=False, verbose=False):
    """
    **SetDrillholeLog** - Saves a list of drillholes in (collarId, name,
    location(X, Y, Z)) format into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: list of (collarId, name, location)
        The data to save
    append: bool
        Flag of whether to append new data to existing log
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetExtractedInformationGroup(root)
    if resp["errorFlag"]:
        # Create Extracted Information Group as it doesn't exist
        eiGroup = root.createGroup("ExtractedInformation")
    else:
        eiGroup = resp["value"]

    resp = GetDrillholeDescriptionGroup(root)
    if resp["errorFlag"]:
        diGroup = eiGroup.createGroup("DrillholeInformation")
        diGroup.setncattr("index_MaxValid", -1)
        diGroup.createDimension("index", None)
        drillholeDescriptionType_t = diGroup.createCompoundType(
            LoopProjectFile.drillholeDescriptionType, "DrillholeDescription"
        )
        diGroup.createVariable(
            "drillholeDescriptions",
            drillholeDescriptionType_t,
            ("index"),
            zlib=True,
            complevel=9,
        )
    else:
        diGroup = resp["value"]

    if diGroup:
        drillholeDescriptionsLocation = diGroup.variables["drillholeDescriptions"]
        index = 0
        if append:
            index = diGroup.dimensions["index"].size
        for i in data:
            drillholeDescriptionsLocation[index] = i
            index += 1
        diGroup.setncattr("index_MaxValid", index)
    else:
        errStr = "(ERROR) Failed to create drillhole description log group for setting drillhole data"
        if verbose:
            print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    return response


def GetDrillholeLog(root, indexList=[], indexRange=(0, 0), verbose=False):
    response = {"errorFlag": False}
    resp = GetDrillholeDescriptionGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        diGroup = resp["value"]
        data = []
        maxValidIndex = min(
            diGroup.dimensions["index"].size, diGroup.getncattr("index_MaxValid")
        )
        # Select all option
        if (
            indexList == []
            and len(indexRange) == 2
            and indexRange[0] == 0
            and indexRange[1] == 0
        ):
            # Select all
            for i in range(0, maxValidIndex):
                data.append((diGroup.variables.get("drillholeDescriptions")[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((diGroup.variables.get("drillholeDescriptions")[i]))
            response["value"] = data
        # Select based on indices range option
        elif (
            len(indexRange) == 2
            and indexRange[0] >= 0
            and indexRange[1] >= indexRange[0]
        ):
            for i in range(indexRange[0], indexRange[1]):
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((diGroup.variables.get("drillholeDescriptions")[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose:
                print(errStr)
            response = {"errorFlag": True, "errorString": errStr}
    return response


def SetEventRelationships(root, data, append=False, verbose=False):
    response = {"errorFlag": False}
    resp = GetExtractedInformationGroup(root)
    if resp["errorFlag"]:
        # Create  Extracted Information Group as it doesn't exist
        eiGroup = root.createGroup("ExtractedInformation")
    else:
        eiGroup = resp["value"]

    resp = GetEventRelationshipsGroup(root)
    if resp["errorFlag"]:
        erGroup = eiGroup.createGroup("EventRelationships")
        erGroup.setncattr("index_MaxValid", -1)
        erGroup.createDimension("index", None)
        eventRelationshipType_t = erGroup.createCompoundType(
            LoopProjectFile.eventRelationshipType, "EventRelationship"
        )
        erGroup.createVariable(
            "eventRelationships",
            eventRelationshipType_t,
            ("index"),
            zlib=True,
            complevel=9,
        )
    else:
        erGroup = resp["value"]

    if erGroup:
        eventRelationshipsLocation = erGroup.variables["eventRelationships"]
        index = 0
        if append:
            index = erGroup.dimensions["index"].size
        for i in data:
            eventRelationshipsLocation[index] = i
            index += 1
        erGroup.setncattr("index_MaxValid", index)
    else:
        errStr = "(ERROR) Failed to create event relationships group for event links"
        if verbose:
            print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    return response


def GetEventRelationships(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetEventRelationshipsGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        erGroup = resp["value"]
        maxValidIndex = min(
            erGroup.dimensions["index"].size, erGroup.getncattr("index_MaxValid")
        )
        data = []
        for i in range(0, maxValidIndex):
            data.append((erGroup.variables.get("eventRelationships")[i]))
        response["value"] = data
    return response
