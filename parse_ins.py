#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import os
import re
import codecs
import json
import time
from datetime import datetime
import traceback
import cookielib
import urllib2
import logging
from urllib import urlencode
import socks
from sockshandler import SocksiPyHandler


def get_resp_by_url(_url, _cookie=None, _headers=None, _params=None):
    try:
        req = urllib2.Request(_url)
        if _headers:
            for header_key in _headers.keys():
                req.add_header(header_key, _headers[header_key])
        opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, "127.0.0.1", 1080))
        opener.add_handler(urllib2.HTTPCookieProcessor(_cookie))
        if _params:
            req.add_data(_params)
        return opener.open(req)
    except urllib2.HTTPError, e:
        print(e.code)
        traceback.print_exc()
    except Exception as e:
        traceback.print_exc()
        print(e)
        # logging.error(e.message)
    return None


def get_content_by_url(_url, _cookie=None, _headers=None, _params=None):
    _resp = get_resp_by_url(_url, _cookie=_cookie, _headers=_headers, _params=_params)
    if _resp:
        return _resp.read()
    else:
        return None


def download_img_or_video(_edge, _user_dir, _is_video):
    try:
        _node = _edge["node"]
        _id = _node["id"]

        _url = _node["display_url"]
        _path = _user_dir + os.sep + str(_id) + (".mp4" if _is_video else ".jpg")
        _resp = get_resp_by_url(_url)
        with open(_path, "wb") as f:
            f.write(_resp.read())

        _desc_path = _user_dir + os.sep + str(_id) + ".txt"
        _desc = _edge["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
        with codecs.open(_desc_path, 'a', encoding='utf-8') as f:
            f.writelines(_desc)

        logging.info("id:%s, url:%s, path:%s" % (str(_id), _url, _path))
    except Exception as e:
        traceback.print_exc()
        logging.error(e.message)


def get_file_content(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    return content


def parse_ins_imgs(_user_name):
    url = "https://www.instagram.com/{}/".format(_user_name)
    home_url = url
    cookie_file_path = "ins_cookie.txt"
    cookie = cookielib.MozillaCookieJar(cookie_file_path)
    user_dir = "./ins/"+_user_name
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(filename="./logs/ins_" + _user_name + ".log", level=logging.DEBUG, format=LOG_FORMAT,
                        datefmt=DATE_FORMAT)

    headers = dict()
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
    # headers['content-type'] = ['application/x-www-form-urlencoded']
    # headers['x-instagram-ajax'] = '1'


    html = get_content_by_url(url, _cookie=cookie, _headers=headers)
    # print(html)
    # return

    match_obj = re.match(r".*window._sharedData\s*=\s*(.*);</script>", html, re.DOTALL)
    if match_obj:
        matched_str = match_obj.group(1)
        data_str = str(matched_str).split("</script")[0]
        if data_str.endswith(';'):
            data_str = data_str[:-1]
        # print(data_str)
        data = json.loads(data_str)
        user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        user_id = user["id"]
        logging.info("user_id: " + user_id)
        info_data = user["edge_owner_to_timeline_media"]
        edges = info_data["edges"]
        page_info = info_data["page_info"]

        img_total_count = info_data["count"]
        img_index = 0

        end_cursor = page_info["end_cursor"]
        has_next_page = page_info["has_next_page"]
        logging.info("img count:%d, has_next_page:%s, end_cursor:%s" % (img_total_count, has_next_page, end_cursor))

        # for edge in edges:
        #     img_index += 1
        #     logging.info("\n=====" + str(img_index) + "/" + str(img_total_count) + "=====")
        #     is_video = edge["node"]["is_video"]
        #     if not is_video:
        #         download_img_or_video(edge, user_dir, is_video)
        #     time.sleep(1)
        time.sleep(5)

        # cookie_str = """mid=Ws2SawALAAF42WHUG5J3X2dqK8fR; ig_vw=1366; ig_pr=1; ig_or=landscape-primary; shbid=11539; rur=FTW; fbm_124024574287414=base_domain=.instagram.com; csrftoken=i6KkkboXSg6KTEE60f3uZAq27xZMexm7; ds_user_id=4868765104; sessionid=IGSCaba82c1fa5870ab83dce032bcd5a2025cdca74869afc2b2682946fafd076d6ee%3AAiN35OCJmzFNZMztsPX49yzyi59pPBxC%3A%7B%22_auth_user_id%22%3A4868765104%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_platform%22%3A4%2C%22_token_ver%22%3A2%2C%22_token%22%3A%224868765104%3A5F6fIVVlIMjish1u1w4C7rtfZen7kxO5%3A28e0891ada292fb74de52dcff2b7f985d4a88a5d4ead83a34245eb5c329d0591%22%2C%22last_refreshed%22%3A1523517446.7438130379%7D; ig_vh=637; urlgen="{\\"time\\": 1523509888\\054 \\"202.5.17.140\\": 7489}:1f6rfu:Rbew0zj7cwXQGcOBDv_0oKR1L7c"""
        # for n_k in n_cookie.keys():
        #     n_v = n_cookie[n_k]
        #     ck = cookielib.Cookie(version=0, name=n_k, value=n_v, port=None, port_specified=False,
        #                           domain="www.instagram.com", domain_specified=False, domain_initial_dot=False,
        #                           path='/', path_specified=False, secure=False, expires=None, discard=True,
        #                           comment=None, comment_url=None, rest={'HttpOnly': None})
        #     cookie.set_cookie(ck)
        #
        csrf_token = data["config"]["csrf_token"]
        print("csrf_token:%s" % csrf_token)
        for cookie_item in cookie:
            print("name:%s, value:%s, expires:%s" %
                  (cookie_item.name, cookie_item.value, str(cookie_item.expires)))
        # headers["cookie"] = cookie_str
        headers['x-requested-with'] = 'XMLHttpRequest'
        headers['Referer'] = home_url
        # print("\nheaders.................")
        # for h_k in headers.keys():
        #     print("name:%s, value:%s" % (h_k, headers[h_k]))

        query_hash = "bfe6fc64e0775b47b311fc0398df88a9"
        # variables = {"id": user_id, "include_chaining": False, "include_reel": False, "include_suggested_users": False,
        #              "include_logged_out_extras": True}
        # query = {"query_hash": query_hash, "variables": json.dumps(variables)}
        # url = "https://www.instagram.com/graphql/query/?" + urlencode(query)
        # print("\nurl.................")
        # print(url)
        # json_str_demo = get_content_by_url(url, _cookie=cookie, _headers=headers)
        # print("json_str_demo:")
        # print(json_str_demo)

        while has_next_page:
            variables = {"id": user_id, "first": len(edges), "after": end_cursor}
            query = {"query_hash": query_hash, "variables": json.dumps(variables)}
            url = "https://www.instagram.com/graphql/query/?" + urlencode(query)
            print(url)
            try:
                json_str = get_content_by_url(url, _cookie=cookie, _headers=headers)
                print(json_str)

                has_next_page = False
                break
                data_obj = json.loads(json_str)
                if "status" in data_obj and data_obj["status"] == "ok":
                    info_data = data_obj["data"]["user"]["edge_owner_to_timeline_media"]
                    page_info = info_data["page_info"]
                    end_cursor = page_info["end_cursor"]
                    has_next_page = page_info["has_next_page"]
                    edges = info_data["edges"]
                    for edge in edges:
                        img_index += 1
                        logging.info("\n=====" + str(img_index) + "/" + str(img_total_count)+"=====")
                        is_video = edge["node"]["is_video"]
                        if not is_video:
                            download_img_or_video(edge, user_dir, is_video)
                        time.sleep(1)

            except Exception as e:
                print(e)
                traceback.print_exc()

            time.sleep(3)


if __name__ == "__main__":
    parse_ins_imgs("paulnicklen")