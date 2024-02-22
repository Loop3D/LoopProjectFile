# import netCDF4
import LoopProjectFile.Extents as Extents


# Check Structural Models valid if present
def CheckStructuralModelsValid(rootGroup, xyzGridSize=None, verbose=False):
    """
    **CheckStricturalModelsValid** - Checks for valid structural model group data
    given a netCDF root node

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    xyzGridSize: [int,int,int] or None
        The 3D grid shape to test data in this node to adhere to
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
    bool
        True if valid structural model data in project file, False otherwise.

    """
    valid = True
    if "StructuralModels" in rootGroup.groups:
        if verbose:
            print("  Structural Models Group Present")
        smGroup = rootGroup.groups.get("StructuralModels")
        #        if verbose: print(smGroup)
        if (
            "easting" in smGroup.ncattrs()
            and "northing" in smGroup.ncattrs()
            and "depth" in smGroup.ncattrs()
        ):
            if xyzGridSize is not None:
                # Check gridSize from extents matches models sizes
                smGridSize = [
                    smGroup.dimensions["easting"].size,
                    smGroup.dimensions["northing"].size,
                    smGroup.dimensions["depth"].size,
                ]
                if smGridSize != xyzGridSize:
                    print(
                        "(INVALID) Extents grid size and Structural Models Grid Size do NOT match"
                    )
                    print("(INVALID) Extents Grid Size :           ", xyzGridSize)
                    print("(INVALID) Structural Models Grid Size : ", smGridSize)
                    valid = False
                else:
                    if verbose:
                        print("  Structural Models grid size adheres to extents")
        else:
            if verbose:
                print("No structural models extents in project file")
    else:
        if verbose:
            print("No Structural Models Group Present")
    return valid


# Get Structural Models group if present
def GetStructuralModelsGroup(rootGroup, verbose=False):
    """
    **GetStructuralModelsGroup** - Gets the stuctural models group node within the
    netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File

    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a netCDF4 Group containing all the structural models

    """
    if "StructuralModels" in rootGroup.groups:
        smGroup = rootGroup.groups.get("StructuralModels")
        return {"errorFlag": False, "value": smGroup}
    else:
        errStr = "No Structural Models Group Present on access request"
        if verbose:
            print(errStr)
        return {"errorFlag": True, "errorString": errStr}


# Extract structural model indexed by parameter
def GetStructuralModel(root, verbose=False, index=0):
    """
    **GetStructuralModel** - Extracts the stuctural model indicated by index from
    the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File

    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a double[int:int:int] which is scalar field of the structural
        model

    """
    response = {"errorFlag": False}
    resp = GetStructuralModelsGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        smGroup = resp["value"]
        # Check data exists at the specified index value
        # Also checking for back indexing or out-of-bounds access
        if smGroup.dimensions.get("index") is None:
            response = {
                "errorFlag": True,
                "errorString": "(ERROR) There are no structural models to get",
            }
            if verbose:
                print(response["errorString"])
        elif smGroup.dimensions["index"].size < index or index < 0:
            response = {
                "errorFlag": True,
                "errorString": "(ERROR) The requested index "
                + str(index)
                + " does not exist",
            }
            if verbose:
                print(response["errorString"])
        else:
            data = smGroup.variables.get("data")[:, :, :, index].data
            if verbose:
                print("The shape of the structuralModel is", data.shape)
            response["value"] = data
    return response


# Set structural model (with dimension checking)
def SetStructuralModel(root, data, index=0, verbose=False):
    """
    **SetStructuralModel** - Saves a 3D scalar representation of a structural
    geological model into the netCDF Loop Project File at specified index

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: double[int,int,int]
        The scalar data to save
    index: int
        The index of this data
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    xyzGridSize = [0, 0, 0]
    Extents.CheckExtentsValid(root, xyzGridSize, verbose)
    resp = GetStructuralModelsGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        smGroup = root.createGroup("StructuralModels")
        smGroup.createDimension("easting", xyzGridSize[0])
        smGroup.createDimension("northing", xyzGridSize[1])
        smGroup.createDimension("depth", xyzGridSize[2])
        smGroup.createDimension("index", None)
        smGroup.createVariable(
            "data",
            "f4",
            ("easting", "northing", "depth", "index"),
            zlib=True,
            complevel=9,
            fill_value=0,
        )
        smGroup.createVariable(
            "minVal", "f4", ("index"), zlib=True, complevel=9, fill_value=0
        )
        smGroup.createVariable(
            "maxVal", "f4", ("index"), zlib=True, complevel=9, fill_value=0
        )
        smGroup.createVariable(
            "valid", "S1", ("index"), zlib=True, complevel=9, fill_value=0
        )
    else:
        smGroup = resp["value"]
    if smGroup:
        # Do dimension checking between incoming data and existing netCDF data shape
        dataGridSize = list(data.shape)
        if dataGridSize != xyzGridSize:
            errStr = (
                "(ERROR) Structural Model data shape does not match extents of project"
            )
            print(errStr)
            response = {"errorFlag": True, "errorString": errStr}
        else:
            # smGroup.variables('data')[:, :, :, index] = data
            if "index" not in smGroup.dimensions.keys():
                smGroup.createDimension("easting", xyzGridSize[0])
                smGroup.createDimension("northing", xyzGridSize[1])
                smGroup.createDimension("depth", xyzGridSize[2])
                smGroup.createDimension("index", None)
                smGroup.createVariable(
                    "data",
                    "f4",
                    ("easting", "northing", "depth", "index"),
                    zlib=True,
                    complevel=9,
                    fill_value=0,
                )
                smGroup.createVariable(
                    "minVal", "f4", ("index"), zlib=True, complevel=9, fill_value=0
                )
                smGroup.createVariable(
                    "maxVal", "f4", ("index"), zlib=True, complevel=9, fill_value=0
                )
                smGroup.createVariable(
                    "valid", "S1", ("index"), zlib=True, complevel=9, fill_value=0
                )
            dataLocation = smGroup.variables["data"]
            dataLocation[:, :, :, index] = data
            minValLocation = smGroup.variables["minVal"]
            minValLocation[index] = data.min()
            maxValLocation = smGroup.variables["maxVal"]
            maxValLocation[index] = data.max()
            validLocation = smGroup.variables["valid"]
            validLocation[index] = 1
    return response


# Set data collection (loopStructural) configuration settings
def SetConfiguration(root, data, verbose=False):
    """
    **SetConfiguration** - Saves the settings for the loop structural step

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    data: dictionary {str:str,...}
        A dictionary with the loop structural settings
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
       dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    resp = GetStructuralModelsGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        smGroup = root.createGroup("StructuralModels")
    else:
        smGroup = resp["value"]

    if data.contains("foliationInterpolator"):
        smGroup.foliationInterpolator = data.foliationInterpolator
    if data.contains("foliationNumElements"):
        smGroup.foliationNumElements = data.foliationNumElements
    if data.contains("foliationBuffer"):
        smGroup.foliationBuffer = data.foliationBuffer
    if data.contains("foliationSolver"):
        smGroup.foliationSolver = data.foliationSolver
    if data.contains("foliationDamp"):
        smGroup.foliationDamp = data.foliationDamp
    if data.contains("faultInterpolator"):
        smGroup.faultInterpolator = data.faultInterpolator
    if data.contains("faultNumElements"):
        smGroup.faultNumElements = data.faultNumElements
    if data.contains("faultDataRegion"):
        smGroup.faultDataRegion = data.faultDataRegion
    if data.contains("faultSolver"):
        smGroup.faultSolver = data.faultSolver
    if data.contains("faultCpw"):
        smGroup.faultCpw = data.faultCpw
    if data.contains("faultNpw"):
        smGroup.faultNpw = data.faultNpw
    return response


# Extract data collection (loopStructural) configuration settings
def GetConfiguration(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetStructuralModelsGroup(root)
    if resp["errorFlag"]:
        response = resp
    else:
        smGroup = resp["value"]
        foliationData = {}
        if "foliationInterpolator" in smGroup.ncattrs():
            foliationData["interpolatortype"] = smGroup.foliationInterpolator
        if "foliationNumElements" in smGroup.ncattrs():
            foliationData["nelements"] = smGroup.foliationNumElements
        if "foliationBuffer" in smGroup.ncattrs():
            foliationData["buffer"] = smGroup.foliationBuffer
        if "foliationSolver" in smGroup.ncattrs():
            foliationData["solver"] = smGroup.foliationSolver
        if "foliationDamp" in smGroup.ncattrs():
            foliationData["damp"] = smGroup.foliationDamp
        faultData = {}
        if "faultInterpolator" in smGroup.ncattrs():
            foliationData["interpolatortype"] = smGroup.faultInterpolator
        if "faultNumElements" in smGroup.ncattrs():
            foliationData["nelements"] = smGroup.faultNumElements
        if "faultDataRegion" in smGroup.ncattrs():
            foliationData["data_region"] = smGroup.faultDataRegion
        if "faultCpw" in smGroup.ncattrs():
            foliationData["cpw"] = smGroup.faultCpw
        if "faultNpw" in smGroup.ncattrs():
            foliationData["npw"] = smGroup.faultNpw
        data = [foliationData, faultData]
        response["value"] = data
    return response


# Set default data collection (loopStructural) configuration settings
def SetDefaultConfiguration(root, verbose=False):
    response = {"errorFlag": False}
    resp = GetStructuralModelsGroup(root)
    if resp["errorFlag"]:
        # Create Structural Models Group and add data shape based on project extents
        smGroup = root.createGroup("StructuralModels")
    else:
        smGroup = resp["value"]

    smGroup.foliationInterpolator = "PLI"
    smGroup.foliationNumElements = 100000
    smGroup.foliationBuffer = 0.8
    smGroup.foliationSolver = "pyamg"
    smGroup.foliationDamp = 1
    smGroup.faultInterpolator = "FDI"
    smGroup.faultNumElements = 10000
    smGroup.faultDataRegion = 0.3
    smGroup.faultSolver = "pyamg"
    smGroup.faultCpw = 10
    smGroup.faultNpw = 10
    return response
