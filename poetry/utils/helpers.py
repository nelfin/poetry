import re
import shutil
import tempfile

from contextlib import contextmanager
from typing import Union

_canonicalize_regex = re.compile('[-_]+')


def canonicalize_name(name):  # type: (str) -> str
    return _canonicalize_regex.sub('-', name).lower()


def module_name(name):  # type: (str) -> str
    return canonicalize_name(name).replace('.', '_').replace('-', '_')


@contextmanager
def temporary_directory(*args, **kwargs):
    try:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory(*args, **kwargs) as name:
            yield name
    except ImportError:
        name = tempfile.mkdtemp(*args, **kwargs)

        yield name

        shutil.rmtree(name)


def parse_requires(requires):  # type: (str) -> Union[list, None]
    lines = requires.split('\n')

    requires_dist = []
    in_section = False
    current_marker = None
    for line in lines:
        line = line.strip()
        if not line:
            if in_section:
                in_section = False

            continue

        if line.startswith('['):
            # extras or conditional dependencies
            marker = line.lstrip('[').rstrip(']')
            if ':' not in marker:
                extra, marker = marker, None
            else:
                extra, marker = marker.split(':')

            if extra:
                if marker:
                    marker = '{} and extra == "{}"'.format(marker, extra)
                else:
                    marker = 'extra == "{}"'.format(extra)

            if marker:
                current_marker = marker

            continue

        if current_marker:
            line = '{}; {}'.format(line, current_marker)

        requires_dist.append(line)

    if requires_dist:
        return requires_dist
