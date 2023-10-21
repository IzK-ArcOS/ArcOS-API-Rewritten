import mimetypes
from pathlib import Path

# a bit of hijacking for platform parity
mimetypes.knownfiles = [str(Path(__file__).parent.joinpath('mime.types').resolve())]
mimetypes.init()
