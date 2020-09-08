# for more information about this file
# see: https://github.com/protocolbuffers/protobuf/issues/1491#issuecomment-547504972

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from . discovery_service_pb2_grpc import *
from . discovery_service_pb2 import *
from . error_pb2_grpc import *
from . error_pb2 import *
