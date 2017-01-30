# -*- coding=utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from ctypes import c_size_t, byref

from chemfiles import get_c_library
from chemfiles.errors import _check_handle
from chemfiles.frame import Frame


class Trajectory(object):
    '''
    A :py:class:`Trajectory` is a chemistry file on the hard drive. It is the
    main entry point of Chemfiles.
    '''

    def __init__(self, path, mode="r", fformat=""):
        '''
        Open a trajectory file at ``path`` with mode ``mode``. Supported modes
        are "r" for read (this is the default) or "w" for write.
        '''
        self.c_lib = get_c_library()
        self._handle_ = self.c_lib.chfl_trajectory_with_format(
            path.encode("utf8"), mode.encode("utf8"), fformat.encode("utf8")
        )
        _check_handle(self._handle_)

    def __del__(self):
        self.c_lib.chfl_trajectory_close(self._handle_)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        # The C pointer will be deleted by the call to __del__, so no need to
        # call close ourselves.
        pass

    def read(self):
        '''
        Read the next step of the :py:class:`Trajectory` and return the
        corresponding :py:class:`Frame`
        '''
        frame = Frame()
        self.c_lib.chfl_trajectory_read(self._handle_, frame._handle_)
        return frame

    def read_step(self, step):
        '''
        Read a specific step in the :py:class:`Trajectory` and return the
        corresponding :py:class:`Frame`.
        '''
        frame = Frame()
        self.c_lib.chfl_trajectory_read_step(
            self._handle_, c_size_t(step), frame._handle_
        )
        return frame

    def write(self, frame):
        '''Write a :py:class:`Frame` to the :py:class:`Trajectory`'''
        self.c_lib.chfl_trajectory_write(self._handle_, frame._handle_)

    def set_topology(self, topology):
        '''
        Set the :py:class:`Topology` associated with a :py:class:`Trajectory`.
        This :py:class:`Topology` will be used when reading and writing the
        files, replacing any :py:class:`Topology` in the frames or files.
        '''
        self.c_lib.chfl_trajectory_set_topology(
            self._handle_, topology._handle_
        )

    def set_topology_file(self, filename):
        '''
        Set the :py:class:`Topology` associated with a :py:class:`Trajectory`
        by reading the first :py:class:`Frame` of ``filename``; and extracting
        the :py:class:`Topology` of this :py:class:`Frame`.
        '''
        self.c_lib.chfl_trajectory_set_topology_file(
            self._handle_, filename.encode("utf8")
        )

    def set_cell(self, cell):
        '''
        Set the :py:class:`UnitCell` associated with a :py:class:`Trajectory`.
        This :py:class:`UnitCell` will be used when reading and writing the
        files, replacing any :py:class:`UnitCell` in the frames or files.
        '''
        self.c_lib.chfl_trajectory_set_cell(self._handle_, cell._handle_)

    def nsteps(self):
        '''
        Get the number of steps (the number of frames) in a
        :py:class:`Trajectory`.
        '''
        res = c_size_t()
        self.c_lib.chfl_trajectory_nsteps(self._handle_, byref(res))
        return res.value

    def sync(self):
        '''
        Synchronize any buffered content to the hard drive.
        '''
        self.c_lib.chfl_trajectory_sync(self._handle_)