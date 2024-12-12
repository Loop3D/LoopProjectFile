# import netCDF4

# Check extents of Loop Project File is valid
def CheckExtentsValid(rootGroup, xyzGridSize, verbose=False):
    """
    **CheckExtentsValid** - Checks for valid extents (geodesic, utm, depth,
    and spacing) and working format in project file

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    xyzGridSize: [int, int, int]
        The 3D grid shape of expected data contained in this project file
        based on the extents contained within
    verbose: bool
        A flag to indicate a higher level of console logging (more if True)

    Returns
    -------
    bool
        True if valid extents in project file, False otherwise.

    """
    valid = True
    if ("epsg" in rootGroup.ncattrs()):
        if verbose:
            print("  ", rootGroup.epsg)
    else:
        print("(INVALID) No epsg format in project file")
        valid = False

    # Check Projection Model
    if "workingFormat" in rootGroup.ncattrs():
        if verbose:
            print(
                "  Working in ",
                "Geodesic" if rootGroup.workingFormat == 0 else "UTM",
                " Projection",
            )
    else:
        print("(INVALID) No working format (Geodesic or UTM selection) in project file")
        valid = False

    # Check Geodesic extents
    if (
        "minLatitude" in rootGroup.ncattrs()
        and "maxLatitude" in rootGroup.ncattrs()
        and "minLongitude" in rootGroup.ncattrs()
        and "maxLongitude" in rootGroup.ncattrs()
    ):
        if verbose:
            print("  Geodesic extents found (deg)")
            print("\t minLatitude   = ", rootGroup.minLatitude)
            print("\t maxLatitude   = ", rootGroup.maxLatitude)
            print("\t minLongitude  = ", rootGroup.minLongitude)
            print("\t maxLongitude  = ", rootGroup.maxLongitude)
    else:
        print("(INVALID) No Geodesic extents found")
        valid = False

    # Check UTM extents
    if (
        "minNorthing" in rootGroup.ncattrs()
        and "maxNorthing" in rootGroup.ncattrs()
        and "minEasting" in rootGroup.ncattrs()
        and "maxEasting" in rootGroup.ncattrs()
        and "utmZone" in rootGroup.ncattrs()
        and "utmNorthSouth" in rootGroup.ncattrs()
    ):
        if verbose:
            print("  UTM extents found (m)")
            print("\t minEasting    = ", rootGroup.minEasting)
            print("\t maxEasting    = ", rootGroup.maxEasting)
            print("\t minNorthing   = ", rootGroup.minNorthing)
            print("\t maxNorthing   = ", rootGroup.maxNorthing)
            print("\t utmZone       = ", rootGroup.utmZone)
            print("\t utmNorthSouth = ", "N" if (rootGroup.utmNorthSouth == 1) else "S")
    else:
        print("(INVALID) No UTM extents found")
        valid = False

    # Check Depth Extents
    if "topDepth" in rootGroup.ncattrs() and "bottomDepth" in rootGroup.ncattrs():
        if verbose:
            print("  Depth extents found (m)")
            print("\t bottomDepth   = ", rootGroup.bottomDepth)
            print("\t topDepth      = ", rootGroup.topDepth)
    else:
        print("(INVALID) No Depth extents found")
        valid = False

    # Check X/Y/Z spacing
    if (
        "spacingX" in rootGroup.ncattrs()
        and "spacingY" in rootGroup.ncattrs()
        and "spacingZ" in rootGroup.ncattrs()
    ):
        if verbose:
            print("  Axis Spacing (m)")
            print("\t spacing X axis = ", rootGroup.spacingX)
            print("\t spacing Y axis = ", rootGroup.spacingY)
            print("\t spacing Z axis = ", rootGroup.spacingZ)
    else:
        print("(INVALID) No spacing information in project file")
        valid = False

    if valid:
        xyzGridSize[0] = int(
            (rootGroup.maxEasting - rootGroup.minEasting) / rootGroup.spacingX + 1
        )
        xyzGridSize[1] = int(
            (rootGroup.maxNorthing - rootGroup.minNorthing) / rootGroup.spacingY + 1
        )
        xyzGridSize[2] = int(
            (rootGroup.topDepth - rootGroup.bottomDepth) / rootGroup.spacingZ + 1
        )

    return valid


# Get Extents and return in a dict
def GetExtents(rootGroup):
    """
    **GetExtents** - Extracts Loop Project region of interest extents given a
    netCDF root node

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File

    Returns
    -------
    dict {"errorFlag", "errorString"/"value"}
        value is a dict{
            "geodesic":[double, double, double, double],
            "utm":[int, int, double, double, double, double],
            "depth":[double, double],
            "spacing":[double, double, double],
            "epsg":str
        } containing the extents of this project file

    """
    response = {"errorFlag": False}
    if (
        "minLatitude" in rootGroup.ncattrs()
        and "maxLatitude" in rootGroup.ncattrs()
        and "minLongitude" in rootGroup.ncattrs()
        and "maxLongitude" in rootGroup.ncattrs()
    ):
        geodesic = [
            rootGroup.minLongitude,
            rootGroup.maxLongitude,
            rootGroup.minLatitude,
            rootGroup.maxLatitude,
        ]
    else:
        errStr = "(ERROR) No or incomplete geodesic boundary in loop project file"
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}

    if (
        "utmZone" in rootGroup.ncattrs()
        and "utmNorthSouth" in rootGroup.ncattrs()
        and "minEasting" in rootGroup.ncattrs()
        and "maxEasting" in rootGroup.ncattrs()
        and "minNorthing" in rootGroup.ncattrs()
        and "maxNorthing" in rootGroup.ncattrs()
    ):
        utm = [
            rootGroup.utmZone,
            rootGroup.utmNorthSouth,
            rootGroup.minEasting,
            rootGroup.maxEasting,
            rootGroup.minNorthing,
            rootGroup.maxNorthing,
        ]
    else:
        errStr = "(ERROR) No or incomplete UTM boundary in loop project file"
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}

    if "topDepth" in rootGroup.ncattrs() and "bottomDepth" in rootGroup.ncattrs():
        depth = [rootGroup.bottomDepth, rootGroup.topDepth]
    else:
        errStr = "(ERROR) No or incomplete depth boundary in loop project file"
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}

    if (
        "spacingX" in rootGroup.ncattrs()
        and "spacingY" in rootGroup.ncattrs()
        and "spacingZ" in rootGroup.ncattrs()
    ):
        spacing = [rootGroup.spacingX, rootGroup.spacingY, rootGroup.spacingZ]
    else:
        errStr = "(ERROR) No or incomplete spacing data in loop project file"
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}

    if ("epsg" in rootGroup.ncattrs()):
        epsg = rootGroup.epsg
    else:
        errStr = "(ERROR) No or incomplete epsg data in loop project file"
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}

    if response["errorFlag"] is False:
        response["value"] = {
            "geodesic": geodesic,
            "utm": utm,
            "depth": depth,
            "spacing": spacing,
            "epsg": epsg
        }
    return response


# Set extents of region of interest on root group
def SetExtents(rootGroup, geodesic, utm, depth, spacing, epsg, preference="utm"):
    """
    **SetExtents** - Saves the extents of the region of interest as specified into
    the netCDF Loop Project File

    Parameters
    ----------
    rootGroup: netCDF4.Group
        The root group node of a Loop Project File
    geodesic: [double, double, double, double]
        The latitude and longitude limits of the region in format:
        [minLong, maxLong, minLat, maxLat]
    utm: [int, int, double, double, double, double]
        The utmZone, utmNorth/South, easting and northing extents in format:
        [utmZone, utmNorthSouth, minEasting, maxEasting, minNorthing, maxNorthing]
    depth: [double, double]
        The depth minimum and maximums in format: [bottomDepth, topDepth]
    spacing: [double, double, double]
        The spacing of adjacent points in the grid for X/Y/Z.  This corresponds
        to [longitude/easting, latitude/northing, depth]
    preference: string (optional)
        A string ("utm" or "geodesic") which specifies which format the Loop GUI
        region of interest should be displayed
    epsg: string
        A string of the EPSG projection used in the Loop Project in the
        format "EPSG:<value>"

    Returns
    -------
       dict {"errorFlag", "errorString"}
        errorString exist and contains error message only when errorFlag is
        True

    """
    response = {"errorFlag": False}
    if len(geodesic) != 4:
        errStr = (
            "(ERROR) Invalid number of geodesic boundary values ("
            + str(len(geodesic))
            + ")"
        )
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    else:
        rootGroup.minLongitude = geodesic[0]
        rootGroup.maxLongitude = geodesic[1]
        rootGroup.minLatitude = geodesic[2]
        rootGroup.maxLatitude = geodesic[3]
    if len(utm) != 6:
        errStr = "(ERROR) Invalid number of UTM boundary values (" + str(len(utm)) + ")"
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    else:
        rootGroup.utmZone = utm[0]
        rootGroup.utmNorthSouth = (
            0 if utm[1] == "S" or utm[1] == "s" or utm[1] == 0 else 1
        )
        rootGroup.minEasting = utm[2]
        rootGroup.maxEasting = utm[3]
        rootGroup.minNorthing = utm[4]
        rootGroup.maxNorthing = utm[5]
    if len(depth) != 2:
        errStr = (
            "(ERROR) Invalid number of depth boundary values (" + str(len(depth)) + ")"
        )
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    else:
        rootGroup.bottomDepth = depth[0]
        rootGroup.topDepth = depth[1]
    if len(spacing) != 3:
        errStr = "(ERROR) Invalid number of spacing values (" + str(len(depth)) + ")"
        print(errStr)
        response = {"errorFlag": True, "errorString": errStr}
    else:
        rootGroup.spacingX = spacing[0]
        rootGroup.spacingY = spacing[1]
        rootGroup.spacingZ = spacing[2]
    rootGroup.workingFormat = 1 if preference == "utm" else 0
    rootGroup.epsg = epsg

    # Do a quick sanity check and swap min and max values if wrong
    if rootGroup.minLatitude > rootGroup.maxLatitude:
        tmp = rootGroup.minLatitude
        rootGroup.minLatitude = rootGroup.maxLatitude
        rootGroup.maxLatitude = tmp
    if rootGroup.minLongitude > rootGroup.maxLongitude:
        tmp = rootGroup.minLongitude
        rootGroup.minLongitude = rootGroup.maxLongitude
        rootGroup.maxLongitude = tmp
    if rootGroup.minEasting > rootGroup.maxEasting:
        tmp = rootGroup.minEasting
        rootGroup.minEasting = rootGroup.maxEasting
        rootGroup.maxEasting = tmp
    if rootGroup.minNorthing > rootGroup.maxNorthing:
        tmp = rootGroup.minNorthing
        rootGroup.minNorthing = rootGroup.maxNorthing
        rootGroup.maxNorthing = tmp
    if rootGroup.bottomDepth > rootGroup.topDepth:
        tmp = rootGroup.bottomDepth
        rootGroup.bottomDepth = rootGroup.topDepth
        rootGroup.topDepth = tmp

    return response
