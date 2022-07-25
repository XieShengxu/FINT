
def int2mac(switch_number):
    """
    auto generate mac address with the number in string
    @param switch_number: mac address number (int)
    @return: mac address in string
    """
    str_swt = str(hex(switch_number))[2:]
    mac_addr = ''
    for i in range(12):
        if i < 12 - len(str_swt):
            mac_addr += '0'
        else:
            mac_addr += str_swt[i - 12 + len(str_swt)]
        if i % 2 == 1 and i != 11:
            mac_addr += ':'
    return mac_addr


def convert(inputs):
    """
    change the code of json.load() from unicode to utf-8
    @param inputs: json.load(x)
    @return: the dictionary of json file encoded with utf-8
    """
    if isinstance(inputs, dict):
        return {convert(key): convert(value) for key, value in inputs.iteritems()}
    elif isinstance(inputs, list):
        return [convert(element) for element in inputs]
    elif isinstance(inputs, unicode):
        return inputs.encode('utf-8')
    else:
        return inputs
