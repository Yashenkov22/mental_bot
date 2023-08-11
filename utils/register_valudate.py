from string import ascii_lowercase as alphabet


def valid_fullname(fullname: str):
    fullname = fullname.lower().split()
    return len(fullname) == 2 \
        and not (set(''.join(fullname)) & set(alphabet))