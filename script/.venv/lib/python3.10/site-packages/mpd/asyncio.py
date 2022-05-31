"""Asynchronous access to MPD using the asyncio methods of Python 3.

Interaction happens over the mpd.asyncio.MPDClient class, whose connect and
command methods are coroutines.

Some commands (eg. listall) additionally support the asynchronous iteration
(aiter, `async for`) interface; using it allows the library user to obtain
items of result as soon as they arrive.

The .idle() method works differently here: It is an asynchronous iterator that
produces a list of changed subsystems whenever a new one is available. The
MPDClient object automatically switches in and out of idle mode depending on
which subsystems there is currently interest in.

Command lists are currently not supported.


This module requires Python 3.5.2 or later to run.
"""

import warnings
import asyncio
from functools import partial
from typing import Optional, List, Tuple, Iterable, Callable, Union

from mpd.base import HELLO_PREFIX, ERROR_PREFIX, SUCCESS
from mpd.base import MPDClientBase
from mpd.base import MPDClient as SyncMPDClient
from mpd.base import ProtocolError, ConnectionError, CommandError
from mpd.base import mpd_command_provider


class BaseCommandResult(asyncio.Future):
    """A future that carries its command/args/callback with it for the
    convenience of passing it around to the command queue."""

    def __init__(self, command, args, callback):
        super().__init__()
        self._command = command
        self._args = args
        self._callback = callback

    async def _feed_from(self, mpdclient):
        while True:
            line = await mpdclient._read_line()
            self._feed_line(line)
            if line is None:
                return


class CommandResult(BaseCommandResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__spooled_lines = []

    def _feed_line(self, line): # FIXME just inline?
        """Put the given line into the callback machinery, and set the result on a None line."""
        if line is None:
            if self.cancelled():
                # Data was still pulled out of the connection, but the original
                # requester has cancelled the request -- no need to filter the
                # data through the preprocessing callback
                pass
            else:
                self.set_result(self._callback(self.__spooled_lines))
        else:
            self.__spooled_lines.append(line)

    def _feed_error(self, error):
        if not self.done():
            self.set_exception(error)
        else:
            # These do occur (especially during the test suite run) when a
            # disconnect was already initialized, but the run task being
            # cancelled has not ever yielded at all and thus still needs to run
            # through to its first await point (which is then in a situation
            # where properties it'd like to access are already cleaned up,
            # resulting in an AttributeError)
            #
            # Rather than quenching them here, they are made visible (so that
            # other kinds of double errors raise visibly, even though none are
            # known right now); instead, the run loop yields initially with a
            # sleep(0) that ensures it can be cancelled properly at any time.
            raise error

class BinaryCommandResult(asyncio.Future):
    # Unlike the regular commands that defer to any callback that may be
    # defined for them, this uses the predefined _read_binary mechanism of the
    # mpdclient
    async def _feed_from(self, mpdclient):
        # Data must be pulled out no matter whether will later be ignored or not
        binary = await mpdclient._read_binary()
        if self.cancelled():
            pass
        else:
            self.set_result(binary)

    _feed_error = CommandResult._feed_error

class CommandResultIterable(BaseCommandResult):
    """Variant of CommandResult where the underlying callback is an
    asynchronous` generator, and can thus interpret lines as they come along.

    The result can be used with the aiter interface (`async for`). If it is
    still used as a future instead, it eventually results in a list.

    Commands used with this CommandResult must use their passed lines not like
    an iterable (as in the synchronous implementation), but as a asyncio.Queue.
    Furthermore, they must check whether the queue elements are exceptions, and
    raise them.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__spooled_lines = asyncio.Queue()

    def _feed_line(self, line):
        self.__spooled_lines.put_nowait(line)

    _feed_error = _feed_line

    def __await__(self):
        asyncio.Task(self.__feed_future())
        return super().__await__()

    __iter__ = __await__  # for 'yield from' style invocation

    async def __feed_future(self):
        result = []
        try:
            async for r in self:
                result.append(r)
        except Exception as e:
            self.set_exception(e)
        else:
            if not self.cancelled():
                self.set_result(result)

    def __aiter__(self):
        if self.done():
            raise RuntimeError("Command result is already being consumed")
        return self._callback(self.__spooled_lines).__aiter__()


@mpd_command_provider
class MPDClient(MPDClientBase):
    __run_task = None  # doubles as indicator for being connected

    #: Indicator of whether there is a pending idle command that was not terminated yet.
    # When in doubt; this is True, thus erring at the side of caution (because
    # a "noidle" being sent while racing against an incoming idle notification
    # does no harm)
    __in_idle = False

    #: Indicator that the last attempted idle failed.
    #
    # When set, IMMEDIATE_COMMAND_TIMEOUT is ignored in favor of waiting until
    # *something* else happens, and only then retried.
    #
    # Note that the only known condition in which this happens is when between
    # start of the connection and the presentation of credentials, more than
    # IMMEDIATE_COMMAND_TIMEOUT passes.
    __idle_failed = False

    #: Seconds after a command's completion to send idle. Setting this too high
    # causes "blind spots" in the client's view of the server, setting it too
    # low sends needless idle/noidle after commands in quick succession.
    IMMEDIATE_COMMAND_TIMEOUT = 0.1

    #: FIFO list of processors that may consume the read stream one after the
    # other
    #
    # As we don't have any other form of backpressure in the sending side
    # (which is not expected to be limited), its limit of COMMAND_QUEUE_LENGTH
    # serves as a limit against commands queuing up indefinitely. (It's not
    # *directly* throttling output, but as the convention is to put the
    # processor on the queue and then send the command, and commands are of
    # limited size, this is practically creating backpressure.)
    __command_queue = None

    #: Construction size of __command_queue. The default limit is high enough
    # that a client can easily send off all existing commands simultaneously
    # without needlessly blocking the TCP flow, but small enough that
    # freespinning tasks create warnings.
    COMMAND_QUEUE_LENGTH = 128

    #: Callbacks registered by any current callers of `idle()`.
    #
    # The first argument lists the changes that the caller is interested in
    # (and all current listeners' union is used to populate the `idle`
    # command's arguments), the latter is an actual callback that will be
    # passed either a set of changes or an exception.
    __idle_consumers: Optional[List[Tuple[
        Iterable[str],
        Callable[[Union[List[str], Exception]], None]
        ]]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__rfile = self.__wfile = None

    async def connect(self, host, port=6600, loop=None):
        if loop is not None:
            warnings.warn("loop passed into MPDClient.connect is ignored, this will become an error", DeprecationWarning)
        if "/" in host:
            r, w = await asyncio.open_unix_connection(host)
        else:
            r, w = await asyncio.open_connection(host, port)
        self.__rfile, self.__wfile = r, w

        self.__command_queue = asyncio.Queue(maxsize=self.COMMAND_QUEUE_LENGTH)
        self.__idle_consumers = []  #: list of (subsystem-list, callbacks) tuples

        try:
            helloline = await asyncio.wait_for(self.__readline(), timeout=5)
        except asyncio.TimeoutError:
            self.disconnect()
            raise ConnectionError("No response from server while reading MPD hello")
        # FIXME should be reusable w/o reaching in
        SyncMPDClient._hello(self, helloline)

        self.__run_task = asyncio.Task(self.__run())

    @property
    def connected(self):
        return self.__run_task is not None

    def disconnect(self):
        if (
            self.__run_task is not None
        ):  # is None eg. when connection fails in .connect()
            self.__run_task.cancel()
        if self.__wfile is not None:
            self.__wfile.close()
        self.__rfile = self.__wfile = None
        self.__run_task = None
        self.__command_queue = None
        if self.__idle_consumers is not None:
            # copying the list as each raising callback will remove itself from __idle_consumers
            for subsystems, callback in list(self.__idle_consumers):
                callback(ConnectionError())
        self.__idle_consumers = None

    def _get_idle_interests(self):
        """Accumulate a set of interests from the current __idle_consumers.
        Returns the union of their subscribed subjects, [] if at least one of
        them is the empty catch-all set, or None if there are no interests at
        all."""

        if not self.__idle_consumers:
            return None
        if any(len(s) == 0 for (s, c) in self.__idle_consumers):
            return []
        return set.union(*(set(s) for (s, c) in self.__idle_consumers))

    def _end_idle(self):
        """If the main task is currently idling, make it leave idle and process
        the next command (if one is present) or just restart idle"""

        if self.__in_idle:
            self.__write("noidle\n")
            self.__in_idle = False

    async def __run(self):
        # See CommandResult._feed_error documentation
        await asyncio.sleep(0)
        result = None

        try:
            while True:
                try:
                    result = await asyncio.wait_for(
                        self.__command_queue.get(),
                        timeout=self.IMMEDIATE_COMMAND_TIMEOUT,
                    )
                except asyncio.TimeoutError:
                    # The cancellation of the __command_queue.get() that happens
                    # in this case is intended, and is just what asyncio.Queue
                    # suggests for "get with timeout".

                    if self.__idle_failed:
                        # We could try for a more elaborate path where we now
                        # await the command queue indefinitely, but as we're
                        # already in an error case, this whole situation only
                        # persists until the error is processed somewhere else,
                        # so ticking once per idle timeout is OK to keep things
                        # simple.
                        continue

                    subsystems = self._get_idle_interests()
                    if subsystems is None:
                        # The presumably most quiet subsystem -- in this case,
                        # idle is only used to keep the connection alive.
                        subsystems = ["database"]

                    # Careful: There can't be any await points between the
                    # except and here, or the sequence between the idle and the
                    # command processor might be wrong.
                    result = CommandResult("idle", subsystems, self._parse_list)
                    result.add_done_callback(self.__idle_result)
                    self.__in_idle = True
                    self._write_command(result._command, result._args)

                # A new command was issued, so there's a chance that whatever
                # made idle fail is now fixed.
                self.__idle_failed = False

                try:
                    await result._feed_from(self)
                except CommandError as e:
                    result._feed_error(e)
                    # This kind of error we can tolerate without breaking up
                    # the connection; any other would fly out, be reported
                    # through the result and terminate the connection

        except Exception as e:
            # Prevent the destruction of the pending task in the shutdown
            # function -- it's just shutting down by itself.
            self.__run_task = None
            self.disconnect()

            if result is not None:
                # The last command has failed: Forward that result.
                #
                # (In idle, that's fine too -- everyone watching see a
                # nonspecific event).
                result._feed_error(e)
                return
            else:
                raise
                # Typically this is a bug in mpd.asyncio.

    def __idle_result(self, result):
        try:
            idle_changes = result.result()
        except CommandError as e:
            # Don't retry until something changed
            self.__idle_failed = True

            # Not raising this any further: The callbacks are notified that
            # "something is up" (which is all their API gives), and whichever
            # command is issued to act on it will hopefully run into the same
            # condition.
            #
            # This does swallow the exact error cause.

            idle_changes = set()
            for subsystems, _ in self.__idle_consumers:
                idle_changes = idle_changes.union(subsystems)

        # make generator accessible multiple times
        idle_changes = list(idle_changes)

        for subsystems, callback in self.__idle_consumers:
            if not subsystems or any(s in subsystems for s in idle_changes):
                callback(idle_changes)

    # helper methods

    async def __readline(self):
        """Wrapper around .__rfile.readline that handles encoding"""
        data = await self.__rfile.readline()
        try:
            return data.decode("utf8")
        except UnicodeDecodeError:
            self.disconnect()
            raise ProtocolError("Invalid UTF8 received")

    async def _read_chunk(self, length):
        try:
            return await self.__rfile.readexactly(length)
        except asyncio.IncompleteReadError:
            raise ConnectionError("Connection lost while reading binary")

    def __write(self, text):
        """Wrapper around .__wfile.write that handles encoding."""
        self.__wfile.write(text.encode("utf8"))

    # copied and subtly modifiedstuff from base

    # This is just a wrapper for the below.
    def _write_line(self, text):
        self.__write(text + "\n")

    # FIXME This code should be shareable.
    _write_command = SyncMPDClient._write_command

    async def _read_line(self):
        line = await self.__readline()
        if not line.endswith("\n"):
            raise ConnectionError("Connection lost while reading line")
        line = line.rstrip("\n")
        if line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX) :].strip()
            raise CommandError(error)
        if line == SUCCESS:
            return None
        return line

    async def _parse_objects_direct(self, lines, delimiters=[], lookup_delimiter=False):
        obj = {}
        while True:
            line = await lines.get()
            if isinstance(line, BaseException):
                raise line
            if line is None:
                break
            key, value = self._parse_pair(line, separator=": ")
            key = key.lower()
            if lookup_delimiter and not delimiters:
                delimiters = [key]
            if obj:
                if key in delimiters:
                    yield obj
                    obj = {}
                elif key in obj:
                    if not isinstance(obj[key], list):
                        obj[key] = [obj[key], value]
                    else:
                        obj[key].append(value)
                    continue
            obj[key] = value
        if obj:
            yield obj

    async def _execute_binary(self, command, args):
        # Fun fact: By fetching data in lockstep, this is a bit less efficient
        # than it could be (which would be "after having received the first
        # chunk, guess that the other chunks are of equal size and request at
        # several multiples concurrently, ensuring the TCP connection can stay
        # full), but at the other hand it leaves the command queue empty so
        # that more time critical commands can be executed right away

        data = None
        args = list(args)
        assert len(args) == 1
        args.append(0)
        final_metadata = None
        while True:
            partial_result = BinaryCommandResult()
            await self.__command_queue.put(partial_result)
            self._end_idle()
            self._write_command(command, args)
            metadata = await partial_result
            chunk = metadata.pop('binary', None)

            if final_metadata is None:
                data = chunk
                final_metadata = metadata
                if not data:
                    break
                try:
                    size = int(final_metadata['size'])
                except KeyError:
                    size = len(chunk)
                except ValueError:
                    raise CommandError("Size data unsuitable for binary transfer")
            else:
                if metadata != final_metadata:
                    raise CommandError("Metadata of binary data changed during transfer")
                if chunk is None:
                    raise CommandError("Binary field vanished changed during transfer")
                data += chunk
            args[-1] = len(data)
            if len(data) > size:
                raise CommandListError("Binary data announced size exceeded")
            elif len(data) == size:
                break

        if data is not None:
            final_metadata['binary'] = data

        final_metadata.pop('size', None)

        return final_metadata

    # omits _read_chunk checking because the async version already
    # raises; otherwise it's just awaits sprinkled in
    async def _read_binary(self):
        obj = {}

        while True:
            line = await self._read_line()
            if line is None:
                break

            key, value = self._parse_pair(line, ": ")

            if key == "binary":
                chunk_size = int(value)
                value = await self._read_chunk(chunk_size)

                if await self.__rfile.readexactly(1) != b"\n":
                    # newline after binary content
                    self.disconnect()
                    raise ConnectionError("Connection lost while reading line")

            obj[key] = value
        return obj

    # command provider interface
    @classmethod
    def add_command(cls, name, callback):
        if callback.mpd_commands_binary:
            async def f(self, *args):
                result = await self._execute_binary(name, args)

                # With binary, the callback is applied to the final result
                # rather than to the iterator over the lines (cf.
                # MPDClient._execute_binary)
                return callback(self, result)
        else:
            command_class = (
                CommandResultIterable if callback.mpd_commands_direct else CommandResult
            )
            if hasattr(cls, name):
                # Idle and noidle are explicitly implemented, skipping them.
                return

            def f(self, *args):
                result = command_class(name, args, partial(callback, self))
                if self.__run_task is None:
                    raise ConnectionError("Can not send command to disconnected client")

                try:
                    self.__command_queue.put_nowait(result)
                except asyncio.QueueFull as e:
                    e.args = ("Command queue overflowing; this indicates the"
                            " application sending commands in an uncontrolled"
                            " fashion without awaiting them, and typically"
                            " indicates a memory leak.",)
                    # While we *could* indicate to the queued result that it has
                    # yet to send its request, that'd practically create a queue of
                    # awaited items in the user application that's growing
                    # unlimitedly, eliminating any chance of timely responses.
                    # Furthermore, the author sees no practical use case that's not
                    # violating MPD's guidance of "Do not manage a client-side copy
                    # of MPD's database". If a use case *does* come up, any change
                    # would need to maintain the property of providing backpressure
                    # information. That would require an API change.
                    raise

                self._end_idle()
                # Careful: There can't be any await points between the queue
                # appending and the write
                try:
                    self._write_command(result._command, result._args)
                except BaseException as e:
                    self.disconnect()
                    result.set_exception(e)
                return result

        escaped_name = name.replace(" ", "_")
        f.__name__ = escaped_name
        setattr(cls, escaped_name, f)

    # commands that just work differently
    async def idle(self, subsystems=()):
        if self.__idle_consumers is None:
            raise ConnectionError("Can not start idle on a disconnected client")

        interests_before = self._get_idle_interests()
        # A queue accepting either a list of things that changed in a single
        # idle cycle, or an exception to be raised
        changes = asyncio.Queue()
        try:
            entry = (subsystems, changes.put_nowait)
            self.__idle_consumers.append(entry)
            if self._get_idle_interests != interests_before:
                # Technically this does not enter idle *immediately* but rather
                # only after any commands after IMMEDIATE_COMMAND_TIMEOUT;
                # practically that should be a good thing.
                self._end_idle()
            while True:
                item = await changes.get()
                if isinstance(item, Exception):
                    raise item
                yield item
        finally:
            if self.__idle_consumers is not None:
                self.__idle_consumers.remove(entry)

    def noidle(self):
        raise AttributeError("noidle is not supported / required in mpd.asyncio")
