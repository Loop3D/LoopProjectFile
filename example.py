import LoopProjectFile as LPF
import sys
import numpy

# Start Main function
# Sanity check arguments
if len(sys.argv) < 2:
    print("Usage: python run.py <filename>")
    quit()
else:
    filename = sys.argv[1]

# Create basic Loop Project and add extents for broken hill region
LPF.CreateBasic(filename)
geodes = [-31.90835, -31.863242, 141.493799, 141.546666]
utm = [54, "S", 6469600, 6474600, 546700, 551700]
depth = [-1000, -6000]
spacing = [100, 100, 100]
LPF.Set(filename, "extents", geodesic=geodes, utm=utm, depth=depth, spacing=spacing)

# Check new file is valid and report the version of the file
LPF.CheckFileValid(filename, True)
resp = LPF.Get(filename, "version")
if resp["errorFlag"]:
    print(resp["errorString"])
else:
    print(resp["value"])

# Report the extents of the new file
resp = LPF.Get(filename, "extents")
if resp["errorFlag"]:
    print(resp["errorString"])
else:
    extents = resp["value"]
    print("Geodesic:", extents["geodesic"])
    print("UTM:     ", extents["utm"])
    print("Depth:   ", extents["depth"])
    print("Spacing: ", extents["spacing"])

# Grab the dummy dataset from the bh Loop Project File with shape (51x51x51)
# and add it to this project (required to have the same shape)
resp = LPF.Get("bh.loop3d", "strModel")
if resp["errorFlag"]:
    print(resp["errorString"])
else:
    strData = resp["value"]
    resp2 = LPF.Set(filename, "strModel", data=strData, index=0)
    if resp2["errorFlag"]:
        print(resp2["errorString"])
    else:
        print("Data saved in new file")
    resp3 = LPF.Get(filename, "strModel", index=0)
    if resp3["errorFlag"]:
        print(resp3["errorString"])
    else:
        print("Data received again")

stratigraphy = numpy.zeros(3, LPF.stratigraphicLayerType)
stratigraphy[0] = (
    1,
    1.0,
    1.1,
    b"Thick One",
    b"Hammersley",
    b"S0",
    1,
    0,
    1,
    1000.0,
    0,
    0,
    0,
    0,
    0,
    0,
)
stratigraphy[1] = (
    2,
    1.1,
    1.2,
    b"Thin One",
    b"Hammersley",
    b"S0",
    1,
    0,
    1,
    100.0,
    0,
    0,
    0,
    0,
    0,
    0,
)
stratigraphy[2] = (
    3,
    1.1,
    1.2,
    b"Next One",
    b"Hammersley",
    b"S0",
    1,
    0,
    1,
    50.0,
    0,
    0,
    0,
    0,
    0,
    0,
)
LPF.Set(filename, "stratigraphicLog", data=stratigraphy)

# Set some dummy observations within the region of interest
contacts = numpy.zeros(3, LPF.contactObservationType)
contacts[0] = (1, 550500.0, 6470000.0, 0.0, 4)
contacts[1] = (2, 550500.0, 6070000.0, 0.0, 4)
contacts[2] = (3, 500500.0, 6070000.0, 0.0, 4)
LPF.Set(filename, "contacts", data=contacts)
LPF.Set(filename, "contactsAppend", data=contacts)

drillholes = numpy.zeros(3, LPF.drillholeObservationType)
drillholes[0] = (
    1023,
    10342.342,
    6034243.226,
    113.34,
    1,
    10342.342,
    6034243.226,
    13.34,
    90.0,
    180.0,
)
drillholes[1] = (
    1023,
    10342.342,
    6034243.226,
    13.34,
    2,
    10342.342,
    6034243.226,
    -86.66,
    90.0,
    180.0,
)
drillholes[2] = (
    1023,
    10342.342,
    6034243.226,
    -86.66,
    3,
    10342.342,
    6034243.226,
    -186.66,
    90.0,
    180.0,
)
LPF.Set(filename, "drillholeObservations", data=drillholes)

# Get the observation data back out to confirm it was saved
resp = LPF.Get(filename, "stratigraphicLog")
if resp["errorFlag"]:
    print(resp["errorString"])
else:
    print(LPF.ConvertToDataFrame(resp["value"], LPF.stratigraphicLayerType))

# Get the observation data back out to confirm it was saved
resp = LPF.Get(filename, "contacts", indexRange=(0, 7))
if resp["errorFlag"]:
    print(resp["errorString"])
else:
    print(LPF.ConvertToDataFrame(resp["value"], LPF.contactObservationType))

resp = LPF.Get(filename, "drillholeObservations")
if resp["errorFlag"]:
    print(resp["errorString"])
else:
    print(LPF.ConvertToDataFrame(resp["value"], LPF.drillholeObservationType))
