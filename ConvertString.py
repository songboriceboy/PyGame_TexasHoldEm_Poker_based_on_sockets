def from_bytes_to_string(byte):
    return str(byte).replace("b'", "").replace("'", "").replace(" ", "")
