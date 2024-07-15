from random import randint

def random_rgb():
    r = randint(0x00, 0xff)
    g = randint(0x00, 0xff)
    b = randint(0x00, 0xff)
    u32 = (r << 16) | (g << 8) | b
    string = f'hex: {hex(u32)[2:]}, dec: {u32}'

    return (r, g, b), string

