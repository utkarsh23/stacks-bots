def hex_to_text(hexadecimal):
    return bytes.fromhex(hexadecimal[2:]).decode("utf-8")
