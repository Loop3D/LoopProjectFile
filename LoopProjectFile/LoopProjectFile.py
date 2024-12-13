# -*- coding: utf-8 -*-
"""

This module provides accessor functions to a Loop Project file as defined in
<url pending>.

Examples
--------
The main accessor functions are LoopProjectFile.Get and LoopProjectFile.Set
which are used as below:
    >>> import LoopProjectFile
    >>> response = LoopProjectFile.Get(`filename`, `element`)
    >>> if response["errorFlag"]: print(response["errorString"])
    >>> else: value = response["value"]
or
    >>> import LoopProjectFile
    >>> response = LoopProjectFile.Set(`filename`, `element`, `value`)
    >>> if response["errorFlag"]: print(response["errorString"])
    >>> else: print("Successful set")
where:
    *filename* - is the Loop Project File filename including pathing
    *element* - is the field of the file to get/set
    *value* - is the data to set

Returns
-------
The structure of each Get or Set function is a dict with "errorFlag" which
indicates a failure (on True) to get/set and then "errorString" in the case of
a failure or "value" in the case of a successful get call.

"""
import numpy
import pandas

import sys
import os
import enum

import netCDF4
import LoopProjectFile.version as version
import LoopProjectFile.Extents as Extents
import LoopProjectFile.StructuralModels as StructuralModels
import LoopProjectFile.DataCollection as DataCollection
import LoopProjectFile.ExtractedInformation as ExtractedInformation
import LoopProjectFile.GeophysicalModels as GeophysicalModels
import LoopProjectFile.ProbabilityModels as ProbabilityModels


class EventType(enum.IntEnum):
    INVALIDEVENT = (-1,)
    FAULTEVENT = (0,)
    FOLDEVENT = (1,)
    FOLIATIONSEVENT = (2,)
    DISCONTINUITYEVENT = (3,)
    STRATIGRAPHICLAYER = 4


class EventRelationshipType(enum.IntEnum):
    INVALIDTYPE = -1
    STRATA_STRATA = 0
    FAULT_STRATA = 1
    FAULT_FAULT_SPLAY = 2
    FAULT_FAULT_ABUT = 3
    FAULT_FAULT_OVERPRINT = 4


# Create a basic loop project file if no file already exists
def CreateBasic(filename):
    """
    **CreateBasic** - Creates a basic Loop Project File without extents or data
    (will not overright existing files)

    Parameters
    ----------
    filename: string
        The name of the file to create

    Returns
    -------
    dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    if os.path.isfile(filename):
        errStr = "File " + filename + " already exists"
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    else:
        rootGroup = netCDF4.Dataset(filename, "w", format="NETCDF4")
        response = version.SetVersion(rootGroup, version=version.LoopVersion())
        if not response["errorFlag"]:
            response = DataCollection.SetDefaultSources(rootGroup)
        if not response["errorFlag"]:
            response = DataCollection.SetDefaultRawSourceData(rootGroup)
        if not response["errorFlag"]:
            response = DataCollection.SetDefaultConfiguration(rootGroup)
        if not response["errorFlag"]:
            response = StructuralModels.SetDefaultConfiguration(rootGroup)
        rootGroup.close()
    return response


# Open project file with error checking for file existing and of netCDF format
def OpenProjectFile(filename, readOnly=True, verbose=False):
    """
    **OpenProjectFile** - Open a Loop Project File and checks it exists and is a
    netCDF formatted file

    Parameters
    ----------
    filename: string
        The name of the file to open
    readOnly: bool
        Whether to open the file without data entry or not (True - read only,
        False - writable)

    Returns
    -------
    dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    if verbose:
        print(f"Accessing file named: {filename}", file=sys.stderr)

    if not os.path.isfile(filename):
        errStr = f"File {filename} does not exist"
        print(errStr, file=sys.stderr)
        return {"errorFlag": True, "errorString": errStr}

    # Quick check to see if openable
    try:
        with open(filename, 'rb'):
            if (verbose):
                print(f"File {filename} opened successfully.", file=sys.stderr)
    except Exception as e:
        return {"errorFlag": True, "errorString": str(e)}

    readFlag = "r" if readOnly else "a"
    try:
        rootgrp = netCDF4.Dataset(filename, readFlag, format="NETCDF4")
        if rootgrp:
            if verbose:
                print(f"NetCDF data model type: {rootgrp.data_model}", file=sys.stderr)
            return {"errorFlag": False, "root": rootgrp}
    except Exception as e:
        print(f"Error occurred while opening file {filename}: {e}", file=sys.stderr)
        return {"errorFlag": True, "errorString": str(e)}


# Accessor Function handling opening and closing of file and calling
# appropriate setter function
def Set(filename, element, **kwargs):
    """
    **Set** - The core set function for interacting with a Loop Project File
    Can set with element and kwargs:
        version     : "version" = [Major, Minor, Sub]
        extents     : "geodesic" = [minLat, maxLat, minLong, maxLong]
                      "utm" = [utmZone, utmNorthSouth, minEasting, maxEasting, minNorthing, maxNorthing]
                      "depth" = [topDepth, bottomDepth]
                      "spacing" = [E/WSpacing, N/SSpacing, DepthSpacing]
                      "preference" = "utm" or "geodesic" (optional)
                      "epsg" = EPSG projection used
        strModel    : "data" = the 3D scalar field of structural data
                      "index" = the index of the dataset to save
                      "verbose" = optional extra console logging
        observations: "data" = the observations data in the following structure
                        a list of observations containing
                        ((easting, northing, altitude),   = the location (truple of doubles)
                        dipdir,                         = the dip direction (double)
                        dip,                            = the dip (double)
                        polarity,                       = the polarity (int)
                        formation,                      = the formation (string) (Hammerley,...)
                        layer)                          = the layer to associate with (string)("S0", "F1",...)
                      "verbose" = optional extra console logging

    Examples
    --------
    For setting version number:
    >>> LoopProjectFile.Set("test.loop3d", "version", version=[1,0,0])
      or
    >>> resp = LoopProjectFile.Set("test.loop3d", "version", version=[1,0,0])
    >>> if resp["errorFlag"]: print(resp["errorString"])

    For saving data:
    >>> LoopProjectFile.Set("test.loop3d", "strModel", data=dataset, index=0, verbose=True)
      or
    >>> resp = LoopProjectFile.Set("test.loop3d", "strModel", data=dataset, index=0, verbose=True)
    >>> if resp["errorFlag"]: print(resp["errorString"])

    For saving extents (in the middle of the pacific ocean):
    >>> LoopProjectFile.Set("test.loop3d", "extents", geodesic=[0,1,-180,-179], \
        utm=[1,1,10000000,9889363.77,833966.132,722587.169], depth=[-1000,-2000] \
        spacing=[1000,1000,10], preference="utm", epsg="EPSG:32753")

    For saving field observations:
    >>> data = ((easting, northing, altitude), dipdir, dip, polarity, formation, layer) * X rows
    >>> resp = LoopProjectFile.Set("test.loop3d", "observations", data=data, append=False, verbose=True)
    >>> if resp["errorFlag"]: print resp["errorString"])


    Parameters
    ----------
    filename: string
        The name of the file to save data to
    element: string
        The name of the element to save
    kwargs: dict
        A dictionary contains the elements to save

    Returns
    -------
    dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    if "verbose" in kwargs.keys():
        verbose = kwargs["verbose"]
    else:
        verbose = False

    fileResp = OpenProjectFile(filename, readOnly=False, verbose=verbose)
    if fileResp["errorFlag"]:
        response = fileResp
    else:
        root = fileResp["root"]
        try:
            if element == "version":
                response = version.SetVersion(root, **kwargs)
            elif element == "extents":
                response = Extents.SetExtents(root, **kwargs)
            elif element == "strModel":
                response = StructuralModels.SetStructuralModel(root, **kwargs)
            elif element == "faultObservations":
                response = DataCollection.SetFaultObservations(root, **kwargs)
            elif element == "faultObservationsAppend":
                response = DataCollection.SetFaultObservations(root, append=True, **kwargs)
            elif element == "foldObservations":
                response = DataCollection.SetFoldObservations(root, **kwargs)
            elif element == "foldObservationsAppend":
                response = DataCollection.SetFoldObservations(root, append=True, **kwargs)
            elif element == "foliationObservations":
                response = DataCollection.SetFoliationObservations(root, **kwargs)
            elif element == "foliationObservationsAppend":
                response = DataCollection.SetFoliationObservations(
                    root, append=True, **kwargs
                )
            elif element == "discontinuityObservations":
                response = DataCollection.SetDiscontinuityObservations(root, **kwargs)
            elif element == "discontinuityObservationsAppend":
                response = DataCollection.SetDiscontinuityObservations(
                    root, append=True, **kwargs
                )
            elif element == "stratigraphicObservations":
                response = DataCollection.SetStratigraphicObservations(root, **kwargs)
            elif element == "stratigraphicObservationsAppend":
                response = DataCollection.SetStratigraphicObservations(
                    root, append=True, **kwargs
                )
            elif element == "contacts":
                response = DataCollection.SetContacts(root, **kwargs)
            elif element == "contactsAppend":
                response = DataCollection.SetContacts(root, append=True, **kwargs)
            elif element == "drillholeObservations":
                response = DataCollection.SetDrillholeObservations(root, **kwargs)
            elif element == "drillholeObservationsAppend":
                response = DataCollection.SetDrillholeObservations(
                    root, append=True, **kwargs
                )
            elif element == "drillholeSurveys":
                response = DataCollection.SetDrillholeSurveys(root, **kwargs)
            elif element == "drillholeSurveysAppend":
                response = DataCollection.SetDrillholeSurveys(root, append=True, **kwargs)
            elif element == "drillholeProperties":
                response = DataCollection.SetDrillholeProperties(root, **kwargs)
            elif element == "drillholePropertiesAppend":
                response = DataCollection.SetDrillholeProperties(
                    root, append=True, **kwargs
                )
            elif element == "stratigraphicLog":
                response = ExtractedInformation.SetStratigraphicLog(root, **kwargs)
            elif element == "stratigraphicLogAppend":
                response = ExtractedInformation.SetStratigraphicLog(
                    root, append=True, **kwargs
                )
            elif element == "stratigraphicThicknesses":
                response = ExtractedInformation.SetStratigraphicThicknesses(root, **kwargs)
            elif element == "stratigraphicThicknessCalculatorLabels":
                response = ExtractedInformation.SetStratigraphicThicknessCalculatorLabels(root, **kwargs)
                
                
            elif element == "faultLog":
                response = ExtractedInformation.SetFaultLog(root, **kwargs)
            elif element == "faultLogAppend":
                response = ExtractedInformation.SetFaultLog(root, append=True, **kwargs)
            elif element == "foldLog":
                response = ExtractedInformation.SetFoldLog(root, **kwargs)
            elif element == "foldLogAppend":
                response = ExtractedInformation.SetFoldLog(root, append=True, **kwargs)
            elif element == "foliationLog":
                response = ExtractedInformation.SetFoliationLog(root, **kwargs)
            elif element == "foliationLogAppend":
                response = ExtractedInformation.SetFoliationLog(root, append=True, **kwargs)
            elif element == "discontinuityLog":
                response = ExtractedInformation.SetDiscontinuityLog(root, **kwargs)
            elif element == "discontinuityLogAppend":
                response = ExtractedInformation.SetDiscontinuityLog(
                    root, append=True, **kwargs
                )
            elif element == "drillholeLog":
                response = ExtractedInformation.SetDrillholeLog(root, **kwargs)
            elif element == "drillholeLogAppend":
                response = ExtractedInformation.SetDrillholeLog(root, append=True, **kwargs)
            elif element == "dataCollectionConfig":
                response = DataCollection.SetConfiguration(root, **kwargs)
            elif element == "dataCollectionSources":
                response = DataCollection.SetSources(root, **kwargs)
            elif element == "dataCollectionRawSourceData":
                response = DataCollection.SetRawSourceData(root, **kwargs)
            elif element == "eventRelationships":
                response = ExtractedInformation.SetEventRelationships(root, **kwargs)
            elif element == "structuralModelsConfig":
                response = StructuralModels.SetConfiguration(root, **kwargs)
            else:
                errStr = "(ERROR) Unknown element for Set function '" + element + "'"
                print(errStr)
                response = {"errorFlag": True, "errorString": errStr}
        finally:
            if (verbose):
                print(f"Closing file: {filename}",file=sys.stderr)
            root.close()
            if (verbose):
                print(f"{filename} closed successfully",file=sys.stderr)
    return response


# Accessor Function handling opening and closing of file and calling
# appropriate getter function
def Get(filename, element, **kwargs):
    """
    **Get** - The core getter function for interacting with a Loop Project File
    Can get data elements which returns a "value" of type:
        version     : "value" = [Major, Minor, Sub]
        extents     : "value" = {"geodesic" = [minLat, maxLat, minLong, maxLong]
                      "utm" = [utmZone, utmNorthSouth, minNorthing, maxNorthing, minEasting, maxEasting]
                      "depth" = [topDepth, bottomDepth]
                      "spacing" = [N/SSpacing, E/WSpacing, DepthSpacing]
                      "preference" = "utm" or "geodesic" (optional),
                      "epsg" = EPSG projection}
        strModel    : "value" = the 3D scalar field of structural data

    Examples
    --------
    For extracting the version number:
    >>> resp = LoopProjectFile.Get("test.loop3d", "version")
    >>> if resp["errorFlag"]: print(resp["errorString"])
    >>> else: version = resp["value"]

    For extracting structural model data:
    >>> resp = LoopProjectFile.Set("test.loop3d", "strModel", data=dataset, index=0)
    >>> if resp["errorFlag"]: print(resp["errorString"])
    >>> else: data = resp["value"]

    For extracting the extents:
    >>> resp = LoopProjectFile.Get("test.loop3d", "extents")
    >>> if resp["errorFlag"]: print(resp["errorString"])
    >>> else:
    >>>     data = resp["value"]
    >>>     geodesic = data["geodesic"]
    >>>     utm = data["utm"]
    >>>     depth = data["depth"]
    >>>     spacing = data["spacing"]
    >>>     epsg = data["epsg"]

    Parameters
    ----------
    filename: string
        The name of the file to load data from
    element: string
        The name of the element to extract
    kwargs: dict
        A dictionary contains the optional get values such as index of
        a structural model to extract

    Returns
    -------
    dict {"errorFlag", "errorString"/"value"}
        errorString exist and contains error message only when errorFlag is
        True otherwise the extracted value is in the "value" keyword

    """
    if "verbose" in kwargs.keys():
        verbose = kwargs["verbose"]
    else:
        verbose = False

    fileResp = OpenProjectFile(filename, readOnly=True, verbose=verbose)
    if fileResp["errorFlag"]:
        response = fileResp
    else:
        root = fileResp["root"]
        try:
            if element == "version":
                response = version.GetVersion(root)
            elif element == "extents":
                response = Extents.GetExtents(root)
            elif element == "strModel":
                response = StructuralModels.GetStructuralModel(root, **kwargs)
            elif element == "faultObservations":
                response = DataCollection.GetFaultObservations(root, **kwargs)
            elif element == "foldObservations":
                response = DataCollection.GetFoldObservations(root, **kwargs)
            elif element == "foliationObservations":
                response = DataCollection.GetFoliationObservations(root, **kwargs)
            elif element == "discontinuityObservations":
                response = DataCollection.GetDiscontinuityObservations(root, **kwargs)
            elif element == "stratigraphicObservations":
                response = DataCollection.GetStratigraphicObservations(root, **kwargs)
            elif element == "contacts":
                response = DataCollection.GetContacts(root, **kwargs)
            elif element == "drillholeObservations":
                response = DataCollection.GetDrillholeObservations(root, **kwargs)
            elif element == "drillholeSurveys":
                response = DataCollection.GetDrillholeSurveys(root, **kwargs)
            elif element == "drillholeProperties":
                response = DataCollection.GetDrillholeProperties(root, **kwargs)
            elif element == "stratigraphicLog":
                response = ExtractedInformation.GetStratigraphicLog(root, **kwargs)
            elif element == "stratigraphicThicknesses":
                response = ExtractedInformation.GetStratigraphicThicknesses(root, **kwargs)
            elif element == "stratigraphicThicknessCalculatorLabels":
                response = ExtractedInformation.GetStratigraphicThicknessCalculatorLabels(root, **kwargs)
            elif element == "faultLog":
                response = ExtractedInformation.GetFaultLog(root, **kwargs)
            elif element == "foldLog":
                response = ExtractedInformation.GetFoldLog(root, **kwargs)
            elif element == "foliationLog":
                response = ExtractedInformation.GetFoliationLog(root, **kwargs)
            elif element == "discontinuityLog":
                response = ExtractedInformation.GetDiscontinuityLog(root, **kwargs)
            elif element == "drillholeLog":
                response = ExtractedInformation.GetDrillholeLog(root, **kwargs)
            elif element == "dataCollectionConfig":
                response = DataCollection.GetConfiguration(root, **kwargs)
            elif element == "dataCollectionSources":
                response = DataCollection.GetSources(root, **kwargs)
            elif element == "dataCollectionRawSourceData":
                response = DataCollection.GetRawSourceData(root, **kwargs)
            elif element == "eventRelationships":
                response = ExtractedInformation.GetEventRelationships(root, **kwargs)
            elif element == "structuralModelsConfig":
                response = StructuralModels.GetConfiguration(root, **kwargs)
            else:
                errStr = "(ERROR) Unknown element for Get function '" + element + "'"
                print(errStr)
                response = {"errorFlag": True, "errorString": errStr}
        finally:
            if (verbose):
                print(f"Closing file: {filename}",file=sys.stderr)
            root.close()
            if (verbose):
                print(f"{filename} closed successfully",file=sys.stderr)
    return response


# Check which element are valid
def CheckValidElements(filename, verbose=False):
    """
    **CheckValidElements** - A function to check through a Loop Project File's
    elements to see whether there is information in each element

    Parameters
    ----------
    filename: string
        The name of the file to load data from
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
    dict or None
        A dictionary of all the elements with a boolean indicating if the
        element contains information

    """
    elements = {
        "version": False,
        "extents": False,
        "strModel": False,
        "faultObservations": False,
        "foldObservations": False,
        "foliationObservations": False,
        "discontinuityObservations": False,
        "stratigraphicObservations": False,
        "contacts": False,
        "drillholeObservations": False,
        "drillholeSurveys": False,
        "drillholeProperties": False,
        "stratigraphicLog": False,
        "stratigraphicThicknesses": False,
        "faultLog": False,
        "foldLog": False,
        "foliationLog": False,
        "discontinuityLog": False,
        "drillholeLog": False,
        "dataCollectionConfig": False,
        "dataCollectionSources": False,
        "dataCollectionRawSourceData": False,
        "eventRelationships": False,
        "structuralModelsConfig": False,
    }
    if not CheckFileIsLoopProjectFile(filename):
        if verbose:
            print(f"{filename} is not a valid loop project file")
        return None
    else:
        for element in elements:
            elements[element] = Get(filename, element)["errorFlag"]
        return elements


# Check full project structure
def CheckFileValid(filename, verbose=False):
    """
    **CheckFileValid** - A function to check through a Loop Project File to
    ensure that it is versioned, the extents are valid, and any data structures
    match the shape that the extents specify (comments on the structure are
    output to console when in verbose mode)

    Parameters
    ----------
    filename: string
        The name of the file to load data from
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
    bool
        A flag indicating whether the Loop Project File is valid

    """
    valid = True
    # Open project file
    fileResp = OpenProjectFile(filename, readOnly=True, verbose=verbose)
    if fileResp["errorFlag"]:
        valid = False
    else:
        rootgrp = fileResp["root"]

        xyzGridSize = [0, 0, 0]
        # Check for errors in project file
        valid = version.CheckVersionValid(rootgrp, verbose) and valid
        valid = Extents.CheckExtentsValid(rootgrp, xyzGridSize, verbose) and valid
        valid = DataCollection.CheckDataCollectionValid(rootgrp, verbose) and valid
        valid = (
            ExtractedInformation.CheckExtractedInformationValid(rootgrp, verbose)
            and valid
        )
        valid = (
            StructuralModels.CheckStructuralModelsValid(rootgrp, xyzGridSize, verbose)
            and valid
        )
        valid = (
            GeophysicalModels.CheckGeophysicalModelsValid(rootgrp, verbose) and valid
        )
        valid = ProbabilityModels.CheckProbabilityModelValid(rootgrp, verbose) and valid

        # Close and report
        rootgrp.close()

        if verbose is True:
            if valid:
                print("\nThis is a valid Loop Project File")
            else:
                print("\nThis Loop Project File is NOT valid")
    return valid


# Explicitly setup Compound Types used in the LoopProjectFile module
faultObservationType = numpy.dtype(
    [
        ("eventId", "<u4"),
        ("easting", "<f8"),
        ("northing", "<f8"),
        ("altitude", "<f8"),
        ("featureId", "<u4"),
        ("dipDir", "<f8"),
        ("dip", "<f8"),
        ("dipPolarity", "<f8"),
        ("val", "<f8"),
        ("displacement", "<f8"),
        ("posOnly", "u1"),
    ]
)

foldObservationType = numpy.dtype(
    [
        ("eventId", "<u4"),
        ("easting", "<f8"),
        ("northing", "<f8"),
        ("altitude", "<f8"),
        ("featureId", "<u4"),
        ("axisX", "<f8"),
        ("axisY", "<f8"),
        ("axisZ", "<f8"),
        ("foliation", "S120"),
        ("whatIsFolded", "S120"),
    ]
)

foliationObservationType = numpy.dtype(
    [
        ("eventId", "<u4"),
        ("easting", "<f8"),
        ("northing", "<f8"),
        ("altitude", "<f8"),
        ("featureId", "<u4"),
        ("dipDir", "<f8"),
        ("dip", "<f8"),
    ]
)

discontinuityObservationType = numpy.dtype(
    [
        ("eventId", "<u4"),
        ("easting", "<f8"),
        ("northing", "<f8"),
        ("altitude", "<f8"),
        ("featureId", "<u4"),
        ("dipDir", "<f8"),
        ("dip", "<f8"),
    ]
)

contactObservationType = numpy.dtype(
    [
        ("layerId", "<u4"),
        ("easting", "<f8"),
        ("northing", "<f8"),
        ("altitude", "<f8"),
        ("featureId", "<u4"),
    ]
)

stratigraphicObservationType = numpy.dtype(
    [
        ("layerId", "<u4"),
        ("easting", "<f8"),
        ("northing", "<f8"),
        ("altitude", "<f8"),
        ("dipDir", "<f8"),
        ("dip", "<f8"),
        ("dipPolarity", "<f8"),
        ("layer", "S120"),
    ]
)

faultEventType = numpy.dtype(
    [
        ("eventId", "<u4"),
        ("minAge", "<f8"),
        ("maxAge", "<f8"),
        ("name", "S120"),
        ("group", "S120"),
        ("supergroup", "S120"),
        ("enabled", "u1"),
        ("avgDisplacement", "<f8"),
        ("avgDownthrowDir", "<f8"),
        ("influenceDistance", "<f8"),
        ("verticalRadius", "<f8"),
        ("horizontalRadius", "<f8"),
        ("colour", "S7"),
        ("centreEasting", "<f8"),
        ("centreNorthing", "<f8"),
        ("centreAltitude", "<f8"),
        ("avgSlipDirEasting", "<f8"),
        ("avgSlipDirNorthing", "<f8"),
        ("avgSlipDirAltitude", "<f8"),
        ("avgNormalEasting", "<f8"),
        ("avgNormalNorthing", "<f8"),
        ("avgNormalAltitude", "<f8"),
    ]
)

foldEventType = numpy.dtype(
    [
        ("eventId", "<u4"),
        ("minAge", "<f8"),
        ("maxAge", "<f8"),
        ("name", "S120"),
        ("group", "S120"),
        ("supergroup", "S120"),
        ("enabled", "u1"),
        ("periodic", "u1"),
        ("wavelength", "<f8"),
        ("amplitude", "<f8"),
        ("asymmetry", "u1"),
        ("asymmetryShift", "<f8"),
        ("secondaryWavelength", "<f8"),
        ("secondaryAmplitude", "<f8"),
    ]
)

foliationEventType = numpy.dtype(
    [
        ("eventId", "<u4"),
        ("minAge", "<f8"),
        ("maxAge", "<f8"),
        ("name", "S120"),
        ("group", "S120"),
        ("supergroup", "S120"),
        ("enabled", "u1"),
        ("lowerScalarValue", "<f8"),
        ("upperScalarValue", "<f8"),
    ]
)

discontinuityEventType = numpy.dtype(
    [
        ("eventId", "<u4"),
        ("minAge", "<f8"),
        ("maxAge", "<f8"),
        ("name", "S120"),
        ("group", "S120"),
        ("supergroup", "S120"),
        ("enabled", "u1"),
        ("scalarValue", "<f8"),
    ]
)

stratigraphicLayerType = numpy.dtype(
    [
        ("layerId", "<u4"),
        ("minAge", "<f8"),
        ("maxAge", "<f8"),
        ("name", "S120"),
        ("group", "S120"),
        ("supergroup", "S120"),
        ("enabled", "u1"),
        ("ThicknessMean", "<f8"),
        ("ThicknessMedian", "<f8"),
        ("ThicknessStdDev", "<f8"),
        ("colour1Red", "u1"),
        ("colour1Green", "u1"),
        ("colour1Blue", "u1"),
        ("colour2Red", "u1"),
        ("colour2Green", "u1"),
        ("colour2Blue", "u1"),
    ]
)
stratigraphicThicknessType = numpy.dtype(
    [
        ('name', 'S120'),
        ('thickness1_mean', '<f8'),
        ('thickness1_median', '<f8'),
        ('thickness1_stddev', '<f8'),
        ('thickness2_mean', '<f8'),
        ('thickness2_median', '<f8'),
        ('thickness2_stddev', '<f8'),
        ('thickness3_mean', '<f8'),
        ('thickness3_median', '<f8'),
        ('thickness3_stddev', '<f8'),
        ('thickness4_mean', '<f8'),
        ('thickness4_median', '<f8'),
        ('thickness4_stddev', '<f8'),
        ('thickness5_mean', '<f8'),
        ('thickness5_median', '<f8'),
        ('thickness5_stddev', '<f8'),
    ]
)
thicknessCalculatorType = numpy.dtype([
    ("name1", "S120"),
    ("name2", "S120"),
    ("name3", "S120"),
    ("name4", "S120"),
    ("name5", "S120")
])

eventRelationshipType = numpy.dtype(
    [
        ("eventId1", "<u4"),
        ("eventId2", "<u4"),
        ("bidirectional", "u1"),
        ("angle", "<f8"),
        ("type", "<i4"),
    ]
)

drillholeDescriptionType = numpy.dtype(
    [
        ("collarId", "<u4"),
        ("holeName", "S120"),
        ("surfaceX", "<f8"),
        ("surfaceY", "<f8"),
        ("surfaceZ", "<f8"),
    ]
)

drillholePropertyType = numpy.dtype(
    [("collarId", "<u4"), ("propertyName", "S120"), ("propertyValue", "S80")]
)

drillholeObservationType = numpy.dtype(
    [
        ("collarId", "<u4"),
        ("fromX", "<f8"),
        ("fromY", "<f8"),
        ("fromZ", "<f8"),
        ("layerId", "<u4"),
        ("toX", "<f8"),
        ("toY", "<f8"),
        ("toZ", "<f8"),
        ("from", "<f8"),
        ("to", "<f8"),
        ("propertyCode", "S120"),
        ("property1", "S120"),
        ("property2", "S120"),
        ("unit", "S120"),
    ]
)

drillholeSurveyType = numpy.dtype(
    [
        ("collarId", "<u4"),
        ("depth", "<f8"),
        ("angle1", "<f8"),
        ("angle2", "<f8"),
        ("unit", "S120"),
    ]
)


def ConvertDataFrame(df, dtype):
    if isinstance(df, pandas.DataFrame):
        return numpy.array(df.to_records(index=False).tolist(), dtype=dtype)
    else:
        raise TypeError("Input is not a DataFrame")


def CheckFileIsLoopProjectFile(filename, verbose=False):
    """
    Check that the file is a valid Loop Project File
    """
    fileResp = OpenProjectFile(filename, readOnly=True, verbose=verbose)
    if fileResp["errorFlag"]:
        valid = False
        print("Project file is not a LoopProjectFile")
    else:
        rootgrp = fileResp["root"]
        rootgrp.close()
        valid = True
    return valid


def ConvertToDataFrame(data, loopCompoundType):
    columns = list(loopCompoundType.names)
    df = pandas.DataFrame.from_records(data, columns=columns)
    df = df.applymap(lambda x: x.decode() if isinstance(x, bytes) else x)
    return df
