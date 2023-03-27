from clicky_scripts import CliClick, GetMouseCoordinates

def test_get_mouse_coordinates():
    clicky = CliClick()
    c = GetMouseCoordinates()
    assert(c.x == None)
    assert(c.y == None)
    clicky.add_command(c)
    clicky.execute()
    assert(type(c.x) == int)
    assert(type(c.y) == int)
