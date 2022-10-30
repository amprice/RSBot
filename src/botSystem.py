from enum import Enum

# TODO: Tie this into knowing is pytest is running or imported....
class BUILD_TYPE(Enum):
        MANUAL_TESTING = 1,
        UNIT_TESTING = 2,
        RELEASE = 3,

BUILD_TYPE = BUILD_TYPE.RELEASE
#BUILD_TYPE = BUILD_TYPE.UNIT_TESTING