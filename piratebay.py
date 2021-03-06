#VERSION: 3.0
# AUTHORS: Fabien Devaux (fab@gnux.info)
# CONTRIBUTORS: Christophe Dumez (chris@qbittorrent.org)
#               Arthur (custparasite@gmx.se)
#               Diego de las Heras (ngosang@hotmail.es)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import json
from urllib.parse import urlencode, unquote

from novaprinter import prettyPrinter
from helpers import retrieve_url


class piratebay(object):
    url = 'https://thepiratebay.org'
    name = 'The Pirate Bay'
    supported_categories = {
        'all': '0',
        'music': '100',
        'movies': '200',
        'games': '400',
        'software': '300'
    }

    # initialize trackers for magnet links
    trackers_list = [
        'udp://tracker.coppersurfer.tk:6969/announce',
        'udp://tracker.leechers-paradise.org:6969/announce',
        'udp://tracker.opentrackr.org:1337/announce',
        'udp://tracker.openbittorrent.com:80/announce',
        'udp://exodus.desync.com:6969/announce',
        'udp://9.rarbg.me:2710/announce',
        'udp://9.rarbg.to:2710/announce',
        'udp://tracker.tiny-vps.com:6969/announce',
        'udp://retracker.lanta-net.ru:2710/announce',
        'udp://open.demonii.si:1337/announce'
    ]
    trackers = '&'.join(urlencode({'tr': tracker}) for tracker in trackers_list)

    def search(self, what, cat='all'):
        base_url = "https://apibay.org/q.php?%s"
        torrentList = []

        # get response json
        what = unquote(what)
        category = self.supported_categories[cat]
        params = {'q': what}
        if category != '0':
            params['cat'] = category
        response = retrieve_url(base_url % urlencode(params))
        response_json = json.loads(response)

        # check empty response
        if len(response_json) == 0:
            return

        # parse results
        for result in response_json:
            res = {
                'link': self.download_link(result),
                'name': result['name'],
                'size': str(result['size']) + " B",
                'seeds': result['seeders'],
                'leech': result['leechers'],
                'engine_url': self.url,
                'desc_link': self.url + '/description.php?id=' + result['id']
            }
            templist = []
            templist.append(res['name'])
            templist.append(res['seeds'])
            templist.append(res['leech'])
            templist.append(res['size'])
            templist.append(res['link'])
            torrentList.append(templist)
        
        return torrentList

    def download_link(self, result):
        return "magnet:?xt=urn:btih:{}&{}&{}".format(
            result['info_hash'], urlencode({'dn': result['name']}), self.trackers)
