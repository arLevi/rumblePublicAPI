# rumblePublicAPI
Extract public information from Rumble ( youtube replacement )

# Dependencies
The following is required
```
import requests
import bs4
```

# Extracting Channel Information
'Channel` or `Playstlist information` - is taken from the channel URL like so: https://rumble.com/c/c-2296374
`Video ID` - is taken from a page like so: https://rumble.com/v2dsuho-144113244.html
`Video information - is taken from an API page like so: https://rumble.com/api/Media/oembed.json?url=https://rumble.com/embed/v2b7eve/

```
from rubmbleapi import RumbleChannel

# Channel URL example: https://rumble.com/c/c-2296374
channel = RumbleChannel("c-2296374")

print("Channel name:", channel.name)
print("Channel followers:", channel.followers)
print("Channel URL:", channel.url())
print("Channel num of playlists:", len(channel.playlists))

for playlist in channel.playlists:
    print("\nPlaylist information")
    print("--------------------")
    print("playlist.title:", playlist.title)
    print("playlist.link.href:", playlist.link.href)

    print("\nVideo information")
    print("-----------------")
    print("playlist.video id:", playlist.video.id)
    print("playlist.video.url():", playlist.video.url())
    print("playlist.video.thumbnail_url:", playlist.video.thumbnail_url)
    print("playlist.video.title:", playlist.video.title)
    print("playlist.video.duration:", playlist.video.duration)
```

### Output example
```
Channel name:
Channel followers: 2 Followers
Channel URL: https://rumble.com/c/c-2296374
Channel num of playlists: 5

Playlist information
--------------------
playlist.title: שבלול בצנצנת - רינת הופר
playlist.link.href: /v2dsuho-144113244.html

Video information
-----------------
playlist.video id: v2b7eve
playlist.video.url(): https://rumble.com/v2dsuho-144113244.html
playlist.video.thumbnail_url: https://sp.rmbl.ws/s8/1/C/5/V/L/C5VLi.qR4e-small--.jpg
playlist.video.title: שבלול בצנצנת - רינת הופר
playlist.video.duration: 248
```


