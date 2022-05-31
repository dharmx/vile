#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import itertools
import mpd
import mpd.asyncio
import os
import socket
import sys
import types
import warnings

import unittest
from unittest import mock

try:
    from twisted.python.failure import Failure

    TWISTED_MISSING = False
except ImportError:
    warnings.warn(
        "No twisted installed: skip twisted related tests! "
        + "(twisted is not available for python >= 3.0 && python < 3.3)"
    )
    TWISTED_MISSING = True

import asyncio


# show deprecation warnings
warnings.simplefilter("default")


TEST_MPD_HOST, TEST_MPD_PORT = ("example.com", 10000)
TEST_MPD_UNIXHOST = "/example/test/host"
TEST_MPD_UNIXTIMEOUT = 0.5


class TestMPDClient(unittest.TestCase):

    longMessage = True

    def setUp(self):
        self.socket_patch = mock.patch("mpd.base.socket")
        self.socket_mock = self.socket_patch.start()
        self.socket_mock.getaddrinfo.return_value = [range(5)]

        self.socket_mock.socket.side_effect = (
            lambda *a, **kw:
            # Create a new socket.socket() mock with default attributes,
            # each time we are calling it back (otherwise, it keeps set
            # attributes across calls).
            # That's probably what we want, since reconnecting is like
            # reinitializing the entire connection, and so, the mock.
            mock.MagicMock(name="socket.socket")
        )

        self.client = mpd.MPDClient()
        self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT)
        self.client._sock.reset_mock()
        self.MPDWillReturn("ACK don't forget to setup your mock\n")

    def tearDown(self):
        self.socket_patch.stop()

    def MPDWillReturn(self, *lines):
        # Return what the caller wants first, then do as if the socket was
        # disconnected.
        innerIter = itertools.chain(lines, itertools.repeat(""))
        if sys.version_info >= (3, 0):
            self.client._rbfile.readline.side_effect = (
                x.encode("utf-8") for x in innerIter
            )
        else:
            self.client._rbfile.readline.side_effect = innerIter

    def assertMPDReceived(self, *lines):
        self.client._wfile.write.assert_called_with(*lines)

    def test_abstract_functions(self):
        MPDClientBase = mpd.base.MPDClientBase
        self.assertRaises(
            NotImplementedError,
            lambda: MPDClientBase.add_command("command_name", lambda x: x),
        )
        client = MPDClientBase()
        self.assertRaises(NotImplementedError, lambda: client.noidle())
        self.assertRaises(NotImplementedError, lambda: client.command_list_ok_begin())
        self.assertRaises(NotImplementedError, lambda: client.command_list_end())

    def test_metaclass_commands(self):
        # just some random functions
        self.assertTrue(hasattr(self.client, "commands"))
        self.assertTrue(hasattr(self.client, "save"))
        self.assertTrue(hasattr(self.client, "random"))
        # space should be replaced
        self.assertFalse(hasattr(self.client, "sticker get"))
        self.assertTrue(hasattr(self.client, "sticker_get"))

    def test_duplicate_tags(self):
        self.MPDWillReturn("Track: file1\n", "Track: file2\n", "OK\n")
        song = self.client.currentsong()
        self.assertIsInstance(song, dict)
        self.assertIsInstance(song["track"], list)
        self.assertMPDReceived("currentsong\n")

    def test_parse_nothing(self):
        self.MPDWillReturn("OK\n", "OK\n")

        self.assertIsNone(self.client.ping())
        self.assertMPDReceived("ping\n")

        self.assertIsNone(self.client.clearerror())
        self.assertMPDReceived("clearerror\n")

    def test_parse_list(self):
        self.MPDWillReturn(
            "tagtype: Artist\n", "tagtype: ArtistSort\n", "tagtype: Album\n", "OK\n"
        )

        result = self.client.tagtypes()
        self.assertMPDReceived("tagtypes\n")
        self.assertIsInstance(result, list)
        self.assertEqual(result, ["Artist", "ArtistSort", "Album",])

    def test_parse_list_groups(self):
        self.MPDWillReturn(
            "Album: \n",
            "Album: 20th_Century_Masters_The_Millenium_Collection\n",
            "Album: Aerosmith's Greatest Hits\n",
            "OK\n",
        )

        result = self.client.list("album")
        self.assertMPDReceived('list "album"\n')
        self.assertIsInstance(result, list)
        self.assertEqual(
            result,
            [
                {"album": ""},
                {"album": "20th_Century_Masters_The_Millenium_Collection"},
                {"album": "Aerosmith's Greatest Hits"},
            ],
        )

        self.MPDWillReturn(
            "Album: \n",
            "Album: 20th_Century_Masters_The_Millenium_Collection\n",
            "Artist: Eric Clapton\n",
            "Album: Aerosmith's Greatest Hits\n",
            "Artist: Aerosmith\n",
            "OK\n",
        )

        result = self.client.list("album", "group", "artist")
        self.assertMPDReceived('list "album" "group" "artist"\n')
        self.assertIsInstance(result, list)
        self.assertEqual(
            result,
            [
                {"album": ""},
                {
                    "album": "20th_Century_Masters_The_Millenium_Collection",
                    "artist": "Eric Clapton",
                },
                {"album": "Aerosmith's Greatest Hits", "artist": "Aerosmith"},
            ],
        )

    def test_parse_item(self):
        self.MPDWillReturn("updating_db: 42\n", "OK\n")
        self.assertIsNotNone(self.client.update())

    def test_parse_object(self):
        # XXX: _read_objects() doesn't wait for the final OK
        self.MPDWillReturn("volume: 63\n", "OK\n")
        status = self.client.status()
        self.assertMPDReceived("status\n")
        self.assertIsInstance(status, dict)

        # XXX: _read_objects() doesn't wait for the final OK
        self.MPDWillReturn("OK\n")
        stats = self.client.stats()
        self.assertMPDReceived("stats\n")
        self.assertIsInstance(stats, dict)

    def test_parse_songs(self):
        self.MPDWillReturn("file: my-song.ogg\n", "Pos: 0\n", "Id: 66\n", "OK\n")
        playlist = self.client.playlistinfo()

        self.assertMPDReceived("playlistinfo\n")
        self.assertIsInstance(playlist, list)
        self.assertEqual(1, len(playlist))
        e = playlist[0]
        self.assertIsInstance(e, dict)
        self.assertEqual("my-song.ogg", e["file"])
        self.assertEqual("0", e["pos"])
        self.assertEqual("66", e["id"])

    def test_readcomments(self):
        self.MPDWillReturn(
            "major_brand: M4V\n", "minor_version: 1\n", "lyrics: Lalala\n", "OK\n"
        )
        comments = self.client.readcomments()
        self.assertMPDReceived("readcomments\n")
        self.assertEqual(comments["major_brand"], "M4V")
        self.assertEqual(comments["minor_version"], "1")
        self.assertEqual(comments["lyrics"], "Lalala")

    def test_iterating(self):
        self.MPDWillReturn("file: my-song.ogg\n", "Pos: 0\n", "Id: 66\n", "OK\n")
        self.client.iterate = True
        playlist = self.client.playlistinfo()
        self.assertMPDReceived("playlistinfo\n")
        self.assertIsInstance(playlist, types.GeneratorType)
        for song in playlist:
            self.assertIsInstance(song, dict)
            self.assertEqual("my-song.ogg", song["file"])
            self.assertEqual("0", song["pos"])
            self.assertEqual("66", song["id"])

    def test_add_and_remove_command(self):
        self.MPDWillReturn("ACK awesome command\n")

        self.client.add_command("awesome command", mpd.MPDClient._parse_nothing)
        self.assertTrue(hasattr(self.client, "awesome_command"))
        # should be unknown by mpd
        self.assertRaises(mpd.CommandError, self.client.awesome_command)

        self.client.remove_command("awesome_command")
        self.assertFalse(hasattr(self.client, "awesome_command"))

        # remove non existing command
        self.assertRaises(ValueError, self.client.remove_command, "awesome_command")

    def test_partitions(self):
        self.MPDWillReturn("partition: default\n", "partition: partition2\n", "OK\n")
        partitions = self.client.listpartitions()
        self.assertMPDReceived("listpartitions\n")
        self.assertEqual(
            [
                {"partition": "default"},
                {"partition": "partition2"},
            ],
            partitions
        )

        self.MPDWillReturn("OK\n")
        self.assertIsNone(self.client.newpartition("Another Partition"))
        self.assertMPDReceived('newpartition "Another Partition"\n')

        self.MPDWillReturn("OK\n")
        self.assertIsNone(self.client.partition("Another Partition"))
        self.assertMPDReceived('partition "Another Partition"\n')

        self.MPDWillReturn("OK\n")
        self.assertIsNone(self.client.delpartition("Another Partition"))
        self.assertMPDReceived('delpartition "Another Partition"\n')

        self.MPDWillReturn("OK\n")
        self.assertIsNone(self.client.moveoutput("My ALSA Device"))
        self.assertMPDReceived('moveoutput "My ALSA Device"\n')

    def test_client_to_client(self):
        # client to client is at this time in beta!

        self.MPDWillReturn("OK\n")
        self.assertIsNone(self.client.subscribe("monty"))
        self.assertMPDReceived('subscribe "monty"\n')

        self.MPDWillReturn("channel: monty\n", "OK\n")
        channels = self.client.channels()
        self.assertMPDReceived("channels\n")
        self.assertEqual(["monty"], channels)

        self.MPDWillReturn("OK\n")
        self.assertIsNone(self.client.sendmessage("monty", "SPAM"))
        self.assertMPDReceived('sendmessage "monty" "SPAM"\n')

        self.MPDWillReturn("channel: monty\n", "message: SPAM\n", "OK\n")
        msg = self.client.readmessages()
        self.assertMPDReceived("readmessages\n")
        self.assertEqual(msg, [{"channel": "monty", "message": "SPAM"}])

        self.MPDWillReturn("OK\n")
        self.assertIsNone(self.client.unsubscribe("monty"))
        self.assertMPDReceived('unsubscribe "monty"\n')

        self.MPDWillReturn("OK\n")
        channels = self.client.channels()
        self.assertMPDReceived("channels\n")
        self.assertEqual([], channels)

    def test_unicode_as_command_args(self):
        self.MPDWillReturn("OK\n")
        res = self.client.find("file", "☯☾☝♖✽")
        self.assertIsInstance(res, list)
        self.assertMPDReceived('find "file" "☯☾☝♖✽"\n')

    def test_numbers_as_command_args(self):
        self.MPDWillReturn("OK\n")
        self.client.find("file", 1)
        self.assertMPDReceived('find "file" "1"\n')

    def test_commands_without_callbacks(self):
        self.MPDWillReturn("\n")
        self.client.close()
        self.assertMPDReceived("close\n")

        # XXX: what are we testing here?
        #      looks like reconnection test?
        self.client._reset()
        self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT)

    def test_set_timeout_on_client(self):
        self.client.timeout = 1
        self.client._sock.settimeout.assert_called_with(1)
        self.assertEqual(self.client.timeout, 1)

        self.client.timeout = None
        self.client._sock.settimeout.assert_called_with(None)
        self.assertEqual(self.client.timeout, None)

    def test_set_timeout_from_connect(self):
        self.client.disconnect()
        with warnings.catch_warnings(record=True) as w:
            self.client.connect("example.com", 10000, timeout=5)
            self.client._sock.settimeout.assert_called_with(5)
            self.assertEqual(len(w), 1)
            self.assertIn("Use MPDClient.timeout", str(w[0].message))

    @unittest.skipIf(
        sys.version_info < (3, 3), "BrokenPipeError was introduced in python 3.3"
    )
    def test_broken_pipe_error(self):
        self.MPDWillReturn("volume: 63\n", "OK\n")
        self.client._wfile.write.side_effect = BrokenPipeError
        self.socket_mock.error = Exception

        with self.assertRaises(mpd.ConnectionError):
            self.client.status()

    def test_connection_lost(self):
        # Simulate a connection lost: the socket returns empty strings
        self.MPDWillReturn("")
        self.socket_mock.error = Exception

        with self.assertRaises(mpd.ConnectionError):
            self.client.status()
            self.socket_mock.unpack.assert_called()

        # consistent behaviour, solves bug #11 (github)
        with self.assertRaises(mpd.ConnectionError):
            self.client.status()
            self.socket_mock.unpack.assert_called()

        self.assertIs(self.client._sock, None)

    @unittest.skipIf(
        sys.version_info < (3, 0),
        "Automatic decoding/encoding from the socket is only " "available in Python 3",
    )
    def test_force_socket_encoding_and_nonbuffering(self):
        # Force the reconnection to refill the mock
        self.client.disconnect()
        self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT)
        self.assertEqual(
            [
                mock.call("rb", newline="\n"),
                mock.call("w", encoding="utf-8", newline="\n"),
            ],
            # We are only interested into the 2 first entries,
            # otherwise we get all the readline() & co...
            self.client._sock.makefile.call_args_list[0:2],
        )

    def test_ranges_as_argument(self):
        self.MPDWillReturn("OK\n")
        self.client.move((1, 2), 2)
        self.assertMPDReceived('move "1:2" "2"\n')

        self.MPDWillReturn("OK\n")
        self.client.move((1,), 2)
        self.assertMPDReceived('move "1:" "2"\n')

        # old code still works!
        self.MPDWillReturn("OK\n")
        self.client.move("1:2", 2)
        self.assertMPDReceived('move "1:2" "2"\n')

        # empty ranges
        self.MPDWillReturn("OK\n")
        self.client.rangeid(1, ())
        self.assertMPDReceived('rangeid "1" ":"\n')

        with self.assertRaises(ValueError):
            self.MPDWillReturn("OK\n")
            self.client.move((1, "garbage"), 2)
            self.assertMPDReceived('move "1:" "2"\n')

    def test_parse_changes(self):
        self.MPDWillReturn(
            "cpos: 0\n",
            "Id: 66\n",
            "cpos: 1\n",
            "Id: 67\n",
            "cpos: 2\n",
            "Id: 68\n",
            "cpos: 3\n",
            "Id: 69\n",
            "cpos: 4\n",
            "Id: 70\n",
            "OK\n",
        )
        res = self.client.plchangesposid(0)
        self.assertEqual(
            [
                {"cpos": "0", "id": "66"},
                {"cpos": "1", "id": "67"},
                {"cpos": "2", "id": "68"},
                {"cpos": "3", "id": "69"},
                {"cpos": "4", "id": "70"},
            ],
            res,
        )

    def test_parse_database(self):
        self.MPDWillReturn(
            "directory: foo\n",
            "Last-Modified: 2014-01-23T16:42:46Z\n",
            "file: bar.mp3\n",
            "size: 59618802\n",
            "Last-Modified: 2014-11-02T19:57:00Z\n",
            "OK\n",
        )
        self.client.listfiles("/")

    def test_parse_mounts(self):
        self.MPDWillReturn(
            "mount: \n",
            "storage: /home/foo/music\n",
            "mount: foo\n",
            "storage: nfs://192.168.1.4/export/mp3\n",
            "OK\n",
        )
        res = self.client.listmounts()
        self.assertEqual(
            [
                {"mount": "", "storage": "/home/foo/music"},
                {"mount": "foo", "storage": "nfs://192.168.1.4/export/mp3"},
            ],
            res,
        )

    def test_parse_neighbors(self):
        self.MPDWillReturn(
            "neighbor: smb://FOO\n", "name: FOO (Samba 4.1.11-Debian)\n", "OK\n"
        )
        res = self.client.listneighbors()
        self.assertEqual(
            [{"name": "FOO (Samba 4.1.11-Debian)", "neighbor": "smb://FOO"}], res
        )

    def test_parse_outputs(self):
        self.MPDWillReturn(
            "outputid: 0\n",
            "outputname: My ALSA Device\n",
            "outputenabled: 0\n",
            "OK\n",
        )
        res = self.client.outputs()
        self.assertEqual(
            [{"outputenabled": "0", "outputid": "0", "outputname": "My ALSA Device"}],
            res,
        )

    def test_parse_playlist(self):
        self.MPDWillReturn(
            "0:file: Weezer - Say It Ain't So.mp3\n",
            "1:file: Dire Straits - Walk of Life.mp3\n",
            "2:file: 01 - Love Delicatessen.mp3\n",
            "3:file: Guns N' Roses - Paradise City.mp3\n",
            "4:file: Nirvana - Lithium.mp3\n",
            "OK\n",
        )
        res = self.client.playlist()
        self.assertEqual(
            [
                "file: Weezer - Say It Ain't So.mp3",
                "file: Dire Straits - Walk of Life.mp3",
                "file: 01 - Love Delicatessen.mp3",
                "file: Guns N' Roses - Paradise City.mp3",
                "file: Nirvana - Lithium.mp3",
            ],
            res,
        )

    def test_parse_playlists(self):
        self.MPDWillReturn(
            "playlist: Playlist\n", "Last-Modified: 2016-08-13T10:55:56Z\n", "OK\n"
        )
        res = self.client.listplaylists()
        self.assertEqual(
            [{"last-modified": "2016-08-13T10:55:56Z", "playlist": "Playlist"}], res
        )

    def test_parse_plugins(self):
        self.MPDWillReturn(
            "plugin: vorbis\n",
            "suffix: ogg\n",
            "suffix: oga\n",
            "mime_type: application/ogg\n",
            "mime_type: application/x-ogg\n",
            "mime_type: audio/ogg\n",
            "mime_type: audio/vorbis\n",
            "mime_type: audio/vorbis+ogg\n",
            "mime_type: audio/x-ogg\n",
            "mime_type: audio/x-vorbis\n",
            "mime_type: audio/x-vorbis+ogg\n",
            "OK\n",
        )
        res = self.client.decoders()
        self.assertEqual(
            [
                {
                    "mime_type": [
                        "application/ogg",
                        "application/x-ogg",
                        "audio/ogg",
                        "audio/vorbis",
                        "audio/vorbis+ogg",
                        "audio/x-ogg",
                        "audio/x-vorbis",
                        "audio/x-vorbis+ogg",
                    ],
                    "plugin": "vorbis",
                    "suffix": ["ogg", "oga"],
                }
            ],
            list(res),
        )

    def test_parse_raw_stickers(self):
        self.MPDWillReturn("sticker: foo=bar\n", "OK\n")
        res = self.client._parse_raw_stickers(self.client._read_lines())
        self.assertEqual([("foo", "bar")], list(res))

        self.MPDWillReturn("sticker: foo=bar\n", "sticker: l=b\n", "OK\n")
        res = self.client._parse_raw_stickers(self.client._read_lines())
        self.assertEqual([("foo", "bar"), ("l", "b")], list(res))

    def test_parse_raw_sticker_with_special_value(self):
        self.MPDWillReturn("sticker: foo==uv=vu\n", "OK\n")
        res = self.client._parse_raw_stickers(self.client._read_lines())
        self.assertEqual([("foo", "=uv=vu")], list(res))

    def test_parse_sticket_get_one(self):
        self.MPDWillReturn("sticker: foo=bar\n", "OK\n")
        res = self.client.sticker_get("song", "baz", "foo")
        self.assertEqual("bar", res)

    def test_parse_sticket_get_no_sticker(self):
        self.MPDWillReturn("ACK [50@0] {sticker} no such sticker\n")
        self.assertRaises(
            mpd.CommandError, self.client.sticker_get, "song", "baz", "foo"
        )

    def test_parse_sticker_list(self):
        self.MPDWillReturn("sticker: foo=bar\n", "sticker: lom=bok\n", "OK\n")
        res = self.client.sticker_list("song", "baz")
        self.assertEqual({"foo": "bar", "lom": "bok"}, res)

        # Even with only one sticker, we get a dict
        self.MPDWillReturn("sticker: foo=bar\n", "OK\n")
        res = self.client.sticker_list("song", "baz")
        self.assertEqual({"foo": "bar"}, res)

    def test_command_list(self):
        self.MPDWillReturn(
            "list_OK\n",
            "list_OK\n",
            "list_OK\n",
            "list_OK\n",
            "list_OK\n",
            "volume: 100\n",
            "repeat: 1\n",
            "random: 1\n",
            "single: 0\n",
            "consume: 0\n",
            "playlist: 68\n",
            "playlistlength: 5\n",
            "mixrampdb: 0.000000\n",
            "state: play\n",
            "xfade: 5\n",
            "song: 0\n",
            "songid: 56\n",
            "time: 0:259\n",
            "elapsed: 0.000\n",
            "bitrate: 0\n",
            "nextsong: 2\n",
            "nextsongid: 58\n",
            "list_OK\n",
            "OK\n",
        )
        self.client.command_list_ok_begin()
        self.client.clear()
        self.client.load("Playlist")
        self.client.random(1)
        self.client.repeat(1)
        self.client.play(0)
        self.client.status()
        res = self.client.command_list_end()
        self.assertEqual(None, res[0])
        self.assertEqual(None, res[1])
        self.assertEqual(None, res[2])
        self.assertEqual(None, res[3])
        self.assertEqual(None, res[4])
        self.assertEqual(
            [
                ("bitrate", "0"),
                ("consume", "0"),
                ("elapsed", "0.000"),
                ("mixrampdb", "0.000000"),
                ("nextsong", "2"),
                ("nextsongid", "58"),
                ("playlist", "68"),
                ("playlistlength", "5"),
                ("random", "1"),
                ("repeat", "1"),
                ("single", "0"),
                ("song", "0"),
                ("songid", "56"),
                ("state", "play"),
                ("time", "0:259"),
                ("volume", "100"),
                ("xfade", "5"),
            ],
            sorted(res[5].items()),
        )


# MPD client tests which do not mock the socket, but rather replace it
# with a real socket from a socket
@unittest.skipIf(
    not hasattr(socket, "socketpair"), "Socketpair is not supported on this platform"
)
class TestMPDClientSocket(unittest.TestCase):

    longMessage = True

    def setUp(self):
        self.connect_patch = mock.patch("mpd.MPDClient._connect_unix")
        self.connect_mock = self.connect_patch.start()

        test_socketpair = socket.socketpair()

        self.connect_mock.return_value = test_socketpair[0]
        self.server_socket = test_socketpair[1]
        self.server_socket_reader = self.server_socket.makefile("rb")
        self.server_socket_writer = self.server_socket.makefile("wb")

        self.MPDWillReturnBinary(b"OK MPD 0.21.24\n")

        self.client = mpd.MPDClient()
        self.client.connect(TEST_MPD_UNIXHOST)
        self.client.timeout = TEST_MPD_UNIXTIMEOUT

        self.connect_mock.assert_called_once()

    def tearDown(self):
        self.close_server_socket()
        self.connect_patch.stop()

    def close_server_socket(self):
        self.server_socket_reader.close()
        self.server_socket_writer.close()
        self.server_socket.close()

    def MPDWillReturnBinary(self, byteStr):
        self.server_socket_writer.write(byteStr)
        self.server_socket_writer.flush()

    def assertMPDReceived(self, byteStr):
        """
        Assert MPD received the given bytestring.
        Note: this disconnects the client.
        """
        # to ensure we don't block, close the socket on client side
        self.client.disconnect()

        # read one extra to ensure nothing extraneous was written
        received = self.server_socket_reader.read(len(byteStr) + 1)

        self.assertEqual(received, byteStr)

    def test_readbinary_error(self):
        self.MPDWillReturnBinary(b"ACK [50@0] {albumart} No file exists\n")

        self.assertRaises(
            mpd.CommandError, lambda: self.client.albumart("a/full/path.mp3")
        )

        self.assertMPDReceived(b'albumart "a/full/path.mp3" "0"\n')

    def test_binary_albumart_disconnect_afterchunk(self):
        self.MPDWillReturnBinary(b"size: 17\nbinary: 3\n" b"\x00\x00\x00\nOK\n")

        # we're expecting a timeout
        self.assertRaises(
            socket.timeout, lambda: self.client.albumart("a/full/path.mp3")
        )

        self.assertMPDReceived(
            b'albumart "a/full/path.mp3" "0"\nalbumart "a/full/path.mp3" "3"\n'
        )
        self.assertIs(self.client._sock, None)

    def test_binary_albumart_disconnect_midchunk(self):
        self.MPDWillReturnBinary(b"size: 8\nbinary: 8\n\x00\x01\x02\x03")

        # we're expecting a timeout or error of some form
        self.assertRaises(
            socket.timeout, lambda: self.client.albumart("a/full/path.mp3")
        )

        self.assertMPDReceived(b'albumart "a/full/path.mp3" "0"\n')
        self.assertIs(self.client._sock, None)

    def test_binary_albumart_singlechunk_networkmultiwrite(self):
        # length 16
        expected_binary = (
            b"\xA0\xA1\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xAB\xAC\xAD\xAE\xAF"
        )

        self.MPDWillReturnBinary(b"binary: 16\n")
        self.MPDWillReturnBinary(expected_binary[0:4])
        self.MPDWillReturnBinary(expected_binary[4:9])
        self.MPDWillReturnBinary(expected_binary[9:14])
        self.MPDWillReturnBinary(expected_binary[14:16])
        self.MPDWillReturnBinary(b"\nOK\n")

        real_binary = self.client.albumart("a/full/path.mp3")
        self.assertMPDReceived(b'albumart "a/full/path.mp3" "0"\n')
        self.assertEqual(real_binary, {"binary": expected_binary})

    def test_binary_albumart_singlechunk_nosize(self):
        # length: 16
        expected_binary = (
            b"\x01\x02\x00\x03\x04\x00\xFF\x05\x07\x08\x0A\x0F\xF0\xA5\x00\x01"
        )

        self.MPDWillReturnBinary(b"binary: 16\n" + expected_binary + b"\nOK\n")

        real_binary = self.client.albumart("a/full/path.mp3")
        self.assertMPDReceived(b'albumart "a/full/path.mp3" "0"\n')
        self.assertEqual(real_binary, {"binary": expected_binary})

    def test_binary_albumart_singlechunk_sizeheader(self):
        # length: 16
        expected_binary = (
            b"\x01\x02\x00\x03\x04\x00\xFF\x05\x07\x08\x0A\x0F\xF0\xA5\x00\x01"
        )

        self.MPDWillReturnBinary(
            b"size: 16\nbinary: 16\n" + expected_binary + b"\nOK\n"
        )

        real_binary = self.client.albumart("a/full/path.mp3")
        self.assertMPDReceived(b'albumart "a/full/path.mp3" "0"\n')
        self.assertEqual(real_binary, {"binary": expected_binary})

    def test_binary_albumart_even_multichunk(self):
        # length: 16 each
        expected_chunk1 = (
            b"\x01\x02\x00\x03\x04\x00\xFF\x05\x07\x08\x0A\x0F\xF0\xA5\x00\x01"
        )
        expected_chunk2 = (
            b"\x0A\x0B\x0C\x0D\x0E\x0F\x10\x1F\x2F\x2D\x33\x0D\x00\x00\x11\x13"
        )
        expected_chunk3 = (
            b"\x99\x88\x77\xDD\xD0\xF0\x20\x70\x71\x17\x13\x31\xFF\xFF\xDD\xFF"
        )
        expected_binary = expected_chunk1 + expected_chunk2 + expected_chunk3

        # 3 distinct commands expected
        self.MPDWillReturnBinary(
            b"size: 48\nbinary: 16\n"
            + expected_chunk1
            + b"\nOK\nsize: 48\nbinary: 16\n"
            + expected_chunk2
            + b"\nOK\nsize: 48\nbinary: 16\n"
            + expected_chunk3
            + b"\nOK\n"
        )

        real_binary = self.client.albumart("a/full/path.mp3")

        self.assertMPDReceived(
            b'albumart "a/full/path.mp3" "0"\nalbumart "a/full/path.mp3" "16"'
            b'\nalbumart "a/full/path.mp3" "32"\n'
        )
        self.assertEqual(real_binary, {"binary": expected_binary})

    def test_binary_albumart_odd_multichunk(self):
        # lengths: 17, 15, 1
        expected_chunk1 = (
            b"\x01\x02\x00\x03\x04\x00\xFF\x05\x07\x08\x0A\x0F\xF0\xA5\x00\x01\x13"
        )
        expected_chunk2 = (
            b"\x0A\x0B\x0C\x0D\x0E\x0F\x10\x1F\x2F\x2D\x33\x0D\x00\x00\x11"
        )
        expected_chunk3 = b"\x99"
        expected_binary = expected_chunk1 + expected_chunk2 + expected_chunk3

        # 3 distinct commands expected
        self.MPDWillReturnBinary(
            b"size: 33\nbinary: 17\n"
            + expected_chunk1
            + b"\nOK\nsize: 33\nbinary: 15\n"
            + expected_chunk2
            + b"\nOK\nsize: 33\nbinary: 1\n"
            + expected_chunk3
            + b"\nOK\n"
        )

        real_binary = self.client.albumart("a/full/path.mp3")
        self.assertMPDReceived(
            b'albumart "a/full/path.mp3" "0"\nalbumart "a/full/path.mp3" "17"\n'
            b'albumart "a/full/path.mp3" "32"\n'
        )
        self.assertEqual(real_binary, {"binary": expected_binary})

    # MPD server can return empty response if a file exists but is empty
    def test_binary_albumart_emptyresponse(self):
        self.MPDWillReturnBinary(b"size: 0\nbinary: 0\n\nOK\n")

        real_binary = self.client.albumart("a/full/path.mp3")
        self.assertMPDReceived(b'albumart "a/full/path.mp3" "0"\n')
        self.assertEqual(real_binary, {"binary": b""})

    # readpicture returns empty object if the song exists but has no picture
    def test_binary_readpicture_emptyresponse(self):
        self.MPDWillReturnBinary(b"OK\n")

        real_binary = self.client.readpicture("plainsong.mp3")
        self.assertMPDReceived(b'readpicture "plainsong.mp3" "0"\n')
        self.assertEqual(real_binary, {})

    def test_binary_readpicture_untyped(self):
        # length: 16 each
        expected_chunk1 = (
            b"\x01\x02\x00\x03\x04\x00\xFF\x05\x07\x08\x0A\x0F\xF0\xA5\x00\x01"
        )
        expected_chunk2 = (
            b"\x0A\x0B\x0C\x0D\x0E\x0F\x10\x1F\x2F\x2D\x33\x0D\x00\x00\x11\x13"
        )
        expected_chunk3 = (
            b"\x99\x88\x77\xDD\xD0\xF0\x20\x70\x71\x17\x13\x31\xFF\xFF\xDD\xFF"
        )
        expected_binary = expected_chunk1 + expected_chunk2 + expected_chunk3

        # 3 distinct commands expected
        self.MPDWillReturnBinary(
            b"size: 48\nbinary: 16\n"
            + expected_chunk1
            + b"\nOK\nsize: 48\nbinary: 16\n"
            + expected_chunk2
            + b"\nOK\nsize: 48\nbinary: 16\n"
            + expected_chunk3
            + b"\nOK\n"
        )

        real_binary = self.client.readpicture("a/full/path.mp3")

        self.assertMPDReceived(
            b'readpicture "a/full/path.mp3" "0"\nreadpicture "a/full/path.mp3" "16"'
            b'\nreadpicture "a/full/path.mp3" "32"\n'
        )
        self.assertEqual(real_binary, {"binary": expected_binary})

    def test_binary_readpicture_typed(self):
        # length: 16 each
        expected_binary = bytes(range(48))

        # 3 distinct commands expected
        self.MPDWillReturnBinary(
            b"size: 48\ntype: image/png\nbinary: 16\n"
            + expected_binary[0:16]
            + b"\nOK\nsize: 48\ntype: image/png\nbinary: 16\n"
            + expected_binary[16:32]
            + b"\nOK\nsize: 48\ntype: image/png\nbinary: 16\n"
            + expected_binary[32:48]
            + b"\nOK\n"
        )

        real_binary = self.client.readpicture("a/full/path.mp3")

        self.assertMPDReceived(
            b'readpicture "a/full/path.mp3" "0"\nreadpicture "a/full/path.mp3" "16"'
            b'\nreadpicture "a/full/path.mp3" "32"\n'
        )
        self.assertEqual(real_binary, {"binary": expected_binary, "type": "image/png"})

    def test_binary_readpicture_badheaders(self):
        expected_binary = bytes(range(32))

        # inconsistent type header from response 1 to response 2
        # exception is expected
        self.MPDWillReturnBinary(
            b"size: 32\ntype: image/jpeg\nbinary: 16\n"
            + expected_binary[0:16]
            + b"\nOK\nsize: 32\ntype: image/png\nbinary: 16\n"
            + expected_binary[16:32]
            + b"\nOK\n"
        )

        self.assertRaises(
            mpd.CommandError, lambda: self.client.readpicture("song.mp3")
        )

        self.assertMPDReceived(
            b'readpicture "song.mp3" "0"\nreadpicture "song.mp3" "16"\n'
        )


class MockTransport(object):
    def __init__(self):
        self.written = list()

    def clear(self):
        self.written = list()

    def write(self, data):
        self.written.append(data)


@unittest.skipIf(TWISTED_MISSING, "requires twisted to be installed")
class TestMPDProtocol(unittest.TestCase):
    def init_protocol(self, default_idle=True, idle_result=None):
        self.protocol = mpd.MPDProtocol(
            default_idle=default_idle, idle_result=idle_result
        )
        self.protocol.transport = MockTransport()

    def test_create_command(self):
        self.init_protocol(default_idle=False)
        self.assertEqual(self.protocol._create_command("play"), b"play")
        self.assertEqual(
            self.protocol._create_command("rangeid", args=["1", ()]), b'rangeid "1" ":"'
        )
        self.assertEqual(
            self.protocol._create_command("rangeid", args=["1", (1,)]),
            b'rangeid "1" "1:"',
        )
        self.assertEqual(
            self.protocol._create_command("rangeid", args=["1", (1, 2)]),
            b'rangeid "1" "1:2"',
        )

    def test_success(self):
        self.init_protocol(default_idle=False)

        def success(result):
            expected = {
                "file": "Dire Straits - Walk of Life.mp3",
                "artist": "Dire Straits",
                "title": "Walk of Life",
                "genre": "Rock/Pop",
                "track": "3",
                "album": "Brothers in Arms",
                "id": "13",
                "last-modified": "2016-08-11T10:57:03Z",
                "pos": "4",
                "time": "253",
            }
            self.assertEqual(expected, result)

        self.protocol.currentsong().addCallback(success)
        self.assertEqual([b"currentsong\n"], self.protocol.transport.written)

        for line in [
            b"file: Dire Straits - Walk of Life.mp3",
            b"Last-Modified: 2016-08-11T10:57:03Z",
            b"Time: 253",
            b"Artist: Dire Straits",
            b"Title: Walk of Life",
            b"Album: Brothers in Arms",
            b"Track: 3",
            b"Genre: Rock/Pop",
            b"Pos: 4",
            b"Id: 13",
            b"OK",
        ]:
            self.protocol.lineReceived(line)

    def test_failure(self):
        self.init_protocol(default_idle=False)

        def error(result):
            self.assertIsInstance(result, Failure)
            self.assertEqual(result.getErrorMessage(), "[50@0] {load} No such playlist")

        self.protocol.load("Foo").addErrback(error)
        self.assertEqual([b'load "Foo"\n'], self.protocol.transport.written)
        self.protocol.lineReceived(b"ACK [50@0] {load} No such playlist")

    def test_default_idle(self):
        def idle_result(result):
            self.assertEqual(list(result), ["player"])

        self.init_protocol(idle_result=idle_result)
        self.protocol.lineReceived(b"OK MPD 0.18.0")
        self.assertEqual([b"idle\n"], self.protocol.transport.written)
        self.protocol.transport.clear()
        self.protocol.lineReceived(b"changed: player")
        self.protocol.lineReceived(b"OK")
        self.assertEqual([b"idle\n"], self.protocol.transport.written)

    def test_noidle_when_default_idle(self):
        self.init_protocol()
        self.protocol.lineReceived(b"OK MPD 0.18.0")
        self.protocol.pause()
        self.protocol.lineReceived(b"OK")
        self.protocol.lineReceived(b"OK")
        self.assertEqual(
            [b"idle\n", b"noidle\n", b"pause\n", b"idle\n"],
            self.protocol.transport.written,
        )

    def test_already_idle(self):
        self.init_protocol(default_idle=False)
        self.protocol.idle()
        self.assertRaises(mpd.CommandError, lambda: self.protocol.idle())

    def test_already_noidle(self):
        self.init_protocol(default_idle=False)
        self.assertRaises(mpd.CommandError, lambda: self.protocol.noidle())

    def test_command_list(self):
        self.init_protocol(default_idle=False)

        def success(result):
            self.assertEqual([None, None], result)

        self.protocol.command_list_ok_begin()
        self.protocol.play()
        self.protocol.stop()
        self.protocol.command_list_end().addCallback(success)
        self.assertEqual(
            [b"command_list_ok_begin\n", b"play\n", b"stop\n", b"command_list_end\n",],
            self.protocol.transport.written,
        )
        self.protocol.transport.clear()
        self.protocol.lineReceived(b"list_OK")
        self.protocol.lineReceived(b"list_OK")
        self.protocol.lineReceived(b"OK")

    def test_command_list_failure(self):
        self.init_protocol(default_idle=False)

        def load_command_error(result):
            self.assertIsInstance(result, Failure)
            self.assertEqual(result.getErrorMessage(), "[50@0] {load} No such playlist")

        def command_list_general_error(result):
            self.assertIsInstance(result, Failure)
            self.assertEqual(result.getErrorMessage(), "An earlier command failed.")

        self.protocol.command_list_ok_begin()
        self.protocol.load("Foo").addErrback(load_command_error)
        self.protocol.play().addErrback(command_list_general_error)
        self.protocol.command_list_end().addErrback(load_command_error)
        self.assertEqual(
            [
                b"command_list_ok_begin\n",
                b'load "Foo"\n',
                b"play\n",
                b"command_list_end\n",
            ],
            self.protocol.transport.written,
        )
        self.protocol.lineReceived(b"ACK [50@0] {load} No such playlist")

    def test_command_list_when_default_idle(self):
        self.init_protocol()
        self.protocol.lineReceived(b"OK MPD 0.18.0")

        def success(result):
            self.assertEqual([None, None], result)

        self.protocol.command_list_ok_begin()
        self.protocol.play()
        self.protocol.stop()
        self.protocol.command_list_end().addCallback(success)
        self.assertEqual(
            [
                b"idle\n",
                b"noidle\n",
                b"command_list_ok_begin\n",
                b"play\n",
                b"stop\n",
                b"command_list_end\n",
            ],
            self.protocol.transport.written,
        )
        self.protocol.transport.clear()
        self.protocol.lineReceived(b"OK")
        self.protocol.lineReceived(b"list_OK")
        self.protocol.lineReceived(b"list_OK")
        self.protocol.lineReceived(b"OK")
        self.assertEqual([b"idle\n"], self.protocol.transport.written)

    def test_command_list_failure_when_default_idle(self):
        self.init_protocol()
        self.protocol.lineReceived(b"OK MPD 0.18.0")

        def load_command_error(result):
            self.assertIsInstance(result, Failure)
            self.assertEqual(result.getErrorMessage(), "[50@0] {load} No such playlist")

        def command_list_general_error(result):
            self.assertIsInstance(result, Failure)
            self.assertEqual(result.getErrorMessage(), "An earlier command failed.")

        self.protocol.command_list_ok_begin()
        self.protocol.load("Foo").addErrback(load_command_error)
        self.protocol.play().addErrback(command_list_general_error)
        self.protocol.command_list_end().addErrback(load_command_error)
        self.assertEqual(
            [
                b"idle\n",
                b"noidle\n",
                b"command_list_ok_begin\n",
                b'load "Foo"\n',
                b"play\n",
                b"command_list_end\n",
            ],
            self.protocol.transport.written,
        )
        self.protocol.transport.clear()
        self.protocol.lineReceived(b"OK")
        self.protocol.lineReceived(b"ACK [50@0] {load} No such playlist")
        self.assertEqual([b"idle\n"], self.protocol.transport.written)

    def test_command_list_item_is_generator(self):
        self.init_protocol(default_idle=False)

        def success(result):
            self.assertEqual(
                result,
                [
                    [
                        "Weezer - Say It Ain't So.mp3",
                        "Dire Straits - Walk of Life.mp3",
                        "01 - Love Delicatessen.mp3",
                        "Guns N' Roses - Paradise City.mp3",
                    ]
                ],
            )

        self.protocol.command_list_ok_begin()
        self.protocol.listplaylist("Foo")
        self.protocol.command_list_end().addCallback(success)
        self.protocol.lineReceived(b"file: Weezer - Say It Ain't So.mp3")
        self.protocol.lineReceived(b"file: Dire Straits - Walk of Life.mp3")
        self.protocol.lineReceived(b"file: 01 - Love Delicatessen.mp3")
        self.protocol.lineReceived(b"file: Guns N' Roses - Paradise City.mp3")
        self.protocol.lineReceived(b"list_OK")
        self.protocol.lineReceived(b"OK")

    def test_already_in_command_list(self):
        self.init_protocol(default_idle=False)
        self.protocol.command_list_ok_begin()
        self.assertRaises(
            mpd.CommandListError, lambda: self.protocol.command_list_ok_begin()
        )

    def test_not_in_command_list(self):
        self.init_protocol(default_idle=False)
        self.assertRaises(
            mpd.CommandListError, lambda: self.protocol.command_list_end()
        )

    def test_invalid_command_in_command_list(self):
        self.init_protocol(default_idle=False)
        self.protocol.command_list_ok_begin()
        self.assertRaises(mpd.CommandListError, lambda: self.protocol.kill())

    def test_close(self):
        self.init_protocol(default_idle=False)

        def success(result):
            self.assertEqual(result, None)

        self.protocol.close().addCallback(success)


class AsyncMockServer:
    def __init__(self):
        self._output = asyncio.Queue()
        self._expectations = []

    def get_streams(self):
        result = asyncio.Future()
        result.set_result((self, self))
        return result

    def readline(self):
        # directly passing around the awaitable
        return self._output.get()

    async def readexactly(self, length):
        ret = await self._output.get()
        if len(ret) != length:
            self.error("Mock data is not chuncked in the way the client expects to read it")
        return ret

    def write(self, data):
        try:
            next_write = self._expectations[0][0][0]
        except IndexError:
            self.error("Data written to mock even though none expected: %r" % data)
        if next_write == data:
            self._expectations[0][0].pop(0)
            self._feed()
        else:
            self.error("Mock got %r, expected %r" % (data, next_write))

    def close(self):
        # todo: make sure calls to self.write fail after calling close
        pass

    def error(self, message):
        raise AssertionError(message)

    def _feed(self):
        if len(self._expectations[0][0]) == 0:
            _, response_lines = self._expectations.pop(0)
            for l in response_lines:
                self._output.put_nowait(l)

    def expect_exchange(self, request_lines, response_lines):
        self._expectations.append((request_lines, response_lines))
        self._feed()


class TestAsyncioMPD(unittest.TestCase):
    def init_client(self, odd_hello=None):
        self.loop = asyncio.get_event_loop()

        self.mockserver = AsyncMockServer()
        asyncio.open_connection = mock.MagicMock(
            return_value=self.mockserver.get_streams()
        )

        if odd_hello is None:
            hello_lines = [b"OK MPD mocker\n"]
        else:
            hello_lines = odd_hello

        self.mockserver.expect_exchange([], hello_lines)

        self.client = mpd.asyncio.MPDClient()
        self._await(self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT))

        asyncio.open_connection.assert_called_with(
            TEST_MPD_HOST, TEST_MPD_PORT
        )

    def __del__(self):
        # Clean up after init_client. (This works for now; if it causes
        # trouble, change all init_client to a `with init_client` or use
        # fixtures).
        if hasattr(self, "client"):
            self.client.disconnect()

    def _await(self, future):
        return self.loop.run_until_complete(future)

    def test_oddhello(self):
        self.assertRaises(
            mpd.base.ProtocolError, self.init_client, odd_hello=[b"NOT OK\n"]
        )

    @unittest.skipIf(
        os.getenv("RUN_SLOW_TESTS") is None,
        "This test would add 5 seconds of idling to the run (export RUN_SLOW_TESTS=1 to run anyway)",
    )
    def test_noresponse(self):
        self.assertRaises(mpd.base.ConnectionError, self.init_client, odd_hello=[])

    def test_status(self):
        self.init_client()

        self.mockserver.expect_exchange(
            [b"status\n"],
            [
                b"volume: 70\n",
                b"repeat: 0\n",
                b"random: 1\n",
                b"single: 0\n",
                b"consume: 0\n",
                b"playlist: 416\n",
                b"playlistlength: 7\n",
                b"mixrampdb: 0.000000\n",
                b"state: play\n",
                b"song: 4\n",
                b"songid: 19\n",
                b"time: 28:403\n",
                b"elapsed: 28.003\n",
                b"bitrate: 465\n",
                b"duration: 403.066\n",
                b"audio: 44100:16:2\n",
                b"OK\n",
            ],
        )

        status = self._await(self.client.status())
        self.assertEqual(
            status,
            {
                "audio": "44100:16:2",
                "bitrate": "465",
                "consume": "0",
                "duration": "403.066",
                "elapsed": "28.003",
                "mixrampdb": "0.000000",
                "playlist": "416",
                "playlistlength": "7",
                "random": "1",
                "repeat": "0",
                "single": "0",
                "song": "4",
                "songid": "19",
                "state": "play",
                "time": "28:403",
                "volume": "70",
            },
        )

    async def _test_outputs(self):
        self.mockserver.expect_exchange(
            [b"outputs\n"],
            [
                b"outputid: 0\n",
                b"outputname: My ALSA Device\n",
                b"plugin: alsa\n",
                b"outputenabled: 0\n",
                b"attribute: dop=0\n",
                b"outputid: 1\n",
                b"outputname: My FM transmitter\n",
                b"plugin: fmradio\n",
                b"outputenabled: 1\n",
                b"OK\n",
            ],
        )

        outputs = self.client.outputs()

        expected = iter(
            [
                {
                    "outputid": "0",
                    "outputname": "My ALSA Device",
                    "plugin": "alsa",
                    "outputenabled": "0",
                    "attribute": "dop=0",
                },
                {
                    "outputid": "1",
                    "outputname": "My FM transmitter",
                    "plugin": "fmradio",
                    "outputenabled": "1",
                },
            ]
        )

        async for o in outputs:
            self.assertEqual(o, next(expected))
        self.assertRaises(StopIteration, next, expected)

    def test_outputs(self):
        self.init_client()
        self._await(self._test_outputs())

    async def _test_list(self):
        self.mockserver.expect_exchange(
            [b'list "album"\n'], [b"Album: first\n", b"Album: second\n", b"OK\n",]
        )

        list_ = self.client.list("album")

        expected = iter([{"album": "first"}, {"album": "second"},])

        async for o in list_:
            self.assertEqual(o, next(expected))
        self.assertRaises(StopIteration, next, expected)

    def test_list(self):
        self.init_client()
        self._await(self._test_list())

    async def _test_albumart(self):
        self.mockserver.expect_exchange(
            [b'albumart "x.mp3" "0"\n'],
            [
                b"size: 32\n",
                b"binary: 16\n",
                bytes(range(16)),
                b"\n",
                b"OK\n",
            ]
        )
        self.mockserver.expect_exchange(
            [b'albumart "x.mp3" "16"\n'],
            [
                b"size: 32\n",
                b"binary: 16\n",
                bytes(range(16)),
                b"\n",
                b"OK\n",
            ],
        )

        albumart = await self.client.albumart("x.mp3")

        expected = {"binary": bytes(range(16)) + bytes(range(16))}

        self.assertEqual(albumart, expected)

    async def _test_readpicture(self):
            self.mockserver.expect_exchange(
                [b'readpicture "x.mp3" "0"\n'],
                [
                    b"size: 32\n",
                    b"type: image/jpeg\n",
                    b"binary: 16\n",
                    bytes(range(16)),
                    b"\n",
                    b"OK\n",
                ]
            )
            self.mockserver.expect_exchange(
                [b'readpicture "x.mp3" "16"\n'],
                [
                    b"size: 32\n",
                    b"type: image/jpeg\n",
                    b"binary: 16\n",
                    bytes(range(16)),
                    b"\n",
                    b"OK\n",
                ],
            )

            art = await self.client.readpicture("x.mp3")

            expected = {"binary": bytes(range(16)) + bytes(range(16)), "type": "image/jpeg"}

            self.assertEqual(art, expected)

    async def _test_readpicture_empty(self):
            self.mockserver.expect_exchange(
                [b'readpicture "x.mp3" "0"\n'],
                [
                    b"OK\n",
                ]
            )

            art = await self.client.readpicture("x.mp3")

            expected = {}

            self.assertEqual(art, expected)

    def test_albumart(self):
        self.init_client()
        self._await(self._test_albumart())

    def test_readpicture(self):
        self.init_client()
        self._await(self._test_readpicture())

    def test_readpicture_empty(self):
        self.init_client()
        self._await(self._test_readpicture_empty())

    def test_mocker(self):
        """Does the mock server refuse unexpected writes?"""
        self.init_client()

        self.mockserver.expect_exchange([b"expecting odd things\n"], [b""])
        self.assertRaises(AssertionError, self._await, self.client.status())

    async def _test_idle(self):
        self.mockserver.expect_exchange(
                [b'idle "database"\n',],
                [b"ACK [4@0] don't let you yet but you shouldn't care\n"],
                )
        self.mockserver.expect_exchange(
                # code could be smarter and set __in_idle = False and not set
                # noidle, but it's not *wrong* either
                [b'noidle\n', b'password "1234"\n',],
                [b"OK\n"],
                )
        self.mockserver.expect_exchange(
                [b'idle "playlist"\n'],
                [b'idle: playlist\n', b"OK\n"],
                )
        self.mockserver.expect_exchange(
                [b'noidle\n', b'currentsong\n'],
                # it's a bit brief but it'll be accepted
                [b"OK\n", ],
                )
        self.mockserver.expect_exchange(
                [b'idle "playlist"\n'],
                [b"ACK [4@0] I don't let you observe for no other reason\n"],
                )
        self.mockserver.expect_exchange(
                [b'noidle\n', b'status\n'],
                [b"ACK [4@0] whatever made the idle failed now fails too\n", ],
                )

        # clearly longer than IMMEDITE_COMMAND_TIMEOUT
        await asyncio.sleep(0.5)

        await self.client.password("1234")

        async for changeset in self.client.idle(["playlist"]):
            # the one regular event sent
            self.assertEqual(changeset, ["playlist"])
            break

        await self.client.currentsong()

        async for changeset in self.client.idle(["playlist"]):
            # watching for regular events but the error also gets shown as an event
            self.assertEqual(changeset, ["playlist"])
            break

        try:
            await self.client.status()
        except mpd.CommandError:
            pass
        else:
            raise AssertionError("The status should have flushed out the error that made the idle fail in the first place")

        self.client.disconnect()

    def test_idle(self):
        self.init_client()
        self._await(self._test_idle())


if __name__ == "__main__":
    unittest.main()
