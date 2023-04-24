#!/usr/bin/env python

import datetime

from clicky_scripts import DailyStart
from clicky_scripts import DailyAsanaProject
from clicky_scripts import KeepUpdating

DailyAsanaProject(datetime.datetime.today() + datetime.timedelta(days=6)).execute()
