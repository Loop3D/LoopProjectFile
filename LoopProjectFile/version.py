__version__ = "0.2.2"


# Current Loop Project File Version
def LoopVersion():
    """
    **LoopVersion** - hardcoded current version

    Returns
    -------
    [int,int,int]
        List of current version [Major,Minor,Sub]version

    """
    return list(map(int, (__version__.split("."))))


# Check version of Loop Project File is valid
def CheckVersionValid(rootGroup, verbose=False):
    """
    **CheckVersionValid** - Checks for valid version information given a netCDF
    root node

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
    bool
        True if valid version in project file, False otherwise.

    """
    if (
        rootGroup
        and "loopMajorVersion" in rootGroup.ncattrs()
        and "loopMinorVersion" in rootGroup.ncattrs()
        and "loopSubVersion" in rootGroup.ncattrs()
    ):
        version = [
            rootGroup.loopMajorVersion,
            rootGroup.loopMinorVersion,
            rootGroup.loopSubVersion,
        ]
        if verbose:
            print(
                "  Loop Project File version = "
                + str(version[0])
                + "."
                + str(version[1])
                + "."
                + str(version[2])
            )
        return True
    else:
        errStr = "(INVALID) No Version for this project file"
        print(errStr)
        return False


# Get the version of this loop project file in an array
def GetVersion(rootGroup):
    """
    **GetVersion** - Extracts the Loop Project File version data given a netCDF
    root node

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File

    Returns
    -------
    dict {"errorFlag","errorString"/"value"}
        value is a [int,int,int] of the version of this project file

    """
    if CheckVersionValid(rootGroup):
        return {
            "errorFlag": False,
            "value": list(
                map(
                    int,
                    [
                        rootGroup.loopMajorVersion,
                        rootGroup.loopMinorVersion,
                        rootGroup.loopSubVersion,
                    ],
                )
            ),
        }
    else:
        return {
            "errorFlag": True,
            "errorString": "No valid Version in Loop Project File",
        }


# Set version on root group
def SetVersion(rootGroup, version):
    """
    **SetVersion** - Saves the version specified into the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    version: [int,int,int]
        The version in list form with [Major/Minor/Sub] version

    Returns
    -------
       dict {"errorFlag","errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    if len(version) != 3:
        errStr = "(ERROR) invalid version for setting current version " + version
        print(errStr)
        return {"errorFlag": True, "errorString": errStr}
    else:
        rootGroup.loopMajorVersion = version[0]
        rootGroup.loopMinorVersion = version[1]
        rootGroup.loopSubVersion = version[2]
        return {"errorFlag": False}
