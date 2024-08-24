try:
    from utils import fread, fwrite
except ImportError:
    from .utils import fread, fwrite

from zipfile import ZipFile
import threading
import requests
import random
import json
import cv2
import re
import os

user_agent_list = [
    'Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.61 Chrome/126.0.6478.61 Not/A)Brand/8  Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0 Config/100.2.9281.82',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0 (Edition Yx 05)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/128.0.0.0'
]

class Pixiv:
    def __init__(self,
                my_id      :int,
                cookies    :str,
                proxy      :str = 'http://127.0.0.1:1080/',
                maxThreads :int = 8):
        self._my_id   = my_id
        self._proxies = {'http': proxy, 'https': proxy} if proxy else None
        self._cookies = fread(cookies).decode() if os.path.exists(cookies) else cookies
        self._threads = maxThreads

        self._headers = {
            'Cookie': self._cookies,
            'Accapt-Language': 'zh-CN, zh;q=0.9, en;q=0.8, jp;q=0-7',
            'Referer': 'https://www.pixiv.net/',
            'User-Agent': random.choice(user_agent_list)
        }

        self.status_done   = 2
        self.status_exists = 1
        self.status_failed = 0

    def threads_call(self, function :callable, item_list :list[str]):
        ths = [
            threading.Thread(target = function, args = (th_id, item_list))
            for th_id in range(self._threads)
        ]
        for th in ths:
            th.start()
        for th in ths:
            th.join()

    def http_get(self, url :str):
        return requests.get(url,  headers = self._headers, proxies = self._proxies)

    def create_filename_form_url(self, url :str):
        result :str = re.findall(
                            r'^\w+://'
                            r'[\w\d.]+/'
                            r'[\w\-\_]+/img/'
                            r'([\w\d./\_]+)$',
                            url, re.S)[0]
        return result.replace('/', '_')

    def image_to_mp4(self, image_path :list[str], mp4_path :str, fps :int = 15):
        image_array = []
        
        for fn in image_path:
            ctx = cv2.imread(fn)
            height, width, layers = ctx.shape
            image_array.append(ctx)

        with cv2.VideoWriter(mp4_path, cv2.VideoWriter_fourcc(*'DIVX'),
                            fps, (width, height)) as mp4_ctx:
            for image in image_array:
                mp4_ctx.write(image)

    def zip_to_mp4(self, url :str, file_save_path :str, content :bytes, mp4_save_path :str):
        fwrite(file_save_path, data = content)

        with ZipFile(file_save_path, 'r') as ctx:
            zip_fn_list = ctx.namelist()
            img2mp4_tmp_path = f'{file_save_path}_tmp'
            
            if not os.path.exists(img2mp4_tmp_path):
                os.makedirs(img2mp4_tmp_path)

            ctx.extractall(img2mp4_tmp_path)

        image_path = [
            os.path.join(img2mp4_tmp_path, fn)
            for fn in zip_fn_list
        ]
        mp4_fn = self.create_filename_form_url(url).replace('zip', 'mp4')

        self.image_to_mp4(image_path, os.path.join(mp4_save_path, mp4_fn))

        for fn in image_path:
            os.remove(fn)

        os.remove(file_save_path)
        os.removedirss(img2mp4_tmp_path)

    def download(self, url :str, save_path :str, zip2mp4 :bool = True):
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        image_save_path = os.path.join(save_path, self.create_filename_form_url(url))

        if os.path.exists(image_save_path) or os.path.exists(image_save_path.replace('zip', 'mp4')):
            return self.status_exists

        try:
            response = self.http_get(url)
        except Exception as e:
            return self.status_failed, e

        if (response.headers['Content-Type'] == 'application/zip') and zip2mp4:
            self.zip_to_mp4(url, image_save_path, response.content, save_path)
        else:
            fwrite(image_save_path, data = response.content)

        return True

    def threads_download(self, urls :list[str], save_path :str):
        def __download(th_id :int, urls :list[str]):
            for item in range(th_id, len(urls), self._threads):
                status = self.download(urls[item], save_path)
                if status == self.status_exists:
                    print(f'\'{urls[item]}\' exists.')
                elif status == self.status_failed:
                    print(f'\'{urls[item]}\' failed.')
        self.threads_call(__download, urls)

class PixivArtworks(Pixiv):
    def __init__(self,
                cookies :str,
                my_id :int = 0,
                proxy :str = 'http://127.0.0.1:1080/',
                maxThreads :int = 8):
        super().__init__(my_id, cookies, proxy, maxThreads)

    '''
    获取指定页码中已关注的作者的UID
    
    page: 页码
    offset: 偏移量（如果你不知道，那说明你不该自己调用这个方法）
    '''
    def get_followed_artist_uids_by_page(self, page :int, offset :int) -> list[str]:
        print('call get_followed_artist_uids_by_page.')
        url = (
            f'https://www.pixiv.net/ajax/user/{self.myself_id}/following'
            f'?offset={page * offset}&limit={offset}&rest=show'
        )

        response = self.http_get(url).json()

        if not response['body']['users']:
            return False

        return [item['userId'] for item in response['body']['users']]

    '''
    获取自己已关注的所有作者的UID
    
    offset: 偏移量
    '''
    def get_all_followed_artist_uids(self, offset :int = 24):
        print('call get_all_followed_artist_uids.')
        results = []
        
        for page in range(0, int(offset * 1e6)):
            result = self.get_followed_artist_uids_by_page(page, offset)
            
            if not result:
                break
            
            results.extend(result)

        return results

    '''
    获取作品页面中所有的动态图像（一般来说，你不应该自己调用这个方法）
    
    @return 如果作品不是动态图，就返回False，否则返回压缩包链接。
    @param
        artworkID: 作品ID
    '''
    def get_artworks_illust_images_url_for_dynamic(self, artworkID :int) -> str | bool:
        print('call get_artworks_illust_images_url_for_dynamic.')
        dynamic_images_url = f'https://www.pixiv.net/ajax/illust/{artworkID}/ugoira_meta'
        dynamic_images_response = self.http_get(dynamic_images_url).json()
        if dynamic_images_response['error'] == False:
            return dynamic_images_response['body']['originalSrc']
        return False

    '''
    获取作品页面中所有的静态图像（一般来说，你不应该自己调用这个方法）
    
    @return 如果作品不是静态图，就返回False，否则返回作品链接列表。
            但通常来说，这个永远不会返回False，所以应该直接判断是否是动态图。
    @param
        artworkID: 作品ID
    '''
    def get_artworks_illust_images_url_for_static(self, artworkID :int) -> list[str] | bool:
        print('call get_artworks_illust_images_url_for_static.')
        static_images_url = f'https://www.pixiv.net/ajax/illust/{artworkID}/pages'
        static_images_response = self.http_get(static_images_url).json()
        results = []
        if static_images_response['error'] == False:
            for item in static_images_response['body']:
                original_url = item['urls']['original']
                results.append(original_url)
            return results
        return False

    '''
    获取作品页面中所有图像（自动区分静态图和动态图）
    
    @return 如果是动态图就返回压缩包链接否则静态图列表。
    @param
        artworkID: 作品ID
    '''
    def get_artworks_illust_images_url(self, artworkID :int):
        print('call get_artworks_illust_images_url.')
        dynamic_result = self.get_artworks_illust_images_url_for_dynamic(artworkID)
        if dynamic_result == False:
            return self.get_artworks_illust_images_url_for_static(artworkID)
        return dynamic_result

    '''
    获取指定作者的所有作品页面中所有图像（自动区分静态图和动态图）
    
    @return 含可能的压缩包链接和静态图链接的列表
    @param
        artistID: 作者UID
    '''
    def get_artist_artwork_images_url(self, artistID :int) -> list[str]:
        print('call get_artist_artwork_images_url.')
        url = f'https://www.pixiv.net/ajax/user/{artistID}/profile/all'
        artworks_keys = [*self.http_get(url).json()['body']['illusts'].keys()]

        self.links = []
        def get_images(th_id :int, artworks :list[int]):
            for pid in range(th_id, len(artworks), self._threads):
                _pid = artworks[pid]
                dynamic_result = self.get_artworks_illust_images_url_for_dynamic(_pid)
                static_result  = self.get_artworks_illust_images_url_for_static(_pid)
                
                if dynamic_result == False:
                    self.links.extend(static_result)
                else:
                    self.links.append(dynamic_result)

        self.threads_call(get_images, artworks_keys)
        return self.links

class PixivBookmarks(Pixiv):
    def __init__(self,
                cookies :str,
                my_id :int = 0,
                proxy :str = 'http://127.0.0.1:1080/',
                maxThreads :int = 8):
        super().__init__(my_id, cookies, proxy, maxThreads)

    '''
    获取指定的收藏夹页码中的所有作品ID。
    
    @param
        userId  指定的用户ID
        page    页码数
        tag     收藏的Tag
        rest    公开收藏夹(show) or 非公开收藏夹(hide)
    @return
        返回一个作品ID列表
    '''
    def get_bookmarks_artworks(self, userId :int, page :int, tag :str = '', rest :str = 'show'):
        results = []
        limit   = 48 # 单次累加的最小量

        url = (
            f'https://www.pixiv.net/ajax/user/{userId}/illusts/bookmarks'
            f'?tag={tag}&offset={(page-1)*limit}&{limit=}&rest={rest}'
        )

        response = self.http_get(url).json()

        for item in response['body']['works']:
            results.append(item['id'])

        return results

if __name__ == '__main__':
    cookie_path = 'e:/pixiv_cookie.txt'
    proxy = 'http://127.0.0.1:8081'
    
    pix_bm = PixivBookmarks(cookie_path, proxy = proxy)
    pix_aw = PixivArtworks(cookie_path, proxy = proxy)

    bookmarks_artwork_ids = pix_bm.get_bookmarks_artworks(38279179, 1)
    for artwork_id in bookmarks_artwork_ids:
        for url in pix_aw.get_artworks_illust_images_url(artwork_id):
            res = pix_bm.download(url, 'f:/Pitchers/Pixiv/手动保存/test')
            print(res)

