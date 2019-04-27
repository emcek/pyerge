from pytest import mark
from pyerge.tmerge import convert2blocks


@mark.parametrize('size, result', [('12K', 12), ('34567k', 34567), ('31M', 31744), ('233m', 238592), ('2G', 2097152), ('1g', 1048576)])
def test_convert2blocks(size, result):
    assert convert2blocks(size) == result
