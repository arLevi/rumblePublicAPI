#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup


class RumbleAPIBase(object):
    
    def __init__(self):
        self.encoding = "utf-8"
        self.http_base = 'https://rumble.com'
        self.http_base_embed = "https://rumble.com/embed"
        self.http_base_api = "https://rumble.com/api/Media/oembed.json?url="

    def get_api_content(self, endpoint):
        """
        GET the url requested
        endpoint | (string) of the URL
        """
        return requests.get(f"{self.http_base_api}{endpoint}").json()

    def get_content(self, endpoint):
        """ Load the content from the website
            Return: BeautifulSoup object

            endpoint | (string) of the endpoint to access
        """
        page = requests.get(f"{self.http_base}{endpoint}")
        page.encoding = self.encoding
        return BeautifulSoup(page.content, "html.parser")


class RumbleImageThumb(object):

    def __init__(self, img=None):
        self.src = ''
        self.alt = ''

        if img:
            self.src = img.attrs.get('src', '')
            self.alt = img.attrs.get('alt', '')


class RumbleATag(RumbleAPIBase):
    def __init__(self, a=None):
        super().__init__()

        self.href = ''
        if a:
            self.href = a.attrs.get('href', '')

    def url(self):
        return f"{self.http_base}{self.href}"

class RumbleVideo(RumbleAPIBase):

    def __init__(self, endpoint):
        """
        endpoint | (string) of the video similar to: /v2dsuho-144113244.html 
        """
        super().__init__()
        self.http_endpoint = endpoint
        self.html     = ""
        self.html_api = ""

        self._id = None
        
    def url(self):
        return f"{self.http_base}{self.http_endpoint}"

    @property
    def id(self):
        if not self._id:
            self._load_video_id()
        return self._id

    @property
    def author_name(self):
        return self._info('author_name')

    @property
    def thumbnail_url(self):
        return self._info('thumbnail_url')
    
    @property
    def title(self):
        return self._info('title')

    @property
    def duration(self):
        return self._info('duration')

    @property
    def author_url(self):
        return self._info('author_url')
    
    @property
    def channel_url(self):
        return self.author_url

    @property
    def channel_name(self):
        return self.author_name


    def _load_video_id(self):
        self.html = self.get_content(self.http_endpoint)
        pattern = re.compile(r'"embedUrl":"https://rumble.com/embed/(\w+?)/"')
        html = self.html.findAll(string=pattern)

        for m in html:
            # we expect only one
            self._id = pattern.search(m.parent.text).group(1)
            return

    def _info(self, key, default=''):
        if not self.html_api:
            if not self._id:
                self._load_video_id()

            self._load_information()

        return self.html_api.get(key, default)

    def _load_information(self):
        """
        Load more video information Rumble API
        i.e: https://rumble.com/api/Media/oembed.json?url=https://rumble.com/embed/{vid}/
        {
          "type": "video",
          "version": "1.0",
          "title": "שבלול בצנצנת - רינת הופר",
          "author_name": "סיפורי ילדים גילאים 4Y 5Y 6Y",
          "author_url": "https://rumble.com/c/c-2296374",
          "provider_name": "Rumble.com",
          "provider_url": "https://rumble.com/",
          "html": "<iframe src=\"https://rumble.com/embed/v2b7eve/\" width=\"1280\" height=\"720\" frameborder=\"0\" title=\"שבלול בצנצנת - רינת הופר\" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>",
          "width": 1280,
          "height": 720,
          "duration": 248,
          "thumbnail_url": "https://sp.rmbl.ws/s8/1/C/5/V/L/C5VLi.qR4e-small--.jpg",
          "thumbnail_width": 1280,
          "thumbnail_height": 720
        }
        """
        if not self.id:
            return

        self.html_api = self.get_api_content(f"{self.http_base_embed}/{self.id}")
        

class RumblePlaylistItem(object):

    def __init__(self, bs_el):
        """
        bs_el | (BeautifulSoup item)
        """
        self.html = bs_el

        self.thumb = self._parse_thumb()
        self.title = self._parse_title()
        self.link  = self._parse_link()
        self.views = self._parse_video_views()

        self.video = self._parse_video()

    def as_json(self):
        """ return item as json """
        return {
            "title": self.title,
            "id"   : self.video.id,
            "thumb": self.thumb.src
        }

    def _parse_thumb(self):
        try:
            return RumbleImageThumb(self.html.find("img", class_="video-item--img"))
        except Exception as e:
            return RumbleImageThumb()

    def _parse_title(self):
        try:
            return self.html.find("h3", class_="video-item--title").text
        except Exception as e:
            return ''

    def _parse_link(self):
        try:
            return RumbleATag(self.html.find("a", class_="video-item--a"))
        except Exception as e:
            return RumbleATag()

    def _parse_video_views(self):
        try:
            return self.html.find("div", class_="video-counters--item video-item--views")
        except Exception as e:
            return 0

    def _parse_video(self):
        """ Parse the video ID which isn't found here, it's found inside the page's video """
        return RumbleVideo(self.link.href)


class RumbleChannel(RumbleAPIBase):

    def __init__(self, channel):
        super().__init__()

        self.channel_id   = channel
        self.name = ""
        self.followers    = "0 followers"

        self.http_endpoint  = f"/c/{self.channel_id}"
        self.html = self.get_content(self.http_endpoint)

        self._playlists = []
        self._playlists_loaded = False  # just in case there are no playlists in this channel

        # Channel and playlist information
        self._load()
        self._load_playlists()

    @property 
    def playlists(self):
        if self._playlists_loaded:
            return self._playlists
        else:
            self._load_playlists()

    def url(self):
        """ Return that channel's URL """
        return f"{self.http_base}{self.http_endpoint}"

    def _load(self):
        """ Load channel information """
        self.channel_name = self.html.find("title").text
        try:
            self.followers = self.html.find("span", class_="listing-header--followers").text
        except:
            self.followers = 0
        
    def _load_playlists(self):
        self._playlists_loaded = True
        items = self.html.find_all("li", class_="video-listing-entry")

        for v in items:
            self._playlists.append(RumblePlaylistItem(v))
        

if __name__ == "__main__":
    # Channel: https://rumble.com/c/c-2296374
    channel = RumbleChannel("c-2296374")

    print("Channel name:", channel.name)
    print("Channel followers:", channel.followers)
    print("Channel URL:", channel.url())
    print("Channel num of playlists:", len(channel.playlists))

    for playlist in channel.playlists:
        print("Playlist information")
        print("--------------------")
        print("playlist.title:", playlist.title)
        print("playlist.link.href:", playlist.link.href)
        print("playlist.thumb.src:", playlist.thumb.src)
        
        print("Video information")
        print("-----------------")
        print("Playlist.video id:", playlist.video.id)
        print("playlist.video.url():", playlist.video.url())
        print("playlist.video.thumbnail_url:", playlist.video.thumbnail_url)
        print("playlist.video.title:", playlist.video.title)
        print("playlist.video.duration:", playlist.video.duration)

        print("As JSON")
        print("-------")
        print(playlist.as_json())




