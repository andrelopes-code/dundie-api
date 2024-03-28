import unicodedata


def get_username(name: str) -> str:
    name = name.lower().replace(' ', '-')

    chars = []

    for c in unicodedata.normalize('NFD', name):
        if unicodedata.category(c) != 'Mn':
            chars.append(c)

    return ''.join(chars)


x = get_username("áááá")
