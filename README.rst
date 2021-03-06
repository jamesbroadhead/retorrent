Retorrent is a media management and re-seeding tool.

*retorrent* is a command-line media management tool which renames newly downloaded files into a standard format, and symlinks back to ease seeding. The main goal of this project is to allow the user to rename all of their media without losing the ability to seed, with as little user-input as possible.


== Support Status ==
This tool is in use by me at time of writing (2017-06), but does not receive major changes/updates.

The majority of the codebase comes from a time where I was still learning python and good programming practises. Mome elements of it do not work as well as they might, have limited test coverate and are in need of rearchitecting.
Contributions are welcome, however those which do not improve test coverage will not be accepted

== Description ==
The average download requires 3-4 presses of 'Enter' for all of its files to be moved to a 'videos' folder, renamed in a standard manner, reverse symlinked to a 'seeding' directory, and provided with its .torrent files.For filenames that are 'easy' to convert, this is reduced even further (1-2 keypresses)

It renames media files from their original filenames to ones that are systematic and easy to organise, into a format compatible with the default filename parsers which come with XBMC (Media Centre).


Some of this code comes from publically accessible code, which may not be covered by the blanket GPL, as the rest of the code in this project is. These sections are commented and attributed, please refer to the attribution for licensing details.

New Torrent Workflow:
	Download a .torrent file using your browser.
	Put the .torrent file in your TORRENTFILESDIR
	Allow your torrent client to download the content to your TORRENTDIR
        (TORRENTDIR != TORRENTFILESDIR)
	Call retorrent on the downloaded file.
        Retorrent will move the content to your media directory with a nice filename
        Retorrent will create symlinks in SEEDDIR with the original filenames
        Retorrent will find the matching .torrent file and move it to SEEDTORRENTFILESDIR

If you define multiple content directories (maybe you have many hard disks), use *symlinker* to create a separate directory tree with symlinks to all of your content. This may then be easily navigated and/or scanned by your media center software.

Removing a Torrent Workflow:
	Determine if content file foo.mkv is seeded using is_seeded.py
	If you still want to remove it, remove all the child symlinks using *remreffer*

Development:
  To lint the bash scripts in this repo (I'm sorry), you'll need to install
  shellcheck. It's not much, but it's something.
  https://github.com/koalaman/shellcheck
  Supported version: 0.3.4
