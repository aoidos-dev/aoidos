
from voxpopuli import PhonemeList

def trim_silences(pho_list : PhonemeList) -> PhonemeList:
    return PhonemeList(pho_list[:-2])