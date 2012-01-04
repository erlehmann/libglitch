libglitch makes 8-bit sounds in the spirit of viznut's [“algorithmic symphonies”][1], using a small language not entirely unlike Forth. Included is a small programm reading formulas from the command line. GNU/Linux users may try “./glitter.py glitch_machine!a10k4h1f!aAk5h2ff!aCk3hg!ad3e!p!9fm!a4kl13f!aCk7Fhn | aplay -f u8” for playback.

Using sox, sound can easily be exported into wave files: “./glitter.py `cat tracks/sidekick.glitch` | head -c128000 | sox -c 1 -r 8000 -t u8 - sidekick.wav”.

For editing and visual effects, try “./glitched.py [filename]”. Controls are the arrow keys (to move the cursor around), page up / page down (to change the opcode), space (to for no opcode), t (for the counter) and all hexadecimal digit keys (for insertion of the corresponding characters). Symbol keys (plus, minus etc.) may also work.

In glitched, press F4 to switch between waveform and stack visualisation. F5, F6, F7, F8 provide finer control over visualisation options. Press all of them in order to see a stack visualisation. F9 shows the current value of the counter (“t”).

libglitch is inspired by a [comment from madgarden][2], who kindly provided the [opcodes][3] he uses in his iOS application [“Glitch Machine”][4] and [some source code][5]. There is also a [Scala implementation][6].

[1]: http://countercomplex.blogspot.com/2011/10/algorithmic-symphonies-from-one-line-of.html

[2]: http://countercomplex.blogspot.com/2011/10/some-deep-analysis-of-one-line-music.html?showComment=1320185523164#c8205241663616732766

[3]: http://paste.ubuntu.com/733764/

[4]: http://madgarden.net/apps/glitch-machine/

[5]: http://paste.ubuntu.com/733829/

[6]: https://github.com/Lymia/ScalaGlitch

License
-------

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
       
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
