from typing import Dict, Any, List

from pathlib import PurePosixPath

from kedro.io.core import (
    AbstractVersionedDataSet,
    get_filepath_str,
    get_protocol_and_path,
)

import fsspec
import numpy as np
import json


class JSONFileDataSet(AbstractVersionedDataSet):
    _version = False

    def __init__(self, filepath: str):
        """Creates a new instance of JsonFileDataSet.
        Simple json file

        Args:
            filepath: The location of the json file to load / save data.
        """
        # parse the path and protocol (e.g. file, http, s3, etc.)
        protocol, path = get_protocol_and_path(filepath)
        self._protocol = protocol
        self._filepath = PurePosixPath(path)
        self._fs = fsspec.filesystem(self._protocol)

    def _describe(self) -> Dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset."""
        return dict(filepath=self._filepath, protocol=self._protocol)

    def _load(self) -> Dict[str, Any]:
        """Loads dict from the json file.

        Returns:
            dict
        """
        # using get_filepath_str ensures that the protocol and path are appended correctly for different filesystems
        load_path = get_filepath_str(self._get_load_path(), self._protocol)
        with self._fs.open(load_path) as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]) -> None:
        """Saves dict to json to the specified filepath."""
        # using get_filepath_str ensures that the protocol and path are appended correctly for different filesystems
        save_path = get_filepath_str(self._get_save_path(), self._protocol)
        with self._fs.open(save_path, "wb") as f:
            json.dump(data, save_path)
