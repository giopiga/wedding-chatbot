def read_key():
    try:
        with open("config/key.txt") as f:
            lines = f.readlines()
            key = lines[0]
            return key
    except Exception as e:
        raise Exception(f"No key found because of {e}")


def read_pwd():
    try:
        with open("config/pwd.txt") as f:
            lines = f.readlines()
            pwd = lines[0]
            return pwd
    except Exception as e:
        raise Exception(f"No pwd found because of {e}")
