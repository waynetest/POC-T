# !/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'xy'

import os
import re
import sys
import time
from lib.core.data import *
from lib.core.log import CUSTOM_LOGGING,LOGGER_HANDLER
from lib.core.settings import BANNER,UNICODE_ENCODING,NULL,INVALID_UNICODE_CHAR_FORMAT
from lib.core.enums import CONTENT_STATUS

def setPaths():
    """
    Sets absolute paths for project directories and files
    """
    ROOT_PATH = paths['ROOT_PATH']
    paths['DATA_PATH'] = os.path.join(ROOT_PATH, "data")
    paths['MODULES_PATH'] = os.path.join(ROOT_PATH, "module")
    paths['OUTPUT_PATH'] = os.path.join(ROOT_PATH, "output")
    paths['WEAK_PASS'] = os.path.join(paths['DATA_PATH'], "pass100.txt")
    paths['LARGE_WEAK_PASS'] = os.path.join(paths['DATA_PATH'], "pass1000.txt")


def checkFile(filename):
    """
    @function Checks for file existence and readability
    """

    valid = True

    if filename is None or not os.path.isfile(filename):
        valid = False

    if valid:
        try:
            with open(filename, "rb"):
                pass
        except:
            valid = False

    if not valid:
        raise Exception("unable to read file '%s'" % filename)


def debugPause():
    if conf['DEBUG']:
        raw_input('[Debug] Press any key to continue.')


def showDebugData():
    logger.log(CUSTOM_LOGGING.SYSINFO, '----conf---=\n%s' % conf)
    logger.log(CUSTOM_LOGGING.SYSINFO, '----paths---=\n%s' % paths)
    logger.log(CUSTOM_LOGGING.SYSINFO, '----th---=\n%s' % th)
    debugPause()

def banner():
    _ = BANNER
    if not getattr(LOGGER_HANDLER, "is_tty", False):
        _ = re.sub("\033.+?m", "", _)
    # dataToStdout(_)
    sys.stdout.flush()
    print BANNER


def pollProcess(process, suppress_errors=False):
    """
    Checks for process status (prints > if still running)
    """

    while True:
        message = '>'
        sys.stdout.write(message)
        try:
            sys.stdout.flush()
        except IOError:
            pass

        time.sleep(1)

        returncode = process.poll()

        if returncode is not None:
            if not suppress_errors:
                if returncode == 0:
                    # TODO　print导致线程资源不安全
                    print " done\n"
                elif returncode < 0:
                    print " process terminated by signal %d\n" % returncode
                elif returncode > 0:
                    print " quit unexpectedly with return code %d\n" % returncode
            break

def getSafeExString(ex, encoding=None):
    """
    Safe way how to get the proper exception represtation as a string
    (Note: errors to be avoided: 1) "%s" % Exception(u'\u0161') and 2) "%s" % str(Exception(u'\u0161'))
    """

    retVal = ex

    if getattr(ex, "message", None):
        retVal = ex.message
    elif getattr(ex, "msg", None):
        retVal = ex.msg

    return getUnicode(retVal, encoding=encoding)


def getUnicode(value, encoding=None, noneToNull=False):
    """
    Return the unicode representation of the supplied value:

    >>> getUnicode(u'test')
    u'test'
    >>> getUnicode('test')
    u'test'
    >>> getUnicode(1)
    u'1'
    """

    if noneToNull and value is None:
        return NULL

    if isListLike(value):
        value = list(getUnicode(_, encoding, noneToNull) for _ in value)
        return value

    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        while True:
            try:
                return unicode(value, encoding or UNICODE_ENCODING)
            except UnicodeDecodeError, ex:
                try:
                    return unicode(value, UNICODE_ENCODING)
                except:
                    value = value[:ex.start] + "".join(INVALID_UNICODE_CHAR_FORMAT % ord(_) for _ in value[ex.start:ex.end]) + value[ex.end:]
    else:
        try:
            return unicode(value)
        except UnicodeDecodeError:
            return unicode(str(value), errors="ignore")  # encoding ignored for non-basestring instances


def isListLike(value):
    """
    Returns True if the given value is a list-like instance

    >>> isListLike([1, 2, 3])
    True
    >>> isListLike(u'2')
    False
    """

    return isinstance(value, (list, tuple, set))