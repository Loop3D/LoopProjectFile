# from multiprocessing.sharedctypes import Value
from .LoopProjectFile import (
    Get,
    Set,
    CheckFileValid,
    CheckFileIsLoopProjectFile,
)  # , CreateBasic, OpenProjectFile
from .LoopProjectFileUtils import ElementFromDataframe  # , ElementFromDataframe
import LoopProjectFile
import pandas as pd
import numpy as np

compoundTypeMap = {
    "version": None,
    "extents": None,
    "strModel": None,
    "faultObservations": LoopProjectFile.faultObservationType,
    "foldObservations": LoopProjectFile.foldObservationType,
    "foliationObservations": LoopProjectFile.foliationObservationType,
    "discontinuityObservations": LoopProjectFile.discontinuityObservationType,
    "stratigraphicObservations": LoopProjectFile.stratigraphicObservationType,
    "contacts": LoopProjectFile.contactObservationType,
    "stratigraphicLog": LoopProjectFile.stratigraphicLayerType,
    "stratigraphicThicknesses": LoopProjectFile.stratigraphicThicknessType,
    "faultLog": LoopProjectFile.faultEventType,
    "foldLog": None,
    "foliationLog": None,
    "discontinuityLog": None,
    "dataCollectionConfig": None,
    "dataCollectionSources": None,
    "eventRelationships": LoopProjectFile.eventRelationshipType,
    "structuralModelsConfig": None,
}


class ProjectFile:
    def __init__(self, project_filename):
        """Python interface for the Loop project file.

        Parameters
        ----------
        project_filename : string
            name/path of projectfile

        Raises
        ------
        BaseException
            Exception if project file doesn't exist
        """
        valid = CheckFileIsLoopProjectFile(project_filename)
        if valid is False:
            raise BaseException("Project file does not exist")
        self.project_filename = project_filename
        self.element_names = [
            "version",
            "extents",
            "strModel",
            "faultObservations",
            "foldObservations",
            "foliationObservations",
            "discontinuityObservations",
            "stratigraphicObservations",
            "contacts",
            "stratigraphicLog",
            "faultLog",
            "foldLog",
            "foliationLog",
            "discontinuityLog",
            "dataCollectionConfig",
            "dataCollectionSources",
            "eventRelationships",
            "structuralModelsConfig",
        ]
        self.compoundTypeMap = compoundTypeMap

    @classmethod
    def new(cls, filename):
        """Create a new project file.

        Parameters
        ----------
        filename : string
            name of projectfile

        Returns
        -------
        ProjectFile
            the new projectfile class
        """
        LoopProjectFile.CreateBasic(filename)
        projectfile = ProjectFile(filename)
        return projectfile

    @property
    def valid(self) -> bool:
        """Check if the project file is valid

        Returns
        -------
        bool
            true if project file is valid, false if not
        """
        return self.is_valid()

    def is_valid(self) -> bool:
        return CheckFileValid(self.project_filename)

    def _add_names_to_df(self, log, df):
        """_summary_

        Parameters
        ----------
        log : _type_
            _description_
        df : _type_
            _description_
        """
        df["name"] = "none"
        for stratigraphic_id in log.index:
            df.loc[df["layerId"] == stratigraphic_id, "name"] = log.loc[stratigraphic_id, "name"]

    @property
    def extents(self) -> np.ndarray:
        """Get the extents of the model

        Returns
        -------
        np.ndarray
            _description_
        """
        resp = Get(self.project_filename, "extents")
        if resp["errorFlag"] is True:
            return None
        return resp["value"]

    @extents.setter
    def extents(self, extents):
        Set(self.project_filename, "extents", **extents)
        pass

    @property
    def version(self) -> str:
        """Get version of the project file

        Returns
        -------
        str
            version string major.minor.patch
        """
        resp = Get(self.project_filename, "version")
        if resp["errorFlag"] is True:
            return None
        return "{}.{}.{}".format(*resp["value"])

    @property
    def origin(self) -> np.ndarray:
        """Get the origin of the model"""
        origin = np.zeros(3)
        origin[0] = self.extents["utm"][2]
        origin[1] = self.extents["utm"][4]
        origin[2] = self.extents["depth"][0]
        return origin

    @property
    def maximum(self) -> np.ndarray:
        """Get top right hand coordinate of the bouinding box

        Returns
        -------
        np.ndarray
            _description_
        """
        maximum = np.zeros(3)
        maximum[0] = self.extents["utm"][3]
        maximum[1] = self.extents["utm"][5]
        maximum[2] = self.extents["depth"][1]
        return maximum

    @property
    def faultObservations(self) -> pd.DataFrame:
        return self.__getitem__("faultObservations")

    @faultObservations.setter
    def faultObservations(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            self.__setitem__("faultObservations", value)
        self._validate_data_frame_columns(
            value,
            {
                k: True
                for k in [
                    "eventId",
                    "easting",
                    "northing",
                    "altitude",
                    "type",
                    "dipDir",
                    "dip",
                    "dipPolarity",
                    "val",
                    "displacement",
                    "posOnly",
                ]
            },
        )
        self.__setitem__("faultObservations", value)

    @property
    def faultLocations(self) -> pd.DataFrame:
        """Get only the observations of the fault location

        Returns
        -------
        pd.DataFrame
            _description_
        """
        df = self.__getitem__("faultObservations")
        # self._add_names_to_df(self.faultLog, df)
        return df.loc[df["posOnly"] == 1, :]

    def _validate_data_frame_columns(self, df: pd.DataFrame, columns: dict):
        for c in columns.keys():
            if c in df.columns:
                columns[c] = True
        columns_in_df = True
        for c in columns.keys():
            if columns[c] is False:
                columns_in_df = False
                print(f"Column: {c} not dataframe")
                # logger.error(f'Column: {c} not dataframe')
        if columns_in_df is False:
            raise ValueError("Columns not in dataframe")

    @faultLocations.setter
    def faultLocations(self, value: pd.DataFrame):
        """Update the faultObservations with new fault locations

        Parameters
        ----------
        value : pd.DataFrame
            _description_
        """
        if isinstance(value, pd.DataFrame) is False:
            raise TypeError("faultLocations must be set with a pandas dataframe")
        columns = {
            "eventId": False,
            "easting": False,
            "northing": False,
            "altitude": False,
            "val": False,
        }
        self._validate_data_frame_columns(value, columns)
        df = self.__getitem__("faultObservations")
        value["posOnly"] == 1
        value = pd.concat([value, df.loc[df["posOnly"] == 0, :]])
        value.reset_index(inplace=True)
        self.__setitem__("faultObservations", value)

    @property
    def faultOrientations(self) -> pd.DataFrame:
        df = self.__getitem__("faultObservations")
        return df.loc[df["posOnly"] == 0, :]

    @faultOrientations.setter
    def faultOrientations(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame) is False:
            raise TypeError("faultOrientations must be set with a pandas dataframe")
        columns = {
            "eventId": False,
            "easting": False,
            "northing": False,
            "altitude": False,
            "dipDir": False,
            "dip": False,
            "dipPolarity": False,
        }
        self._validate_data_frame_columns(value, columns)

        df = self.__getitem__("faultObservations")
        value["posOnly"] == 0
        value = pd.concat([value, df.loc[df["posOnly"] == 1, :]])
        value.reset_index(inplace=True)
        self.__setitem__("faultObservations", value)

    @property
    def faultLog(self) -> pd.DataFrame:
        return self.__getitem__("faultLog")  # .set_index('name')

    @faultLog.setter
    def faultLog(self, value: pd.DataFrame):
        self.__setitem__("faultLog", value)

    @property
    def foliationObservations(self) -> pd.DataFrame:
        return self.__getitem__("foliationObservations")

    @foliationObservations.setter
    def foliationObservations(self, value: pd.DataFrame):
        self.__setitem__("foliationObservations", value)

    @property
    def foldObservations(self) -> pd.DataFrame:
        return self.__getitem__("foldObservations")

    @foldObservations.setter
    def foldObservations(self, value: pd.DataFrame):
        self.__setitem__("foldObservations", value)

    @property
    def stratigraphicLog(self) -> pd.DataFrame:
        return self.__getitem__("stratigraphicLog")

    @stratigraphicLog.setter
    def stratigraphicLog(self, value: pd.DataFrame):
        # TODO: add a validator
        self.__setitem__("stratigraphicLog", value)

    @property
    def stratigraphyLocations(self) -> pd.DataFrame:
        df = self.__getitem__("contacts")
        self._add_names_to_df(self.stratigraphicLog, df)
        return df

    @stratigraphyLocations.setter
    def stratigraphyLocations(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame) is False:
            raise TypeError("stratigraphyLocations must be set with a pandas dataframe")
        self._validate_data_frame_columns(
            value,
            {k: False for k in ["layerId", "easting", "northing", "altitude", "type", "name"]},
        )
        self.__setitem__("contacts", value)

    @property
    def stratigraphyOrientations(self) -> pd.DataFrame:
        df = self.__getitem__("stratigraphicObservations")
        self._add_names_to_df(self.stratigraphicLog, df)
        return df

    @stratigraphyOrientations.setter
    def stratigraphyOrientations(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame) is False:
            raise TypeError("stratigraphyOrientations must be set with a pandas dataframe")
        self._validate_data_frame_columns(
            value,
            {
                k: False
                for k in [
                    "layerId",
                    "easting",
                    "northing",
                    "altitude",
                    "type",
                    "name",
                    "dipDir",
                    "dip",
                    "dipPolarity",
                    "layer",
                ]
            },
        )
        self.__setitem__("stratigraphicObservations", value)

    def _ipython_key_completions_(self):
        return self.element_names

    def __getitem__(self, element):
        resp = Get(self.project_filename, element)
        if resp["errorFlag"] is False:
            if compoundTypeMap[element] is None:
                return resp["value"]
            else:
                return LoopProjectFile.ElementToDataframe(
                    self.project_filename, element, compoundTypeMap[element]
                )
        # if the project file is empty for a given element, return an empty dataframe with the correct headers
        if resp["errorFlag"] is True:
            if (
                resp["errorString"]
                == "No Observations present in DataCollection for access request"
            ):
                # TODO: this isn't really ideal and maybe need to be removed but at least it gives an idea of the column
                # names needed.
                return pd.DataFrame(columns=list(compoundTypeMap[element].names))
            if (
                resp["errorString"]
                == "No EventLog present in ExtractedInformation for access request"
            ):
                # TODO: this isn't really ideal and maybe need to be removed but at least it gives an idea of the column
                # names needed.
                return pd.DataFrame(columns=list(compoundTypeMap[element].names))
        # return ProjectFileElement(self.project_filename, element).value

    def __setitem__(self, element, value):
        if compoundTypeMap[element] is None:
            if isinstance(value, dict):
                Set(self.project_filename, element, **value)
            else:
                Set(self.project_filename, element, {element: value})
        else:
            if isinstance(value, pd.DataFrame):
                names = compoundTypeMap[element].names
                if pd.Index(names).isin(value.columns).all():
                    ElementFromDataframe(
                        self.project_filename,
                        value.loc[:, names],
                        element,
                        compoundTypeMap[element],
                    )
                else:
                    raise ValueError("Dataframe must have columns: {}".format(names))
            else:
                raise TypeError("Cannot set project file with {}".format(type(value)))
