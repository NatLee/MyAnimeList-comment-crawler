
import os
import logging
import platform
from datetime import datetime, timedelta
from tqdm import tqdm

class TqdmUpTo(tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
    def updateTo(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # will also set self.n = b * bsize

def creationDate(filePath):
    if platform.system() == 'Windows':
        time = os.path.getctime(filePath)
    else:
        stat = os.stat(filePath)
        try:
            time = stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            logging.warning('Unable to get create time, so return last modified time.')
            time =  stat.st_mtime
    return datetime.fromtimestamp(time)

