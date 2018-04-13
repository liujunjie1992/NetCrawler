#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import os
import time
from datetime import datetime
import traceback
import json
import re
import urllib2
import socks
from sockshandler import SocksiPyHandler
import logging
from bs4 import BeautifulSoup


def get_resp_by_url(_url):
    try:
        opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, "127.0.0.1", 1080))
        return opener.open(_url)
    except Exception as e:
        traceback.print_exc()
        logging.error(e.message)
    return None


def get_content_by_url(_url):
    _resp = get_resp_by_url(_url)
    if _resp:
        return _resp.read()
    else:
        return None


def get_user(_url):
    html = get_content_by_url(_url)
    soup = BeautifulSoup(html, "html.parser")
    n = soup.find("h1", class_="truncate")
    b = n.next_sibling
    user_id = None
    while b:
        if len(str(b).strip()) > 0 and b.get("data-view-signature"):
            match_obj = re.match(r".*__nsid_([\d|%|N]+)__", b.get("data-view-signature"), re.M | re.I)
            if match_obj:
                user_id = match_obj.group(1)
            break
        b = b.next_sibling
    match_obj = re.match(r".*root.YUI_config.flickr.api.site_key\s*=\s*\"([a-z0-9]*)\"", html, re.DOTALL)
    if match_obj:
        api_key = match_obj.group(1)
    match_obj = re.match(r".*root.YUI_config.flickr.api.site_key_expiresAt\s*=\s*(\d+)", html, re.DOTALL)
    if match_obj:
        expires_second = int(match_obj.group(1))
    return user_id, str(n.contents[0]).strip(), api_key, expires_second


def parse_and_download_photos(user_home_url):
    try:
        user_id, user_name, api_key, expires_second = get_user(user_home_url)
        user_dir = "./flickr/" + user_name
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)

        rest_url_fs = "https://api.flickr.com/services/rest?per_page={}&page={}&extras=can_addmeta%2Ccan_comment%2Ccan_download%2Ccan_share%2Ccontact%2Ccount_comments%2Ccount_faves%2Ccount_views%2Cdate_taken%2Cdate_upload%2Cdescription%2Cicon_urls_deep%2Cisfavorite%2Cispro%2Clicense%2Cmedia%2Cneeds_interstitial%2Cowner_name%2Cowner_datecreate%2Cpath_alias%2Crealname%2Crotation%2Csafety_level%2Csecret_k%2Csecret_h%2Curl_c%2Curl_f%2Curl_h%2Curl_k%2Curl_l%2Curl_m%2Curl_n%2Curl_o%2Curl_q%2Curl_s%2Curl_sq%2Curl_t%2Curl_z%2Cvisibility%2Cvisibility_source%2Co_dims%2Cis_marketplace_printable%2Cis_marketplace_licensable%2Cpubliceditability&get_user_info=1&jump_to=&user_id={}&privacy_filter=1&viewerNSID=&method=flickr.people.getPhotos&csrf=&api_key={}&format=json&hermes=1&hermesClient=1&reqId=d4b31ff3&nojsoncallback=1"

        sleep_second = 3
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        logging.basicConfig(filename="./logs/flickr_" + user_id + ".log", level=logging.DEBUG, format=LOG_FORMAT,
                            datefmt=DATE_FORMAT)
        expires_datetime = datetime.fromtimestamp(expires_second)
        expired_count = 0
        logging.info("user_id:%s, user_name:%s, api_key:%s, dir:%s, expired datetime:%s"
                     % (user_id, user_name, api_key, os.path.abspath(user_dir), expires_datetime))

        page_no = 1
        per_page_num = 100

        rest_url = rest_url_fs.format(per_page_num, page_no, user_id, api_key)
        json_str = get_content_by_url(rest_url)
        # print(json_str)
        data = json.loads(json_str)
        total_page_num = int(data["photos"]["pages"])
        total_img_num = int(data["photos"]["total"])

        while page_no <= total_page_num:
            try:
                # refresh home page to update api_key and expires_second when it expired
                if time.time() >= expires_second:
                    new_url = user_home_url + "page" + str(page_no)
                    logging.info("new_url:" + new_url)
                    user_id, user_name, api_key, expires_second = get_user(new_url)
                    expires_datetime = datetime.fromtimestamp(expires_second)
                    expired_count += 1
                    logging.info(
                        "user_id:%s, user_name:%s, api_key:%s, dir:%s, expired datetime:%s, expired_count:%d"
                        % (user_id, user_name, api_key, os.path.abspath(user_dir), expires_datetime,
                           expired_count))

                rest_url = rest_url_fs.format(per_page_num, page_no, user_id, api_key)
                json_str = get_content_by_url(rest_url)
                data = json.loads(json_str)
                info_data = data["photos"]["photo"]

                index = 1
                for info_item in info_data:
                    try:
                        # find biggest size photo url
                        img_url_key = None
                        max_height = 0
                        for key in info_item:
                            if str(key).startswith("height_"):
                                t_url_key = "url_" + str(key).split("_")[1]
                                if t_url_key in info_item:
                                    tag_height = int(info_item[key])
                                    if max_height < tag_height:
                                        img_url_key = t_url_key
                                        max_height = tag_height
                        img_url = info_item[img_url_key]

                        img_name = info_item["title"]
                        img_name = re.sub(r'[\\/:*?"<>|]', '-', img_name)
                        img_path = "./flickr/" + user_name + "/" + img_name + ".jpg"

                        if os.path.exists(img_path):
                            timestamp = str(time.time()).split(".")[0] + str(datetime.utcnow().microsecond / 1000)
                            img_path = str(img_path).replace(".jpg", "#" + timestamp + ".jpg")

                        logging.info("([" + str(page_no) + "/" + str(total_page_num) + "]"
                                     + " [" + str(index) + "/" + str(per_page_num) + "]"
                                     + " [" + str(index + (page_no - 1) * per_page_num) + "/" + str(total_img_num) + "]"
                                     + ")"
                                     + img_name + " -> " + img_url + " -> " + img_path)

                        try:
                            _resp = get_resp_by_url(img_url)
                            with open(img_path, "wb") as f:
                                f.write(_resp.read())
                        except Exception as e:
                            traceback.print_exc()
                            logging.error(e.message)

                        try:
                            time.sleep(1)
                        except Exception as e:
                            traceback.print_exc()
                            logging.error(e.message)

                        index += 1
                    except Exception as e:
                        traceback.print_exc()
                        logging.error(e.message)

                try:
                    time.sleep(sleep_second)
                except Exception as e:
                    traceback.print_exc()
                    logging.error(e.message)

                page_no += 1
            except Exception as e:
                traceback.print_exc()
                logging.error(e.message)

    except Exception as e:
        traceback.print_exc()
        logging.error(e.message)


if __name__ == "__main__":
    base_url = "https://www.flickr.com/photos/{}/"
    accounts = ["spacex", "137994134@N07", "wolfhorn", "nasahubble"]

    # for account in accounts:
    #     url = base_url.format(account)
    #     parse_and_download_photos(url)

    url = base_url.format(accounts[-1])
    parse_and_download_photos(url)
