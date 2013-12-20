"""
Functions and classes to record and print out log messages.

This module provides a own logger class as well as specific functions to
improve Pythons logging facility.

wxGlade uses the python logging instance with three log handler attached.

The first handler L{StringHandler} is used to cache messages later
displaying calling getBufferAsList() or getBufferAsString().

The second handler C{logging.StreamHandler} to print error messages to
sys.stderr.

The third handler C{logging.FileHandler} writes all messages into a file. This
behaviour is useful to store logged exceptions permanently.

@note: Python versions older then 2.6.6 (released 24th August 2010) contains
logging implementation that are not Unicode aware.
The Python bug report #8924 contains the details. A fix has been committed
in revision 81919 (27.12.2010) in the public Python repository.

@todo: Integrate Unicode logging fix.

@copyright: 2013 Carsten Grohmann
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import atexit
import cStringIO
import datetime
import inspect
import logging
import logging.handlers
import os
import pprint
import sys
import types

import config


stringLoggerInstance = None
"""\
Reference to the active StringHandler instance
"""

_orig_exec_handler = None
"""\
Contains the original exception handler

@see: L{installExceptionHandler()}
@see: L{deinstallExceptionHandler()}
"""


class StringHandler(logging.handlers.MemoryHandler):
    """\
    Stores the log records as a list of strings.
    """

    storeAsUnicode = True
    """\
    Stores the log records as unicode strings

    @type: Boolean
    """

    buffer = []
    """\
    The message buffer itself
    """

    encoding = sys.stdout.encoding or sys.getfilesystemencoding()
    """\
    Encoding of all character strings

    The default encoding is used to convert character strings into unicode
    strings.

    @see: L{storeAsUnicode}
    """

    def __init__(self, storeAsUnicode=True):
        """\
        Constructor

        @param storeAsUnicode: Store recorded log records as unicode strings
        """
        self.buffer = []
        logging.handlers.MemoryHandler.__init__(self, sys.maxint, 99)
        self.storeAsUnicode = storeAsUnicode

    def _toUnicode(self, msg):
        """\
        Convert a non unicode string into a unicode string

        @return: Unicode string
        @see: L{self.encoding}
        """
        # return msg if is already a unicode string or None
        if type(msg) in [types.UnicodeType, types.NoneType]:
            return msg

        # convert character string into a unicode string
        if not isinstance(msg, unicode):
            msg = msg.decode(self.encoding, 'replace')
        return msg

    def getBufferAsList(self, clean=True):
        """\
        Returns all buffered messages

        @param clean: Clean the internal message buffer
        @return:      Message buffer
        @rtype:       List of strings

        @see: L{getBufferAsString()}
        """
        self.acquire()
        try:
            messages = self.buffer[:]
            if clean:
                self.flush()
        finally:
            self.release()
        return messages

    def getBufferAsString(self, clean=True):
        """\
        Returns all buffered messages

        @param clean: Clean the internal message buffer
        @return:      Concatenated messages
        @rtype:       String

        @see: L{getBufferAsList()}
        """
        msg_list = self.getBufferAsList(clean)
        if self.storeAsUnicode:
            return u'\n'.join(msg_list)
        return '\n'.join(msg_list)

    def emit(self, record):
        """\
        Emit a record.

        Add a formatted log record to the buffer.
        """
        msg = self.format(record)
        if self.storeAsUnicode:
            msg = self._toUnicode(msg)
        self.buffer.append(msg)
        if self.shouldFlush(record):
            self.flush()

    def flush(self):
        """\
        Empty the buffer
        """
        self.buffer = []

# end of class StringHandler


class wxGladeFormatter(logging.Formatter):
    """\
    Extended formatter to include more exception details automatically.
    """

    def formatException(self, ei):
        """
        Returns a detailed exception

        @param ei: Tuple or list of exc_type, exc_value, exc_tb
        @return: Formatted exception
        @rtype:  String
        """
        context = None
        exc_tb = ei[2]
        exc_type = ei[0]
        exc_value = ei[1]
        filename = None
        frame = None
        func_args = None
        func_name = None
        index = None
        lineno = None
        sio = cStringIO.StringIO()
        stack_level = 0
        stack_list = []
        var = None
        var_name = None
        var_type = None
        var_value = None
        try:
            try:
                # log exception details
                now = datetime.datetime.now().isoformat()
                sio.write(_('An unexpected error occurred!\n'))
                sio.write('\n')
                sio.write(_('Date and time:      %s\n') % now)
                sio.write(_('Python version:     %s\n') % config.py_version)
                sio.write(_('wxPython version:   %s\n') % config.wx_version)
                sio.write(_('wxWidgets platform: %s\n') % config.platform)
                sio.write(_('wxGlade version:    %s\n') % config.version)
                sio.write('\n')
                sio.write(_('Exception type:    %s\n') % exc_type)
                sio.write(_('Exception details: %s\n') % exc_value)
                sio.write(_('Application stack trace:\n'))

                # leave the exception handler if no traceback is available
                if not exc_tb:
                    return

                # get stack frames
                stack_list = inspect.getinnerframes(exc_tb, 7)
                stack_list.reverse()
                stack_level=-1

                for frame, filename, lineno, func_name, context, index in stack_list:
                    stack_level += 1
                    func_args = inspect.formatargvalues(
                        *inspect.getargvalues(frame)
                    )

                    msg = _('Stack frame at level %d' % stack_level)
                    sio.write('%s\n' % msg)
                    msg = '=' * len(msg)
                    sio.write('%s\n' % msg)
                    sio.write(_('  File "%s", line %d\n') % (filename, lineno))
                    sio.write(_('  Function "%s%s"\n') % (func_name, func_args))
                    sio.write(_('  Source code context:\n'))

                    pos = 0
                    for line in context:
                        line = line.rstrip()
                        if pos == index:
                            sio.write('  ->  %s\n' % line)
                        else:
                            sio.write('      %s\n' % line)
                        pos += 1

                    if frame.f_locals:
                        sio.write(_('  Local variables:\n'))
                        for var_name in frame.f_locals:
                            # convert name and value to ascii characters
                            var = frame.f_locals[var_name]
                            var_type = type(var)
                            if var_type == types.UnicodeType:
                                var_value = frame.f_locals[var_name]
                                var_value = var_value.encode('unicode_escape')
                            elif var_type == types.StringType:
                                var_value = frame.f_locals[var_name]
                                var_value = var_value.encode('string-escape')
                            else:
                                var_value = pprint.pformat(frame.f_locals[var_name])
                                var_value = var_value
                            sio.write(_('  -> %s (%s): %s\n') % (
                                var_name, var_type, var_value)
                            )
                    else:
                        sio.write(_('  No local variables\n'))
                    sio.write('\n')
            except Exception, e:
                # This code should NEVER be executed!
                logging.error('Some strange things occurred: %s', e)
                sys.exit(1)

        # delete local references of trace backs or part of them  to avoid
        # circular references
        finally:
            del context
            del ei
            del exc_tb
            del exc_type,
            del exc_value,
            del filename
            del frame
            del func_args
            del func_name
            del index
            del lineno
            del stack_level
            del stack_list
            del var
            del var_name
            del var_type
            del var_value

        s = sio.getvalue()
        sio.close()
        if s[-1] == "\n":
            s = s[:-1]
        return s

# end of class wxGladeFormatter


def init(filename='wxglade.log', encoding=None, level=None):
    """\
    Initialise the logging facility

    Initialise and configure the logging itself as well as the handlers
    described above.

    Our own exception handler will be installed finally.

    The file logger won't be instantiate if not file name is given.

    @param filename: Name of the log file
    @type filename:  String
    @param encoding: Encoding of the log file
    @type encoding:  String
    @param level:    Verbosity of messages written in log file e.g. "INFO"
    @type level:     String

    @see: L{StringHandler}
    @see: L{stringLoggerInstance}
    @see: L{installExceptionHandler()}
    """
    global stringLoggerInstance

    default_formatter = wxGladeFormatter(
        '%(levelname)-8s: %(message)s'
        )
    file_formatter = wxGladeFormatter(
        '%(asctime)s %(name)s %(levelname)s: %(message)s'
        )
    logger = logging.getLogger()

    # check for installed handlers and remove them
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # set newline sequence
    if os.name == 'nt':
        logging.StreamHandler.terminator = '\r\n'
    elif os.name == 'mac':
        logging.StreamHandler.terminator = '\r'
    else:
        logging.StreamHandler.terminator = '\n'

    # inject own function
    logging.LogRecord.getMessage = getMessage

    # install own exception handler
    installExceptionHandler()

    # instantiate own handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(default_formatter)
    logger.addHandler(console)

    if filename:
        fileLogger = logging.handlers.RotatingFileHandler(
            filename,
            maxBytes=100*1024,
            encoding=encoding,
            backupCount=1,
            )
        fileLogger.setFormatter(file_formatter)
        fileLogger.setLevel(logging.NOTSET)
        logger.addHandler(fileLogger)

    stringLoggerInstance = StringHandler(storeAsUnicode=False)
    stringLoggerInstance.setLevel(logging.WARNING)
    stringLoggerInstance.setFormatter(default_formatter)
    logger.addHandler(stringLoggerInstance)

    # don't filter log levels in root logger
    logger.setLevel(logging.NOTSET)

    # Set log level for file logger only
    if level:
        if level.upper() in logging._levelNames:                 # pylint: disable=W0212
            logger.setLevel(logging._levelNames[level.upper()])  # pylint: disable=W0212
        else:
            logging.warning(
                _('Invalid log level "%s". Use "WARNING" instead.'),
                level.upper(),
                )
            logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.NOTSET)


def deinit():
    """\
    Reactivate system exception handler

    @see: L{deinstallExceptionHandler()}
    """
    deinstallExceptionHandler()
    if deinit in atexit._exithandlers:
        atexit._exithandlers.remove(deinit)


def setDebugLevel():
    """\
    Set the log level to DEBUG for all log handlers
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)


def getBufferAsList(clean=True):
    """\
    Returns all messages buffered by L{stringLoggerInstance}.

    @param clean: Clean the internal message buffer
    @return:      Message buffer
    @rtype:       List of strings

    @see: L{StringHandler.getBufferAsList()}
    @see: L{stringLoggerInstance}
    """
    return stringLoggerInstance.getBufferAsList(clean)


def getBufferAsString(clean=True):
    """\
    Returns all messages buffered by L{stringLoggerInstance}.

    @param clean: Clean the internal message buffer
    @return:      Concatenated messages
    @rtype:       String

    @see: L{StringHandler.getBufferAsString()}
    @see: L{stringLoggerInstance}
    """
    return stringLoggerInstance.getBufferAsString(clean)


def flush():
    """\
    Empty the buffer of the L{stringLoggerInstance}.

    @see: L{StringHandler.flush()}
    @see: L{stringLoggerInstance}
    """
    stringLoggerInstance.flush()


def installExceptionHandler():
    """\
    Install own exception handler

    The original exception handler is saved in L{_orig_exec_handler}.

    @see: L{_orig_exec_handler}
    @see: L{deinstallExceptionHandler()}
    """
    global _orig_exec_handler
    if _orig_exec_handler:
        logging.debug(
            _('The exception handler has been installed already.'),
            )
        return

    _orig_exec_handler = sys.excepthook
    sys.excepthook = exceptionHandler


def deinstallExceptionHandler():
    """\
   Restore the original exception handler

   The original exception handler has been saved in L{_orig_exec_handler}.

   @see: L{_orig_exec_handler}
   @see: L{installExceptionHandler()}
    """
    global _orig_exec_handler
    if not _orig_exec_handler:
        logging.debug(
            _('The exception handler has not been installed.'
              'Thereby it can not be deinstalled.'),
            )
        return

    sys.excepthook = _orig_exec_handler
    _orig_exec_handler = None


def exceptionHandler(exc_type, exc_value, exc_tb):
    """\
    Log detailed information about uncaught exceptions

    @param exc_type:  Type of the exception (normally a class object)
    @param exc_value: The "value" of the exception
    @param exc_tb:    Call stack of the exception
    """
    logging.error(
        _("An unhandled exception occurred"),
        exc_info=(exc_type, exc_value, exc_tb)
    )


def getMessage(self):
    """\
    Return the message for this LogRecord.

    Return the message for this LogRecord after merging any user-supplied
    arguments with the message.

    This specific version tries to handle Unicode user-supplied arguments.
    """
    if not hasattr(types, "UnicodeType"):  # if no unicode support...
        msg = str(self.msg)
    else:
        msg = self.msg
        if type(msg) not in (types.UnicodeType, types.StringType):
            try:
                msg = str(self.msg)
            except UnicodeError:
                msg = self.msg      # Defer encoding till later
    if self.args:
        try:
            msg = msg % self.args
        except UnicodeError:
            # TODO it's still an hack :-/
            logging.error(_('Unknown format of arguments: %s'), self.args)
        except TypeError:
            # Errors caused by wrong message formatting
            logging.exception(_('Wrong format of a log message'))
    return msg
