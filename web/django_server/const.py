import enum


class BaseEnum(enum.Enum):
    @classmethod
    def to_choice(cls):
        return [(tag.value, tag) for tag in cls]

    @classmethod
    def values(cls, excepts=[]):
        return [tag.value for tag in cls if tag not in excepts]

    @classmethod
    def of(cls, value):
        if value is None:
            return None

        for tag in cls:
            if tag.value == value:
                return tag
        return None


class SpaceStateEnum(BaseEnum):
    WATING = 'w'
    AVAILABLE = 'a'
    UNAVAILABLE = 'u'


class ManClassEnum(BaseEnum):
    ADMIN = 'a'
    MEMBER = 'm'
    NON_MEMBER = 'n'
    GUEST = 'g'


class ProgramStateEnum(BaseEnum):
    READY = 'r'
    INVITING = 'i'
    PROGRESS = 'p'
    END = 'e'
    SUSPEND = 's'


class UserStatusEnum(BaseEnum):
    ACTIVE = 'a'
    INACTIVE = 'i'
    DELETED = 'd'


class ProgramTagTypeEnum(BaseEnum):
    AFTERSCHOOL = 'a'
    TOWN = 't'
    ETC = 'e'


class MannaError(enum.Enum):
    # general case: 1XXX
    INVALID_PARAMETER = 1000
    INVALID_STATE = 1001
    INVALID_PERMISSION = 1002
    DUPLICATED = 1010
    TOO_MANY = 1011
    DOES_NOT_EXIST = 1012
    INVALID_TOKEN = 1013

    # program & meeting: 2xxx
    MAX_PARTICIPANT = 2000
    EXPIRED = 2001
