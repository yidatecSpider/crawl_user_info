import hashlib


def calc_raw_video(chat):
    return get_md5_int('%s' % chat)


def get_raw_video_id(chat):
    return '%s' % calc_raw_video(chat)


def get_md5_int(calc_str):
    calc_str = calc_str.encode('utf8')
    hex_val = hashlib.md5(calc_str).hexdigest()
    deci_val = 0
    for i in range(0, 8):
        p = 7 - i
        deci_val = deci_val * 256 + int(hex_val[p * 2:p * 2 + 2], 16)
    return deci_val