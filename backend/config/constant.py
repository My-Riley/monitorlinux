class CommonConstant:
    """通用常量"""

    HTTP = "http://"
    HTTPS = "https://"
    WWW = "www."
    YES = "Y"
    NO = "N"
    SUCCESS = "0"
    FAIL = "1"
    LOGIN_SUCCESS = "登录成功"
    LOGOUT = "退出成功"
    REGISTER = "注册成功"
    LOGIN_FAIL = "登录失败"
    LOGIN_FAIL = "登录失败"
    LOOKUP_RMI = "rmi:"
    LOOKUP_LDAP = "ldap:"
    LOOKUP_LDAPS = "ldaps:"
    UNIQUE = True
    NOT_UNIQUE = False
    DEPT_NORMAL = "0"
    DEPT_DISABLE = "1"


class JobConstant:
    """定时任务常量"""

    JOB_ERROR_LIST = [
        "app",
        "config",
        "exceptions",
        "import ",
        "middlewares",
        "module_admin",
        "open(",
        "os.",
        "server",
        "sub_applications",
        "subprocess.",
        "sys.",
        "utils",
        "while ",
        "__import__",
        '"',
        "'",
        ",",
        "?",
        ":",
        ";",
        "/",
        "|",
        "+",
        "-",
        "=",
        "~",
        "!",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "<",
        ">",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        " ",
    ]
    JOB_WHITE_LIST = ["module_task"]


class MenuConstant:
    """菜单常量"""

    TYPE_DIR = "M"
    TYPE_MENU = "C"
    TYPE_BUTTON = "F"
    YES_FRAME = 0
    NO_FRAME = 1
    LAYOUT = "Layout"
    PARENT_VIEW = "ParentView"
    INNER_LINK = "InnerLink"


class HttpStatusConstant:
    """HTTP状态码常量"""

    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    MOVED_PERM = 301
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    BAD_METHOD = 405
    CONFLICT = 409
    UNSUPPORTED_TYPE = 415
    ERROR = 500
    NOT_IMPLEMENTED = 501
    WARN = 601
