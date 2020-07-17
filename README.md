# Infinity Engine TLK files parser and merger

The `tlk.py` module can read and write TLK dialogue files for Infinity Engine games (like Baldur's Gate, Icewind Dale
and others), with command line interface to merge two TLK files together, like this:

    ./tlk.py dialog.tlk dialog_to_merge.tlk dialog_output.tlk

For viewing TLK file contents, [TlkViewer](https://github.com/mrfearless/TlkViewer) is a useful tool.
For more serious work with Infinity Engine, see the [WeiDU](https://github.com/WeiDUorg/weidu) toolkit.
I have created this to merge two TLK files, which is easy but not readily done using TlkViewer
(reader only) or WeiDU (much more complex tool written in OCaml). So I made this simple Python module :)

Implemented thanks to [Infinity Engine Structures Description Project](https://gibberlings3.github.io/iesdp)
documentation of the TLK format.

Works with Python 3.7+, see LICENSE.txt for license terms (MIT).
