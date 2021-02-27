SERVER_PROFILES = {
    'router_manager': {
        'addr4router': ('0.0.0.0', '1313'),
    },
    '13::': {
        "addr4router": ('127.0.0.1', '1315'),
        "local_addr": "13::",
        'addr4port': ('127.0.0.1', '1316'),
    },
    '13:game1:': {
        'addr4client': ('127.0.0.1', '1315'),
        'local_addr': '13:game1:',
        'router_addr': '13::'
    },
    '13:gate1:': {
        'addr4client': ('127.0.0.1', '1317'),
        'local_addr': '13:gate1:',
        'router_addr': '13::'
    }
}


def get_profile(local_addr):
    return SERVER_PROFILES.get(local_addr)
