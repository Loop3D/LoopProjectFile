# Check Probability Model valid if present
def CheckProbabilityModelValid(rootGroup, verbose=False):
    """
    **CheckProbabilityModelValid** - Checks for valid Probability model group data
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
        True if valid probability data in project file, False otherwise.

    """
    valid = True
    if "ProbabilityModel" in rootGroup.groups:
        if verbose:
            print("  Probability Model Group Present")
        pmGroup = rootGroup.groups.get("ProbabilityModel")
        if verbose:
            print(pmGroup)
    else:
        if verbose:
            print("No Probability Model Group Present")
    return valid
