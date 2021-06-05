from typing import Dict, Any, List, Optional

from pathlib import PurePosixPath

from kedro.io.core import (
    AbstractVersionedDataSet,
    get_filepath_str,
    get_protocol_and_path, Version,
)

import fsspec
import numpy as np
import json


class JSONLinesDataSet(AbstractVersionedDataSet):
    _version = False

    def __init__(self, filepath: str, version: Optional[Version] = 0):
        """Creates a new instance of JSONLinesDataSet.
        Each line of the file is a json object

        Args:
            filepath: The location of the image file to load / save data.
        """
        # parse the path and protocol (e.g. file, http, s3, etc.)
        super().__init__(filepath, version)
        protocol, path = get_protocol_and_path(filepath)
        self._protocol = protocol
        self._filepath = PurePosixPath(path)
        self._fs = fsspec.filesystem(self._protocol)

    def _describe(self) -> Dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset."""
        return dict(filepath=self._filepath, protocol=self._protocol)

    def _load(self) -> List[dict]:
        """Loads list of dict from the file.

        Returns:
            Data from the file as a list of dicts
        """
        # using get_filepath_str ensures that the protocol and path are appended correctly for different filesystems
        load_path = get_filepath_str(self._get_load_path(), self._protocol)
        data = []
        with self._fs.open(load_path) as f:
            for line in f:
                data.append(json.loads(line))
        return data

    def _save(self, data: List[dict]) -> None:
        """Saves list of dicts to the specified filepath."""
        # using get_filepath_str ensures that the protocol and path are appended correctly for different filesystems
        save_path = get_filepath_str(self._get_save_path(), self._protocol)

        with self._fs.open(save_path, "w", encoding="utf8") as f:
            for sample in data:
                f.write(json.dumps(sample) + "\n")
