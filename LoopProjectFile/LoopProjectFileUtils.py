# import netCDF4
import pandas
import os
import sys
import numpy
import LoopProjectFile


def GetGroup(node, groupName, verbose=False):
    """
    **GetGroup** - Gets the requested group node within the
    netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        A group node of a Loop Project File

    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a netCDF4 Group containing data for this project

    """
    if groupName in node.groups:
        return {"errorFlag": False, "value": node.groups.get(groupName)}
    else:
        errStr = "No " + groupName + " present in " + node.name + " for access request"
        if verbose:
            print(errStr)
        return {"errorFlag": True, "errorString": errStr}


def ElementFromDataframe(loopFilename, df, element, loopCompoundType):
    # print('Entered ElementFromDataframe')
    """
    **ElementFromCsv** - Imports one element of the loop project file
    from a csv file into the project file

    Parameters
    ----------
    loopFilename: string
        The filename of the loop project file
    importFilename: string
        The filename of the csv file containing the element data
    element: string
        The name of the element to extract
    loopCompoundType: numpy.compoundType
        The numpy data structure that the element is stored in

    Returns
    -------

    """
    if isinstance(df, pandas.DataFrame) is False:
        print("not a dataframedoes not exist")
        raise Exception("not a dataframedoes not exist")
    if not os.path.isfile(loopFilename):
        print(loopFilename, "does not exist. Try LoopProjectFile.CreateBasic first")
        raise Exception(
            f"{loopFilename} does not exist. Try LoopProjectFile.CreateBasic first"
        )
    if len(df.columns) != len(loopCompoundType):
        print("In dataframe columns do not match compound type")
        print(
            "  Dataframe:",
            df.columns,
            " does not match\n  Compound type:",
            loopCompoundType.names,
        )
        raise Exception("In dataframe columns do not match compound type")
    try:
        struct = LoopProjectFile.ConvertDataFrame(df, loopCompoundType)
        resp = LoopProjectFile.Set(loopFilename, element, data=struct)
        if resp["errorFlag"]:
            print(resp["errorString"])
            raise Exception(resp["errorString"])
    except Exception as e:
        return f"Error in ElementFromDataframe for {element}: {e}"


def ElementFromCsv(loopFilename, importFilename, element, loopCompoundType):
    """
    **ElementFromCsv** - Imports one element of the loop project file
    from a csv file into the project file

    Parameters
    ----------
    loopFilename: string
        The filename of the loop project file
    importFilename: string
        The filename of the csv file containing the element data
    element: string
        The name of the element to extract
    loopCompoundType: numpy.compoundType
        The numpy data structure that the element is stored in

    Returns
    -------

    """
    if not os.path.isfile(importFilename):
        print(importFilename, "does not exist")
        return
    if not os.path.isfile(loopFilename):
        print(loopFilename, "does not exist. Try LoopProjectFile.CreateBasic first")
        return
    try:
        df = pandas.read_csv(importFilename)
        ElementFromDataframe(loopFilename, df, element, loopCompoundType)
    except Exception as e:
        raise Exception(f"Error processing {importFilename}: {e}")


def FromCsv(loopFilename, importPath, overwrite=False):
    # print('Entered Fromcsv','loopFilename',loopFilename,'importPath',importPath)
    """
    **FromCsv** - Imports all elements of the loop project file
    from csv files into the project file

    Parameters
    ----------
    loopFilename: string
        The filename of the loop project file
    importPath: string
        The path to the csv files containing the element data
    overwrite: bool (default=False)
        A flag to indicate whether to overwrite a pre-existing loop
        project file

    Returns
    -------

    """
    # Check that filename exists and is a netCDF file
    if os.path.isfile(loopFilename):
        if overwrite:
            os.remove(loopFilename)
        else:
            print(loopFilename, "already exists and overwrite not set", file=sys.stderr)
            raise Exception("already exists and overwrite not set")

    importPath = importPath.replace("\\", "/")
    if importPath[-1] != "/" and importPath[-1] != "\\":
        importPath += "/"

    if not os.path.isdir(importPath):
        print("Import path", importPath, "does not exist", file=sys.stderr)
        raise Exception(f"Import path {importPath} does not exist")

    # Create the basic loop project file
    print("Creating", loopFilename)
    LoopProjectFile.CreateBasic(loopFilename)

    print("  Importing from", str(importPath) + "extents.csv", "into project file")
    if not os.path.isfile(importPath + "extents.csv"):
        print(str(importPath) + "extents.csv", "does not exist")
        raise Exception("extents.csv is required")
    else:
        print(importPath + "extents.csv", file=sys.stderr)
        df = pandas.read_csv(str(importPath) + "extents.csv")
        extents = {}
        extents["geodesic"] = list(df.values[0][0:4])
        extents["utm"] = list(df.values[0][4:10])
        extents["depth"] = list(df.values[0][10:12])
        extents["spacing"] = list(df.values[0][12:15])
        LoopProjectFile.Set(loopFilename, "extents", **extents)

    # Import from various csvs
    # try:
    print("  Importing from", str(importPath) + "contacts.csv", "into project file")
    ElementFromCsv(
        loopFilename,
        importPath + "contacts.csv",
        "contacts",
        LoopProjectFile.contactObservationType,
    )

    print("  Importing from", str(importPath) + "faultLog.csv", "into project file")
    ElementFromCsv(
        loopFilename,
        importPath + "faultLog.csv",
        "faultLog",
        LoopProjectFile.faultEventType,
    )
    print("  Importing from", str(importPath) + "faultObs.csv", "into project file")
    ElementFromCsv(
        loopFilename,
        importPath + "faultObs.csv",
        "faultObservations",
        LoopProjectFile.faultObservationType,
    )

    print("  Importing from", str(importPath) + "foldLog.csv", "into project file")
    ElementFromCsv(
        loopFilename,
        importPath + "foldLog.csv",
        "foldLog",
        LoopProjectFile.foldEventType,
    )
    print("  Importing from", str(importPath) + "foldObs.csv", "into project file")
    ElementFromCsv(
        loopFilename,
        importPath + "foldObs.csv",
        "foldObservations",
        LoopProjectFile.foldObservationType,
    )

    print("  Importing from", str(importPath) + "foliationLog.csv", "into project file")
    ElementFromCsv(
        loopFilename,
        importPath + "foliationLog.csv",
        "foliationLog",
        LoopProjectFile.foliationEventType,
    )

    print("  Importing from", str(importPath) + "foliationObs.csv", "into project file")
    ElementFromCsv(
        loopFilename,
        importPath + "foliationObs.csv",
        "foliationObservations",
        LoopProjectFile.foliationObservationType,
    )

    print(
        "  Importing from",
        str(importPath) + "discontinuityLog.csv",
        "into project file",
    )
    ElementFromCsv(
        loopFilename,
        importPath + "discontinuityLog.csv",
        "discontinuityLog",
        LoopProjectFile.discontinuityEventType,
    )

    print(
        "  Importing from",
        str(importPath) + "discontinuityObs.csv",
        "into project file",
    )
    ElementFromCsv(
        loopFilename,
        importPath + "discontinuityObs.csv",
        "discontinuityObservations",
        LoopProjectFile.discontinuityObservationType,
    )

    print(
        "  Importing from",
        str(importPath) + "stratigraphicLog.csv",
        "into project file",
    )
    ElementFromCsv(
        loopFilename,
        importPath + "stratigraphicLog.csv",
        "stratigraphicLog",
        LoopProjectFile.stratigraphicLayerType,
    )

    print(
        "  Importing from",
        str(importPath) + "stratigraphicObs.csv",
        "into project file",
    )
    ElementFromCsv(
        loopFilename,
        importPath + "stratigraphicObs.csv",
        "stratigraphicObservations",
        LoopProjectFile.stratigraphicObservationType,
    )

    print("  Importing from", str(importPath) + "eventRel.csv", "into project file")
    ElementFromCsv(
        loopFilename,
        importPath + "eventRel.csv",
        "eventRelationships",
        LoopProjectFile.eventRelationshipType,
    )
    return "All CSV files processed successfully"


def ElementToDataframe(loopFilename, element, loopCompoundType):
    """
    **ElementToCsv** - Exports one element of the loop project file
    to a csv file outputFilename

    Parameters
    ----------
    loopFilename: string
        The filename of the loop project file
    element: string
        The name of the element to extract
    loopCompoundType: numpy.compoundType
        The numpy data structure that the element is stored in

    Returns
    -------

    """
    resp = LoopProjectFile.Get(loopFilename, element)
    if resp["errorFlag"]:
        print(resp["errorString"])
        return None
    else:
        columns = list(loopCompoundType.names)
        attr = resp.get("attributes",{})

        df = pandas.DataFrame.from_records(resp["value"], columns=columns)

        for name in columns:
            if type(loopCompoundType[name]) is not numpy.dtypes.VoidDType:
                df[name] = df[name].astype(loopCompoundType[name])
        df = df.map(lambda x: x.decode() if isinstance(x, bytes) else x)
        if "headers" in attr:
            if len(attr["headers"]) != len(columns):
                print("Number of headers does not match number of columns")
            else:
                df = df.rename(columns=dict(zip(columns,attr["headers"])))
        if "ncols" in attr:
            df = df.iloc[:, : attr["ncols"]]
        # df.set_index(columns[0], inplace=True)
        return df  # .to_csv(outputFilename)


def ElementToCsv(loopFilename, outputFilename, element, loopCompoundType):
    """
    **ElementToCsv** - Exports one element of the loop project file
    to a csv file outputFilename

    Parameters
    ----------
    loopFilename: string
        The filename of the loop project file
    outputFilename: string
        The filename of the csv file which will contain the element data
    element: string
        The name of the element to extract
    loopCompoundType: numpy.compoundType
        The numpy data structure that the element is stored in

    Returns
    -------

    """
    df = ElementToDataframe(loopFilename, element, loopCompoundType)
    if df:
        df.to_csv(outputFilename)


def ToCsv(loopFilename, outputPath):
    """
    **ToCsv** - Exports all elements of the loop project file
    to csv files in the outputPath directory

    Parameters
    ----------
    loopFilename: string
        The filename of the loop project file
    outputPath: string
        The path to where the csv files containing the element data will
        be exported

    Returns
    -------

    """
    # Check that filename exists
    if not os.path.isfile(loopFilename):
        print(loopFilename, "does not exist")
        return

    outputPath = outputPath.replace("\\", "/")
    if outputPath[-1] != "/" and outputPath[-1] != "\\":
        outputPath += "/"

    if not os.path.isdir(outputPath):
        print("Output Path", outputPath, "does not exist. Creating now.")
        os.mkdir(outputPath)

    # Extract and print version
    print(loopFilename, ":")
    resp = LoopProjectFile.Get(loopFilename, "version")
    if resp["errorFlag"]:
        print(loopFilename, "is not a loop project file")
        return
    print("  Exporting extents into", str(outputPath) + "extents.csv")
    resp = LoopProjectFile.Get(loopFilename, "extents")
    if resp["errorFlag"]:
        print(resp["errorString"])
        return
    else:
        utmNorthSouth = "N" if not resp["value"]["utm"][0] else "S"
        print("  Extents:")
        print("    utm zone:", str(resp["value"]["utm"][0]) + utmNorthSouth)
        print("    easting: ", resp["value"]["utm"][2], "-", resp["value"]["utm"][3])
        print("    northing:", resp["value"]["utm"][4], "-", resp["value"]["utm"][5])
        print("    altitude:", resp["value"]["depth"][0], "-", resp["value"]["depth"][1])
        columns = [
            "minLong",
            "maxLong",
            "minLat",
            "maxLat",
            "utmZone",
            "isUtmZoneNorth",
            "minEasting",
            "maxEasting",
            "minNorthing",
            "maxNorthing",
            "lowerBound",
            "upperBound",
            "spacingEastWest",
            "spacingNorthSouth",
            "spacingDepth",
        ]
        df = pandas.DataFrame(columns=columns)
        df.loc[0] = list(
            resp["value"]["geodesic"]
            + resp["value"]["utm"]
            + resp["value"]["depth"]
            + resp["value"]["spacing"]
        )
        df.set_index(columns[0], inplace=True)
        df.to_csv(str(outputPath) + "extents.csv")

    # Extract each element into separate csv files
    print("  Exporting contacts into", str(outputPath) + "contacts.csv")
    ElementToCsv(
        loopFilename,
        outputPath + "contacts.csv",
        "contacts",
        LoopProjectFile.contactObservationType,
    )

    print("  Exporting fault event log into", str(outputPath) + "faultLog.csv")
    ElementToCsv(
        loopFilename,
        outputPath + "faultLog.csv",
        "faultLog",
        LoopProjectFile.faultEventType,
    )
    print("  Exporting fault observations into", str(outputPath) + "faultObs.csv")
    ElementToCsv(
        loopFilename,
        outputPath + "faultObs.csv",
        "faultObservations",
        LoopProjectFile.faultObservationType,
    )

    print("  Exporting fold event log into", str(outputPath) + "foldLog.csv")
    ElementToCsv(
        loopFilename,
        outputPath + "foldLog.csv",
        "foldLog",
        LoopProjectFile.foldEventType,
    )
    print("  Exporting fold observations into", str(outputPath) + "foldObs.csv")
    ElementToCsv(
        loopFilename,
        outputPath + "foldObs.csv",
        "foldObservations",
        LoopProjectFile.foldObservationType,
    )

    print("  Exporting foliation event log into", str(outputPath) + "foliationLog.csv")
    ElementToCsv(
        loopFilename,
        outputPath + "foliationLog.csv",
        "foliationLog",
        LoopProjectFile.foliationEventType,
    )
    print("  Exporting foliation observations into", str(outputPath) + "foliationObs.csv")
    ElementToCsv(
        loopFilename,
        outputPath + "foliationObs.csv",
        "foliationObservations",
        LoopProjectFile.foliationObservationType,
    )

    print(
        "  Exporting discontinuity event log into",
        str(outputPath) + "discontinuityLog.csv",
    )
    ElementToCsv(
        loopFilename,
        outputPath + "discontinuityLog.csv",
        "discontinuityLog",
        LoopProjectFile.discontinuityEventType,
    )
    print(
        "  Exporting discontinuity observations into",
        str(outputPath) + "discontinuityObs.csv",
    )
    ElementToCsv(
        loopFilename,
        outputPath + "discontinuityObs.csv",
        "discontinuityObservations",
        LoopProjectFile.discontinuityObservationType,
    )

    print(
        "  Exporting stratigraphic event log into",
        str(outputPath) + "stratigraphicLog.csv",
    )
    ElementToCsv(
        loopFilename,
        outputPath + "stratigraphicLog.csv",
        "stratigraphicLog",
        LoopProjectFile.stratigraphicLayerType,
    )
    print(
        "  Exporting stratigraphic observations into",
        str(outputPath) + "stratigraphicObs.csv",
    )
    ElementToCsv(
        loopFilename,
        outputPath + "stratigraphicObs.csv",
        "stratigraphicObservations",
        LoopProjectFile.stratigraphicObservationType,
    )

    print("  Exporting event relationships into", str(outputPath) + "eventRel.csv")
    ElementToCsv(
        loopFilename,
        outputPath + "eventRel.csv",
        "eventRelationships",
        LoopProjectFile.eventRelationshipType,
    )


def handleLoopProjectFile(file, shared_path="/shared"):
    if file:
        filename = file.filename
        if not filename.endswith(".loop3d"):
            filename += ".loop3d"
        filepath = os.path.join(shared_path, filename)
        if os.path.exists(filepath):
            raise Exception(f"File {filename} already exists in the shared path.")
        file.save(filepath)
        if not LoopProjectFile.CheckFileValid(filepath):
            os.remove(filepath)
            raise Exception("Uploaded file is not a valid LoopProjectFile.")
        return
    else:
        raise Exception("No file was provided for upload.")


def handleCSVlist(files, loopFilename, shared_path="/shared"):
    if not loopFilename:
        raise Exception("loopFilename is required")
    if not files:
        raise Exception("No CSV files provided")

    loop_file_path = os.path.join(shared_path, loopFilename)
    saved_files = []

    for file_storage in files.getlist("file"):
        if file_storage and file_storage.filename.endswith(".csv"):
            filepath = os.path.join(shared_path, file_storage.filename)
            file_storage.save(filepath)
            saved_files.append(filepath)

    try:
        FromCsv(loop_file_path, shared_path)
    except Exception as conversion_error:
        for csv_file in saved_files:
            try:
                os.remove(os.path.join(shared_path, csv_file))
            except Exception as e:
                print(f"Failed to delete CSV file {csv_file}: {e}")
        if os.path.exists(loop_file_path):
            try:
                os.remove(loop_file_path)
            except Exception as e:
                print(f"Failed to delete project file {loop_file_path}: {e}")
        raise conversion_error
    else:
        for csv_file in saved_files:
            try:
                os.remove(os.path.join(shared_path, csv_file))
            except Exception as e:
                print(f"Failed to delete CSV file {csv_file}: {e}")

    return "success", f"{loopFilename} is created and saved successfully"

def map_colors_to_contacts(contacts: pandas.DataFrame, stratigraphicLog: pandas.DataFrame) -> pandas.DataFrame:
    contacts = contacts.merge(stratigraphicLog[['layerId', 'colour1Red', 'colour1Green','colour1Blue']], on='layerId',how='left')
    return contacts
