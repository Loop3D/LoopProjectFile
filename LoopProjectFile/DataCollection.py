# import netCDF4
import LoopProjectFile.LoopProjectFileUtils as LoopProjectFileUtils
import LoopProjectFile


# Check Data Collection valid if present
def CheckDataCollectionValid(rootGroup, verbose=False):
    """
    **CheckDataCollectionValid** - Checks for valid data collection group data
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
        True if valid data collection formatting in project file, False
        otherwise.

    """
    valid = True
    if "DataCollection" in rootGroup.groups:
        if verbose:
            print("  Data Collection Group Present")
        dcGroup = rootGroup.groups.get("DataCollection")
        if verbose:
            print(dcGroup)
    else:
        if verbose:
            print("No Data Collection Group Present")
    return valid


# Get Data Collection group if present
def GetDataCollectionGroup(rootGroup, verbose=False):
    return LoopProjectFileUtils.GetGroup(rootGroup, "DataCollection", verbose)


# Get Observations group if present
def GetObservationsGroup(rootGroup, verbose=False):
    resp = GetDataCollectionGroup(rootGroup, verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"], "Observations", verbose)


# Get Contacts group if present
def GetContactsGroup(rootGroup, verbose=False):
    resp = GetDataCollectionGroup(rootGroup, verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"], "Contacts", verbose)


# Get Drillhole group if present
def GetDrillholesGroup(rootGroup, verbose=False):
    resp = GetDataCollectionGroup(rootGroup, verbose)
    if resp["errorFlag"]:
        return resp
    else:
        return LoopProjectFileUtils.GetGroup(resp["value"], "Drillholes", verbose)


def CreateObservationGroup(dataCollectionGroup):
    obGroup = dataCollectionGroup.createGroup("Observations")
    obGroup.setncattr("faultObservationIndex_MaxValid", -1)
    obGroup.setncattr("foldObservationIndex_MaxValid", -1)
    obGroup.setncattr("foliationObservationIndex_MaxValid", -1)
    obGroup.setncattr("discontinuityObservationIndex_MaxValid", -1)
    obGroup.setncattr("stratigraphicObservationIndex_MaxValid", -1)
    obGroup.createDimension("faultObservationIndex", None)
    obGroup.createDimension("foldObservationIndex", None)
    obGroup.createDimension("foliationObservationIndex", None)
    obGroup.createDimension("discontinuityObservationIndex", None)
    obGroup.createDimension("stratigraphicObservationIndex", None)
    faultObservationType_t = obGroup.createCompoundType(
        LoopProjectFile.faultObservationType, "FaultObservation"
    )
    obGroup.createVariable(
        "faultObservations",
        faultObservationType_t,
        ("faultObservationIndex"),
        zlib=True,
        complevel=9,
    )
    foldObservationType_t = obGroup.createCompoundType(
        LoopProjectFile.foldObservationType, "FoldObservation"
    )
    obGroup.createVariable(
        "foldObservations",
        foldObservationType_t,
        ("foldObservationIndex"),
        zlib=True,
        complevel=9,
    )
    foliationObservationType_t = obGroup.createCompoundType(
        LoopProjectFile.foliationObservationType, "FoliationObservation"
    )
    obGroup.createVariable(
        "foliationObservations",
        foliationObservationType_t,
        ("foliationObservationIndex"),
        zlib=True,
        complevel=9,
    )
    discontinuityObservationType_t = obGroup.createCompoundType(
        LoopProjectFile.discontinuityObservationType, "DiscontinuityObservation"
    )
    obGroup.createVariable(
        "discontinuityObservations",
        discontinuityObservationType_t,
        ("discontinuityObservationIndex"),
        zlib=True,
        complevel=9,
    )
    stratigraphicObservationType_t = obGroup.createCompoundType(
        LoopProjectFile.stratigraphicObservationType, "StratigraphicObservation"
    )
    obGroup.createVariable(
        "stratigraphicObservations",
        stratigraphicObservationType_t,
        ("stratigraphicObservationIndex"),
        zlib=True,
        complevel=9,
    )
    return obGroup


def CreateDrillholeGroup(dataCollectionGroup):
    dhGroup = dataCollectionGroup.createGroup("Drillholes")
    dhGroup.setncattr("drillholeObservationIndex_MaxValid", -1)
    dhGroup.setncattr("drillholeSurveyIndex_MaxValid", -1)
    dhGroup.setncattr("drillholePropertyIndex_MaxValid", -1)
    dhGroup.createDimension("drillholeObservationIndex", None)
    dhGroup.createDimension("drillholeSurveyIndex", None)
    dhGroup.createDimension("drillholePropertyIndex", None)
    drillholeObservationType_t = dhGroup.createCompoundType(
        LoopProjectFile.drillholeObservationType, "DrillholeObservation"
    )
    dhGroup.createVariable(
        "drillholeObservations",
        drillholeObservationType_t,
        ("drillholeObservationIndex"),
        zlib=True,
        complevel=9,
    )
    drillholeSurveyType_t = dhGroup.createCompoundType(
        LoopProjectFile.drillholeSurveyType, "DrillholeSurvey"
    )
    dhGroup.createVariable(
        "drillholeSurveys",
        drillholeSurveyType_t,
        ("drillholeSurveyIndex"),
        zlib=True,
        complevel=9,
    )
    drillholePropertyType_t = dhGroup.createCompoundType(
        LoopProjectFile.drillholePropertyType, "DrillholeProperty"
    )
    dhGroup.createVariable(
        "drillholeProperties",
        drillholePropertyType_t,
        ("drillholePropertyIndex"),
        zlib=True,
        complevel=9,
    )
    return dhGroup


# Extract observations
def GetObservations(
    root,
    indexName,
    variableName,
    indexList=[],
    indexRange=(0, 0),
    keyword="",
    verbose=False,
):
    response = {"errorFlag": False}
    resp = GetObservationsGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        if verbose:
            print("Getting variable " + variableName)
        oGroup = resp["value"]
        data = []
        maxValidIndex = min(
            oGroup.dimensions[indexName].size, oGroup.getncattr(indexName + "_MaxValid")
        )
        # Select all option
        if (
            indexList == []
            and len(indexRange) == 2
            and indexRange[0] == 0
            and indexRange[1] == 0
            and keyword == ""
        ):
            if verbose:
                print("Getting all")
            # Create list of observations as:
            # ((easting, northing, altitude), dipdir, dip, formation, layer)
            for i in range(0, maxValidIndex):
                data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on keyword and list of indices option
        elif keyword != "" and indexList != []:
            if verbose:
                print("Getting keyword and index list")
            for i in indexList:
                if (
                    int(i) >= 0
                    and int(i) < maxValidIndex
                    and oGroup.variables.get(variableName)[i] == keyword
                ):
                    data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on keyword option
        elif keyword != "":
            if verbose:
                print("Getting keyword")
            for i in range(0, maxValidIndex):
                if oGroup.variables.get(variableName)[i] == keyword:
                    data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            if verbose:
                print("Getting index list")
            for i in indexList:
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on indices range option
        elif (
            len(indexRange) == 2
            and indexRange[0] >= 0
            and indexRange[1] >= indexRange[0]
        ):
            if verbose:
                print("Getting index range")
            for i in range(indexRange[0], indexRange[1]):
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((oGroup.variables.get(variableName)[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose:
                print(errStr)
            response = {"errorFlag": True, "errorString": errStr}
    return response


def GetFaultObservations(
    root, indexList=[], indexRange=(0, 0), keyword="", verbose=False
):
    return GetObservations(
        root,
        "faultObservationIndex",
        "faultObservations",
        indexList,
        indexRange,
        keyword,
        verbose,
    )


def GetFoldObservations(
    root, indexList=[], indexRange=(0, 0), keyword="", verbose=False
):
    return GetObservations(
        root,
        "foldObservationIndex",
        "foldObservations",
        indexList,
        indexRange,
        keyword,
        verbose,
    )


def GetFoliationObservations(
    root, indexList=[], indexRange=(0, 0), keyword="", verbose=False
):
    return GetObservations(
        root,
        "foliationObservationIndex",
        "foliationObservations",
        indexList,
        indexRange,
        keyword,
        verbose,
    )


def GetDiscontinuityObservations(
    root, indexList=[], indexRange=(0, 0), keyword="", verbose=False
):
    return GetObservations(
        root,
        "discontinuityObservationIndex",
        "discontinuityObservations",
        indexList,
        indexRange,
        keyword,
        verbose,
    )


def GetStratigraphicObservations(
    root, indexList=[], indexRange=(0, 0), keyword="", verbose=False
):
    return GetObservations(
        root,
        "stratigraphicObservationIndex",
        "stratigraphicObservations",
        indexList,
        indexRange,
        keyword,
        verbose,
    )


# Set observations
def SetObservations(root, data, indexName, variableName, append=False, verbose=False):
    """
    **SetObservations** - Saves a list of observations in ((easting, northing,
    altitude), dipdir, dip, layer) format into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: list of ((X, Y, Z), dipdir, dip, polarity, formation, layer)
        The data to save
    index: int
        The index of this data
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    resp = GetObservationsGroup(root)
    if resp["errorFlag"]:
        oGroup = CreateObservationGroup(dcGroup)
    else:
        oGroup = resp["value"]

    if oGroup:
        observationLocation = oGroup.variables[variableName]
        index = 0
        if append:
            index = oGroup.dimensions[indexName].size
        for i in data:
            observationLocation[index] = i
            index += 1
        oGroup.setncattr(indexName + "_MaxValid", index)
    else:
        errStr = "(ERROR) Failed to Create observations group for observations setting"
        if verbose:
            print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    return response


def SetFaultObservations(root, data, append=False, verbose=False):
    return SetObservations(
        root, data, "faultObservationIndex", "faultObservations", append, verbose
    )


def SetFoldObservations(root, data, append=False, verbose=False):
    return SetObservations(
        root, data, "foldObservationIndex", "foldObservations", append, verbose
    )


def SetFoliationObservations(root, data, append=False, verbose=False):
    return SetObservations(
        root,
        data,
        "foliationObservationIndex",
        "foliationObservations",
        append,
        verbose,
    )


def SetDiscontinuityObservations(root, data, append=False, verbose=False):
    return SetObservations(
        root,
        data,
        "discontinuityObservationIndex",
        "discontinuityObservations",
        append,
        verbose,
    )


def SetStratigraphicObservations(root, data, append=False, verbose=False):
    return SetObservations(
        root,
        data,
        "stratigraphicObservationIndex",
        "stratigraphicObservations",
        append,
        verbose,
    )


# Extract contacts
def GetContacts(root, indexList=[], indexRange=(0, 0), keyword="", verbose=False):
    response = {"errorFlag": False}
    # Note contacts use a different group node "Contacts" hence we cannot use GetObservations function
    resp = GetContactsGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        group = resp["value"]
        data = []
        maxValidIndex = min(
            group.dimensions["index"].size, group.getncattr("index_MaxValid")
        )
        # Select all option
        if (
            indexList == []
            and len(indexRange) == 2
            and indexRange[0] == 0
            and indexRange[1] == 0
            and keyword == ""
        ):
            # Create list of observations as:
            # ((easting, northing, altitude), dipdir, dip, formation, layer)
            for i in range(0, maxValidIndex):
                data.append((group.variables.get("contacts")[i]))
            response["value"] = data
        # Select based on keyword and list of indices option
        elif keyword != "" and indexList != []:
            for i in indexList:
                if (
                    int(i) >= 0
                    and int(i) < maxValidIndex
                    and group.variables.get("layer")[i] == keyword
                ):
                    data.append((group.variables.get("contacts")[i]))
            response["value"] = data
        # Select based on keyword option
        elif keyword != "":
            for i in range(0, maxValidIndex):
                if group.variables.get("layer")[i] == keyword:
                    data.append((group.variables.get("contacts")[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((group.variables.get("contacts")[i]))
            response["value"] = data
        # Select based on indices range option
        elif (
            len(indexRange) == 2
            and indexRange[0] >= 0
            and indexRange[1] >= indexRange[0]
        ):
            for i in range(indexRange[0], indexRange[1]):
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((group.variables.get("contacts")[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose:
                print(errStr)
            response = {"errorFlag": True, "errorString": errStr}
    return response


# Set contacts
def SetContacts(root, data, append=False, verbose=False):
    """
    **SetContacts** - Saves a list of contacts in ((easting, northing,
    altitude), formation) format into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: list of ((X, Y, Z), formation)
        The data to save
    index: int
        The index of this data
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    # Note contacts use a different group node "Contacts" hence we cannot use SetObservations function
    resp = GetContactsGroup(root)
    if resp["errorFlag"]:
        group = dcGroup.createGroup("Contacts")
        group.setncattr("index_MaxValid", -1)
        group.createDimension("index", None)
        contactObservationType_t = group.createCompoundType(
            LoopProjectFile.contactObservationType, "contactObservation"
        )
        group.createVariable(
            "contacts", contactObservationType_t, ("index"), zlib=True, complevel=9
        )
    else:
        group = resp["value"]

    if group:
        contactsLocation = group.variables["contacts"]
        index = 0
        if append:
            index = group.dimensions["index"].size
        for i in data:
            contactsLocation[index] = i
            index += 1
        group.setncattr("index_MaxValid", index)
    else:
        errStr = "(ERROR) Failed to Create contacts group for contact setting"
        if verbose:
            print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    return response


# Extract drillhole observaions
def GetDrillholeData(
    root,
    indexName,
    variableName,
    indexList=[],
    indexRange=(0, 0),
    keyword="",
    verbose=False,
):
    response = {"errorFlag": False}
    # Note contacts use a different group node "Contacts" hence we cannot use GetObservations function
    resp = GetDrillholesGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        group = resp["value"]
        data = []
        maxValidIndex = min(
            group.dimensions[indexName].size, group.getncattr(indexName + "_MaxValid")
        )
        # Select all option
        if (
            indexList == []
            and len(indexRange) == 2
            and indexRange[0] == 0
            and indexRange[1] == 0
            and keyword == ""
        ):
            # Create list of observations as:
            # ((easting, northing, altitude), dipdir, dip, formation, layer)
            for i in range(0, maxValidIndex):
                data.append((group.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on keyword and list of indices option
        elif keyword != "" and indexList != []:
            for i in indexList:
                if (
                    int(i) >= 0
                    and int(i) < maxValidIndex
                    and group.variables.get("layer")[i] == keyword
                ):
                    data.append((group.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on keyword option
        elif keyword != "":
            for i in range(0, maxValidIndex):
                if group.variables.get("layer")[i] == keyword:
                    data.append((group.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on list of indices option
        elif indexList != []:
            for i in indexList:
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((group.variables.get(variableName)[i]))
            response["value"] = data
        # Select based on indices range option
        elif (
            len(indexRange) == 2
            and indexRange[0] >= 0
            and indexRange[1] >= indexRange[0]
        ):
            for i in range(indexRange[0], indexRange[1]):
                if int(i) >= 0 and int(i) < maxValidIndex:
                    data.append((group.variables.get(variableName)[i]))
            response["value"] = data
        else:
            errStr = "Non-implemented filter option"
            if verbose:
                print(errStr)
            response = {"errorFlag": True, "errorString": errStr}
    return response


def GetDrillholeObservations(
    root, indexList=[], indexRange=(0, 0), keyword="", verbose=False
):
    return GetDrillholeData(
        root,
        "drillholeObservationIndex",
        "drillholeObservations",
        indexList,
        indexRange,
        keyword,
        verbose,
    )


def GetDrillholeSurveys(
    root, indexList=[], indexRange=(0, 0), keyword="", verbose=False
):
    return GetDrillholeData(
        root,
        "drillholeSurveyIndex",
        "drillholeSurveys",
        indexList,
        indexRange,
        keyword,
        verbose,
    )


def GetDrillholeProperties(
    root, indexList=[], indexRange=(0, 0), keyword="", verbose=False
):
    return GetDrillholeData(
        root,
        "drillholePropertyIndex",
        "drillholeProperties",
        indexList,
        indexRange,
        keyword,
        verbose,
    )


# Set drillhole observations
def SetDrillholeData(root, data, indexName, variableName, append=False, verbose=False):
    """
    **SetDrillholeObservations** - Saves a list of drillhole observaions in ((easting, northing,
    altitude), (easting, northing, altitude), formation, dip, dipDir) format into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: list of ((X, Y, Z), (X, Y, Z), formation, dip, dipDir)
        The data to save
    index: int
        The index of this data
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    # Note drillholes use a different group node "Drillholes" hence we cannot use SetObservations function
    resp = GetDrillholesGroup(root)
    if resp["errorFlag"]:
        group = CreateDrillholeGroup(dcGroup)
    else:
        group = resp["value"]

    if group:
        drillholeObservationsLocation = group.variables[variableName]
        index = 0
        if append:
            index = group.dimensions[indexName].size
        for i in data:
            drillholeObservationsLocation[index] = i
            index += 1
        group.setncattr(indexName + "_MaxValid", index)
    else:
        errStr = "(ERROR) Failed to Create drillhole group for drillhole setting"
        if verbose:
            print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    return response


def SetDrillholeObservations(root, data, append=False, verbose=False):
    return SetDrillholeData(
        root,
        data,
        "drillholeObservationIndex",
        "drillholeObservations",
        append,
        verbose,
    )


def SetDrillholeSurveys(root, data, append=False, verbose=False):
    return SetDrillholeData(
        root, data, "drillholeSurveyIndex", "drillholeSurveys", append, verbose
    )


def SetDrillholeProperties(root, data, append=False, verbose=False):
    return SetDrillholeData(
        root, data, "drillholePropertyIndex", "drillholeProperties", append, verbose
    )


# Extract data collection (map2loop) configuration settings
def GetConfiguration(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        dcGroup = resp["value"]
        data = {}
        if "quietMode" in dcGroup.ncattrs():
            data["quietMode"] = dcGroup.quietMode
        if "deposits" in dcGroup.ncattrs():
            data["deposits"] = dcGroup.deposits
        if "dtb" in dcGroup.ncattrs():
            data["dtb"] = dcGroup.dtb
        if "orientationDecimate" in dcGroup.ncattrs():
            data["orientationDecimate"] = dcGroup.orientationDecimate
        if "contactDecimate" in dcGroup.ncattrs():
            data["contactDecimate"] = dcGroup.contactDecimate
        if "intrusionMode" in dcGroup.ncattrs():
            data["intrusionMode"] = dcGroup.intrusionMode
        if "interpolationSpacing" in dcGroup.ncattrs():
            data["interpolationSpacing"] = dcGroup.interpolationSpacing
        if "misorientation" in dcGroup.ncattrs():
            data["misorientation"] = dcGroup.misorientation
        if "interpolationScheme" in dcGroup.ncattrs():
            data["interpolationScheme"] = dcGroup.interpolationScheme
        if "faultDecimate" in dcGroup.ncattrs():
            data["faultDecimate"] = dcGroup.faultDecimate
        if "minFaultLength" in dcGroup.ncattrs():
            data["minFaultLength"] = dcGroup.minFaultLength
        if "faultDip" in dcGroup.ncattrs():
            data["faultDip"] = dcGroup.faultDip
        if "plutonDip" in dcGroup.ncattrs():
            data["plutonDip"] = dcGroup.plutonDip
        if "plutonForm" in dcGroup.ncattrs():
            data["plutonForm"] = dcGroup.plutonForm
        if "distBuffer" in dcGroup.ncattrs():
            data["distBuffer"] = dcGroup.distBuffer
        if "contactDip" in dcGroup.ncattrs():
            data["contactDip"] = dcGroup.contactDip
        if "contactOrientationDecimate" in dcGroup.ncattrs():
            data["contactOrientationDecimate"] = dcGroup.contactOrientationDecimate
        if "nullScheme" in dcGroup.ncattrs():
            data["nullScheme"] = dcGroup.nullScheme
        if "thicknessBuffer" in dcGroup.ncattrs():
            data["thicknessBuffer"] = dcGroup.thicknessBuffer
        if "maxThicknessAllowed" in dcGroup.ncattrs():
            data["maxThicknessAllowed"] = dcGroup.maxThicknessAllowed
        if "foldDecimate" in dcGroup.ncattrs():
            data["foldDecimate"] = dcGroup.foldDecimate
        if "fatStep" in dcGroup.ncattrs():
            data["fatStep"] = dcGroup.fatStep
        if "closeDip" in dcGroup.ncattrs():
            data["closeDip"] = dcGroup.closeDip
        if "useInterpolations" in dcGroup.ncattrs():
            data["useInterpolations"] = dcGroup.useInterpolations
        if "useFat" in dcGroup.ncattrs():
            data["useFat"] = dcGroup.useFat
        response["value"] = data
    return response


# Set data collection (map2loop) configuration settings
def SetConfiguration(root, data, verbose=False):
    """
    **SetConfiguration** - Saves the settings for the data collection step

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: dictionary {str: str,...}
        A dictionary with the data colletion settings
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    if data.contains("quietMode"):
        dcGroup.quietMode = data.quietMode
    if data.contains("deposits"):
        dcGroup.deposits = data.deposits
    if data.contains("dtb"):
        dcGroup.dtb = data.dtb
    if data.contains("orientationDecimate"):
        dcGroup.orientationDecimate = data.orientationDecimate
    if data.contains("contactDecimate"):
        dcGroup.contactDecimate = data.contactDecimate
    if data.contains("intrusionMode"):
        dcGroup.intrusionMode = data.intrusionMode
    if data.contains("interpolationSpacing"):
        dcGroup.interpolationSpacing = data.interpolationSpacing
    if data.contains("misorientation"):
        dcGroup.misorientation = data.misorientation
    if data.contains("interpolationScheme"):
        dcGroup.interpolationScheme = data.interpolationScheme
    if data.contains("faultDecimate"):
        dcGroup.faultDecimate = data.faultDecimate
    if data.contains("minFaultLength"):
        dcGroup.minFaultLength = data.minFaultLength
    if data.contains("faultDip"):
        dcGroup.faultDip = data.faultDip
    if data.contains("plutonDip"):
        dcGroup.plutonDip = data.plutonDip
    if data.contains("plutonForm"):
        dcGroup.plutonForm = data.plutonForm
    if data.contains("distBuffer"):
        dcGroup.distBuffer = data.distBuffer
    if data.contains("contactDip"):
        dcGroup.contactDip = data.contactDip
    if data.contains("contactOrientationDecimate"):
        dcGroup.contactOrientationDecimate = data.contactOrientationDecimate
    if data.contains("nullScheme"):
        dcGroup.nullScheme = data.nullScheme
    if data.contains("thicknessBuffer"):
        dcGroup.thicknessBuffer = data.thicknessBuffer
    if data.contains("maxThicknessAllowed"):
        dcGroup.maxThicknessAllowed = data.maxThicknessAllowed
    if data.contains("foldDecimate"):
        dcGroup.foldDecimate = data.foldDecimate
    if data.contains("fatStep"):
        dcGroup.fatStep = data.fatStep
    if data.contains("closeDip"):
        dcGroup.closeDip = data.closeDip
    if data.contains("useInterpolations"):
        dcGroup.useInterpolations = data.useInterpolations
    if data.contains("useFat"):
        dcGroup.useFat = data.useFat
    return response


# Set default data collection (map2loop) configuration settings
def SetDefaultConfiguration(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    dcGroup.quietMode = 0
    dcGroup.deposits = "Fe,Cu,Au,NONE"
    dcGroup.dtb = ""
    dcGroup.orientationDecimate = 0
    dcGroup.contactDecimate = 5
    dcGroup.intrusionMode = 0
    dcGroup.interpolationSpacing = 500
    dcGroup.misorientation = 30
    dcGroup.interpolationScheme = "scipy_rbf"
    dcGroup.faultDecimate = 5
    dcGroup.minFaultLength = 5000
    dcGroup.faultDip = 90
    dcGroup.plutonDip = 45
    dcGroup.plutonForm = "domes"
    dcGroup.distBuffer = 10
    dcGroup.contactDip = -999
    dcGroup.contactOrientationDecimate = 5
    dcGroup.nullScheme = "null"
    dcGroup.thicknessBuffer = 5000
    dcGroup.maxThicknessAllowed = 10000
    dcGroup.foldDecimate = 5
    dcGroup.fatStep = 750
    dcGroup.closeDip = -999
    dcGroup.useInterpolations = 0
    dcGroup.useFat = 1
    return response


# Extract data collection (map2loop) source urls
def GetSources(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        dcGroup = resp["value"]
        data = {}
        if "structureUrl" in dcGroup.ncattrs():
            data["structureUrl"] = dcGroup.structureUrl
        if "geologyUrl" in dcGroup.ncattrs():
            data["geologyUrl"] = dcGroup.geologyUrl
        if "faultUrl" in dcGroup.ncattrs():
            data["faultUrl"] = dcGroup.faultUrl
        if "foldUrl" in dcGroup.ncattrs():
            data["foldUrl"] = dcGroup.foldUrl
        if "mindepUrl" in dcGroup.ncattrs():
            data["mindepUrl"] = dcGroup.mindepUrl
        if "metadataUrl" in dcGroup.ncattrs():
            data["metadataUrl"] = dcGroup.metadataUrl
        if "sourceTags" in dcGroup.ncattrs():
            data["sourceTags"] = dcGroup.sourceTags
        response["value"] = data
    return response


# Set data collection (map2loop) source urls
def SetSources(root, data, verbose=False):
    """
    **SetConfiguration** - Saves the settings for the data collection step

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: dictionary {str: str,...}
        A dictionary with the data colletion settings
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    if data.contains("structureUrl"):
        dcGroup.structureUrl = data.structureUrl
    if data.contains("geologyUrl"):
        dcGroup.geologyUrl = data.geologyUrl
    if data.contains("faultUrl"):
        dcGroup.faultUrl = data.faultUrl
    if data.contains("foldUrl"):
        dcGroup.foldUrl = data.foldUrl
    if data.contains("mindepUrl"):
        dcGroup.mindepUrl = data.mindepUrl
    if data.contains("metadataUrl"):
        dcGroup.metadataUrl = data.metadataUrl
    if data.contains("sourceTags"):
        dcGroup.sourceTags = data.sourceTags
    return response


# Create Default data collection (map2loop) source urls
def SetDefaultSources(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    dcGroup.structureUrl = ""
    dcGroup.geologyUrl = ""
    dcGroup.faultUrl = ""
    dcGroup.foldUrl = ""
    dcGroup.mindepUrl = ""
    dcGroup.metadataUrl = ""
    dcGroup.sourceTags = ""
    return response


# Extract data collection (map2loop) raw data
def GetRawSourceData(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        dcGroup = resp["value"]
        data = {}
        if "structureRawData" in dcGroup.ncattrs():
            data["structureRawData"] = dcGroup.structureRawData
        if "geologyRawData" in dcGroup.ncattrs():
            data["geologyRawData"] = dcGroup.geologyRawData
        if "faultRawData" in dcGroup.ncattrs():
            data["faultRawData"] = dcGroup.faultRawData
        if "foldRawData" in dcGroup.ncattrs():
            data["foldRawData"] = dcGroup.foldRawData
        response["value"] = data
    return response


# Set data collection raw data
def SetRawSourceData(root, data, verbose=False):
    """
    **SetConfiguration** - Saves the settings for the data collection step

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: dictionary {str: str,...}
        A dictionary with the data colletion settings
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    if data.contains("structureRawData"):
        dcGroup.structureRawData = data.structureRawData
    if data.contains("geologyRawData"):
        dcGroup.geologyRawData = data.geologyRawData
    if data.contains("faultRawData"):
        dcGroup.faultRawData = data.faultRawData
    if data.contains("foldRawData"):
        dcGroup.foldRawData = data.foldRawData
    return response


# Create blank data collection data
def SetDefaultRawSourceData(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetDataCollectionGroup(root)
    if resp["errorFlag"]:
        dcGroup = root.createGroup("DataCollection")
    else:
        dcGroup = resp["value"]

    dcGroup.structureRawData = ""
    dcGroup.geologyRawData = ""
    dcGroup.faultRawData = ""
    dcGroup.foldRawData = ""

    return response
