#!/usr/bin/env python
from clicky_scripts import CliClick, GetMouseCoordinates


click = CliClick()
c = GetMouseCoordinates()
click.add_command(c)
click.execute()
print(c)
