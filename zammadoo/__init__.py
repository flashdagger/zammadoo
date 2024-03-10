#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__version__ = "0.2.0"

from .client import LOG, APIException
from .client import Client as Client  # pylint: disable=useless-import-alias

LOG.name = __name__
_ = APIException, Client  # make pyflakes happy
