def strip(s: str):
    return s.replace('<p>', '').\
        replace('</p>', ' ').\
        replace('<br>', ' ').\
        replace('<br/>', ' ').\
        replace('<br />', ' ').\
        replace('&ndash;', '-').\
        replace('&nbsp;', ' ').strip()


def maybe_get(d, key):
    if isinstance(d, str):
        return strip(d)
    val = d.get(key)
    if not isinstance(val, dict):
        return val
    elif 'ru' in val:
        return strip(val['ru'])
    elif '1' in val:
        return val['1']
    else:
        return val


def normalize_coord(coords):
    if isinstance(coords, str):
        if isinstance(coords, str) and coords.count(','):
            coords = ','.join(coords.split(',')[-2:])
    return coords
