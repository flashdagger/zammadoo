#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__version__ = "0.1.0"

from .client import LOG, APIException, Client as Client

LOG.name = __name__
_ = APIException, Client  # make pyflakes happy
