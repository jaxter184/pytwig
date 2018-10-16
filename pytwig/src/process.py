from src import decoder, encoder
from src.lib import fs, util, atoms, route, dicttobw
from src.lib.luts import typeLists

def process_data(input, flag='decode'): #decodes then reencodes a single file
    header = input[:40].decode("utf-8") #'BtWg00010001008d000016a00000000000000000'
    if flag == 'decode':
        header = header[:11] + '1' + header[12:]
        pre_output = ''
        decoded_input = decoder.bwDecode(input)
        for each_object in decoded_input: #encodes all of the objects in the output list
            pre_output += util.json_encode(atoms.serialize(each_object))
        return header + decoder.reformat(pre_output)
    else if flag == 'encode':
        encoded_input = encoder.bwEncode(input)
        header = header[:11] + '2' + header[12:]
        return header.encode('utf-8') + encoded_input

'''def x_in_y(query, base): #got this from online somewhere
    try:
        l = len(query)
    except TypeError:
        l = 1
        query = type(base)((query,))

    for i in range(len(base)):
        if base[i:i+l] == query:
            return True
    return False'''
