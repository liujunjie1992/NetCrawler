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
from bs4 import BeautifulSoup
import logging


def get_img_url_and_id(img_url):
    o_items = img_url.split("/")
    img_name = o_items[-1]
    i_items = img_name.split("_")
    if len(i_items) > 2:
        img_name = "_".join(i_items[0:2]) + "_b." + img_name.split(".")[-1]
    else:
        img_name = "_".join(i_items).split(".")[0] + "_b." + img_name.split(".")[-1]
    return "https://" + "/".join(o_items[0:-1]) + "/" + img_name, img_name.split("_")[0]


def parse_save_img(div_eles, _info_data):
    if not div_eles or len(div_eles) == 0:
        print("Error div elements.")
        return
    for index in range(1, len(div_eles)):
        try:
            div_ele = div_eles[index]
            # print(div_ele)
            style_str = div_ele.get("style")
            if style_str:
                match_obj = re.match(r".*\(//(.*)\)", style_str, re.M | re.I)
                if match_obj:
                    img_url_str, img_id = get_img_url_and_id(match_obj.group(1))
                    img_name = None
                    # print(img_id)
                    for info_item in _info_data:
                        if img_id == info_item["id"]:
                            img_name = info_item["title"]
                            break
                    if img_name:
                        img_name = re.sub(r'[\\/:*?"<>|]', '-', img_name)
                        img_path = "./flickr/" + img_name + ".jpg"

                        _resp = urllib2.urlopen(img_url_str)

                        if os.path.exists(img_path):
                            timestamp = str(time.time()).split(".")[0] + str(datetime.utcnow().microsecond / 1000)
                            img_path = str(img_path).replace(".jpg", "#" + timestamp + ".jpg")

                        logging.info(img_name + " -> " + img_url_str + " -> " + img_path)
                        try:
                            with open(img_path, "wb") as f:
                                f.write(_resp.read())
                        except Exception as e:
                            traceback.print_exc()
                            logging.error(e.message)
                    else:
                        logging.info(img_id + "<" + img_url_str + ">" + " not find title.")

                    try:
                        time.sleep(1)
                    except Exception as e:
                        traceback.print_exc()
                        logging.error(e.message)
                    # print("*" * 120)
        except Exception as e:
            traceback.print_exc()
            logging.error(e.message)


if __name__ == "__main__":
    try:
        base_url_str = "https://www.flickr.com"
        user_name = "137994134@N07"

        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
        logging.basicConfig(filename="./logs/flickr_" + user_name + ".log", level=logging.DEBUG, format=LOG_FORMAT,
                            datefmt=DATE_FORMAT)

        response = urllib2.urlopen(base_url_str + "/photos/" + user_name + "/with/41309663572/")
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        next_page_ele = soup.find("link", rel="next")
        sleep_second = 3
        page_no = 1
        while next_page_ele:
            # parse and save img
            # print(html)
            try:
                logging.info("start download page no." + str(page_no))
                rest_url = "https://api.flickr.com/services/rest?per_page=100&page=" + str(
                    page_no) + "&extras=can_addmeta%2Ccan_comment%2Ccan_download%2Ccan_share%2Ccontact%2Ccount_comments%2Ccount_faves%2Ccount_views%2Cdate_taken%2Cdate_upload%2Cdescription%2Cicon_urls_deep%2Cisfavorite%2Cispro%2Clicense%2Cmedia%2Cneeds_interstitial%2Cowner_name%2Cowner_datecreate%2Cpath_alias%2Crealname%2Crotation%2Csafety_level%2Csecret_k%2Csecret_h%2Curl_c%2Curl_f%2Curl_h%2Curl_k%2Curl_l%2Curl_m%2Curl_n%2Curl_o%2Curl_q%2Curl_s%2Curl_sq%2Curl_t%2Curl_z%2Cvisibility%2Cvisibility_source%2Co_dims%2Cis_marketplace_printable%2Cis_marketplace_licensable%2Cpubliceditability&get_user_info=1&jump_to=&user_id=137994134%40N07&privacy_filter=1&viewerNSID=&method=flickr.people.getPhotos&csrf=&api_key=2775b0b7a4a7568a28afbf476ae5da74&format=json&hermes=1&hermesClient=1&reqId=d4b31ff3&nojsoncallback=1"
                resp = urllib2.urlopen(rest_url)
                json_str = resp.read()
                data = json.loads(json_str)
                info_data = data["photos"]["photo"]
                # print(json.dumps(info_data))
                parse_save_img(soup.find_all("div", class_="photostream"), info_data)

                # next page
                print(next_page_ele)
                response = urllib2.urlopen(base_url_str + next_page_ele.get("href"))
                html = response.read()
                soup = BeautifulSoup(html, "html.parser")
                next_page_ele = soup.find("link", rel="next")
                page_no += 1

                try:
                    time.sleep(sleep_second)
                except Exception as e:
                    traceback.print_exc()
                    logging.error(e.message)
            except Exception as e:
                traceback.print_exc()
                logging.error(e.message)

    except Exception as e:
        traceback.print_exc()
        logging.error(e.message)
