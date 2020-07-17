#!/usr/bin/env python

"""
Infinity Engine TLK files parser and merger
===========================================

This module can read/write TLK dialogue files for Infinity Engine games
and merge them from command line.

Author: Tomas Karabela <tkarabela@seznam.cz>

Format references:
    - https://gibberlings3.github.io/iesdp/file_formats/ie_formats/tlk_v1.htm
    - https://gibberlings3.github.io/iesdp/file_formats/general.htm

See also:
    - WeiDU <https://github.com/WeiDUorg/weidu>
    - TlkViewer <https://github.com/mrfearless/TlkViewer>

"""

import struct
from dataclasses import dataclass
import argparse
from typing import NamedTuple, List


class TLKv1Entry(NamedTuple):
    entry_type: int
    sound_ref: bytes
    volume: int
    pitch: int
    string: bytes


@dataclass
class TLKv1File:
    entries: List[TLKv1Entry]
    language_id: int

    @classmethod
    def read(cls, path: str):
        tlk = cls(entries=[], language_id=0)

        with open(path, "rb") as fp:
            data = fp.read()

        header_signature, header_version, language_id, entries_count, string_data_offset =\
            TLKv1HeaderStruct.unpack_from(data)

        assert header_signature == HEADER_SIGNATURE, "Unexpected file header ('TLK ')"
        assert header_version == HEADER_VERSION, "Unexpected file header ('V1  ')"
        tlk.language_id = language_id

        offset = TLKv1HeaderStruct.size
        for i in range(entries_count):
            entry_type, sound_ref, volume, pitch, string_offset, string_length = \
                TLKv1EntryStruct.unpack_from(data, offset)

            string_content = data[string_data_offset+string_offset : string_data_offset+string_offset+string_length]

            entry = TLKv1Entry(entry_type=entry_type,
                               sound_ref=sound_ref,
                               volume=volume,
                               pitch=pitch,
                               string=string_content)

            tlk.entries.append(entry)
            offset += TLKv1EntryStruct.size

        return tlk

    def write(self, path: str):
        with open(path, "wb") as fp:
            # write header
            entries_count = len(self.entries)
            string_data_offset = TLKv1HeaderStruct.size + entries_count * TLKv1EntryStruct.size

            header_data = TLKv1HeaderStruct.pack(HEADER_SIGNATURE, HEADER_VERSION, self.language_id,
                                                 entries_count, string_data_offset)
            fp.write(header_data)

            # write entries
            relative_string_offset = 0

            for entry in self.entries:
                string_length = len(entry.string)
                entry_data = TLKv1EntryStruct.pack(entry.entry_type, entry.sound_ref, entry.volume, entry.pitch,
                                                   relative_string_offset, string_length)
                fp.write(entry_data)
                relative_string_offset += string_length

            # write string data for entries
            for entry in self.entries:
                fp.write(entry.string)

    def __repr__(self):
        return f"<TLKv1File with {len(self.entries)} entries>"


TLKv1HeaderStruct = struct.Struct("<4s4sHII")
TLKv1EntryStruct = struct.Struct("<H8sIIII")
HEADER_SIGNATURE = b"TLK "
HEADER_VERSION = b"V1  "


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base_tlk", help="base TLK file into which lines will be merged")
    parser.add_argument("tlk_to_merge", help="TLK file with changes to be merged")
    parser.add_argument("output_tlk", help="resulting merged TLK file")
    args = parser.parse_args()

    # read input
    base_tlk = TLKv1File.read(args.base_tlk)
    tlk_to_merge = TLKv1File.read(args.tlk_to_merge)

    # do the merge
    new_entries = tlk_to_merge.entries.copy()  # take all lines from other file
    new_entries.extend(base_tlk.entries[len(tlk_to_merge.entries):])  # keep any extra lines from base file
    base_tlk.entries = new_entries

    # write output
    base_tlk.write(args.output_tlk)
