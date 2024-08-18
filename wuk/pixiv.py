from .utils import fread, fwrite
from zipfile import ZipFile
import threading
import requests
import json
import cv2
import re
import os

def fwrite_json(path :str, json_data :dict):
    fwrite(path, data = json.dumps(json_data, ensure_ascii = False, indent = 4).encode())

class pixiv:
    '''
    这里需要着重声明一个事情，如果你在调用getTotalArtistList方法后发现得到的数量少于Pixiv官网的数量。
    这不是我代码的问题，这是Pixiv的问题。
    不信的话你可以在getArtistList方法中检测每一页的作者数量然后和Pixiv官网的那一页的数量作对比。
    
    :myID 你自己在Pixiv的ID
    :cookies 你在Pixiv的Cookie，可以cookie明文文件的路径也可以直接是cookie字符串。
    :save_path 你需要将下载的图片保存在哪
    :proxies 你设置的代理（如果需要）
    :maxNumberThreads 多线程下载时使用的线程数
    '''
    def __init__(self,
                myID             :str | int,
                cookies          :str,
                save_path        :str,
                proxies          :str = 'http://localhost:1080',
                maxNumberThreads :int = 8):
        self.maxNumberThreads = maxNumberThreads
        self.myself_id = myID
        self.save_path = save_path
        self.cookies   = None
        
        self.STATUS_DONE   = 1
        self.STATUS_EXISTS = -1
        self.STATUS_FAILED = 0

        if not os.path.exists(cookies):
            self.cookies = cookies
        elif os.path.exists(cookies):
            self.cookies = fread(cookies).decode()
        else:
            raise ValueError('缺少Cookie，无法进行爬取。')

        self.proxies = {'http': proxies, 'https': proxies} if proxies else None
        self.headers = {
            'Cookie': self.cookies,
            'Accapt-Language': 'zh-CN, zh;q=0.9, en;q=0.8',
            'Referer': 'https://www.pixiv.net/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0'
        }

    # 开启指定数量的线程并执行
    def __threads(self, func :callable, url_list :list[str]):
        th_list = [threading.Thread(target = func, args = (thId, url_list)) for thId in range(self.maxNumberThreads)]

        for th in th_list:
            th.start()

        for th in th_list:
            th.join()

    # 封装HTTP请求
    def __http_get(self, url :str):
        return requests.get(url, headers = self.headers, proxies = self.proxies)

    # 根据下载链接来创建一个文件名
    def __create_filename(self, url :str):
        return re.findall(r'\w+://[a-zA-Z0-9.\-\_]+/[a-zA-Z\-\_]+/img/([0-9a-zA-Z./\_]+)',
            url, re.S | re.I)[0].replace('/', '_')

    # 指定一个Jpg图像文件路径的列表，将它们依次转为视频的每一帧
    def __img_to_mp4(self, inPath :list[str], outPath :str, fps :int = 15):
        img_array = []

        for filename in inPath:
            img = cv2.imread(filename)
            height, width, layers = img.shape
            img_array.append(img)

        out = cv2.VideoWriter(outPath, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

        for i in img_array:
            out.write(i)

        out.release()

    # 将Zip压缩包里面的图像转为视频
    def __zip_to_mp4(self, link :str, fileSavePath :str, content :bytes, folder :str):
        fwrite(fileSavePath, data = content)

        with ZipFile(fileSavePath, 'r') as ctx:
            zip_filename_list = ctx.namelist()
            jpgToMp4TempSavePath = f'{fileSavePath}_Temp'

            if not os.path.exists(jpgToMp4TempSavePath):
                os.makedirs(jpgToMp4TempSavePath)

            ctx.extractall(jpgToMp4TempSavePath)

        jpgPath = [os.path.join(jpgToMp4TempSavePath, fn) for fn in zip_filename_list]
        gifFileName = self.__create_filename(link).replace('zip', 'mp4')

        self.__img_to_mp4(jpgPath, os.path.join(folder, gifFileName))

        for fn in jpgPath:
            os.remove(fn)

        os.remove(fileSavePath)
        os.removedirs(jpgToMp4TempSavePath)

    # 获取指定页码中所有作者ID
    def get_followed_artist_uids_by_page(self, page :int, offset :int) -> list[str]:
        url = (
            f'https://www.pixiv.net/ajax/user/{self.myself_id}/following'
            f'?offset={page * offset}&limit={offset}&rest=show'
        )
        
        res = self.__http_get(url).json()

        # 如果获取完毕就返回一个False
        if not res['body']['users']:
            return False
        # 否则返回当前页获取的ID列表
        return [index['userId'] for index in res['body']['users']]

    # 获取自己关注的所有作者的ID
    def get_all_followed_artists_uids(self, offset :int = 24):
        results = []
        for page in range(0, int(offset * 1e6)):
            result = self.get_followed_artist_uids_by_page(page, offset)
            if not result:
                break
            results += result
        return results

    # 多线程获取指定作者的所有作品中的所有图像的链接
    # 这个方法如果改为单线程，那么速度堪忧并且没法兼容多线程下载图像
    def get_artist_artwork_image_links(self, artistID :str | int):
        artworks = [*self.__http_get(f'https://www.pixiv.net/ajax/user/{artistID}/profile/all'
            f'?lang=zh').json()['body']['illusts'].keys()]

        self.links = []
        def get_images(thID :int, artworks :list[str]):
            for pid in range(thID, len(artworks), self.maxNumberThreads):
                print(f'Thread[{thID:02x}] obtains the image link in PID[{artworks[pid]}].')
                dynamicImageUrl = f'https://www.pixiv.net/ajax/illust/{artworks[pid]}/ugoira_meta?lang=zh'
                staticImageUrl = f'https://www.pixiv.net/ajax/illust/{artworks[pid]}/pages?lang=zh'

                dynamicImage_result = self.__http_get(dynamicImageUrl).json()
                statucImage_result = self.__http_get(staticImageUrl).json()

                if not dynamicImage_result['error']:
                    self.links.append(dynamicImage_result['body']['originalSrc'])
                else:
                    for index in statucImage_result['body']:
                        self.links.append(index['urls']['original'])

        self.__threads(get_images, artworks)

        return self.links

    # 用于单独获取指定作品页面中的所有图像的下载链接（后续考虑是否转为多线程）
    def get_artworks_illust_image_links(self, artworksID :int):
        static_images_url = f'https://www.pixiv.net/ajax/illust/{artworksID}/pages?lang=zh'
        dynamic_images_url = f'https://www.pixiv.net/ajax/illust/{artworksID}/ugoira_meta?lang=zh'
        results_link = []

        static_images_response = self.__http_get(static_images_url).json()
        dynamic_images_response = self.__http_get(dynamic_images_url).json()

        fwrite_json('static_images_response.json', static_images_response)
        fwrite_json('dynamic_images_response.json', dynamic_images_response)

        # 如果是静态图
        if (static_images_response['error'] == False) and (dynamic_images_response['error'] == True):
            for item in static_images_response['body']:
                original_url = item['urls']['original']
                results_link.append(original_url)
        # 如果是动态图
        elif dynamic_images_response['error'] == False:
            results_link.append(dynamic_images_response['body']['originalSrc'])

        return results_link

    # 下载单个作品（提供重连机制）
    def download(self, url :str, zipToMp4 :bool = False, ReSpecifyPath :str = None, retry_count :int = 5):
        # 如果用户指定了新的保存路径就使用新的路径以覆盖类中的save_path
        if ReSpecifyPath:
            self.save_path = ReSpecifyPath

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        fileSavePath = os.path.join(self.save_path, self.__create_filename(url))

        if os.path.exists(fileSavePath) or os.path.exists(fileSavePath.replace('zip', 'mp4')):
            return self.STATUS_EXISTS

        while True:
            try:
                response = self.__http_get(url)
                break
            except:
                if not retry_count:
                    return self.STATUS_FAILED
                retry_count -= 1

        if response.headers['Content-Type'] == 'application/zip':
            if zipToMp4:
                self.__zip_to_mp4(url, fileSavePath, response.content, self.save_path)
            else:
                fwrite(fileSavePath, data = response.content)
        else:
            fwrite(fileSavePath, data = response.content)

        return self.STATUS_DONE

    # 多线程下载指定作者的所有作品
    def multi_threaded_download(self, artistID :str | int, ReSpecifyPath :str = None):
        def _download(thID :int, links :list[str]):
            for index in range(thID, len(links), self.maxNumberThreads):
                
                status = self.download(links[index], zipToMp4 = True, ReSpecifyPath = ReSpecifyPath)
                
                # '''
                fn = self.__create_filename(links[index])
                print(f'Thread[{thID:02x}] download \'{fn}\'')
                if status == self.STATUS_EXISTS:
                    print(f'Thread[{thID:02x}] download \'{fn}\', Exists.')
                elif status == self.STATUS_FAILED:
                    print(f'Thread[{thID:02x}] download \'{fn}\', Failed.')
                # '''
        self.__threads(_download, self.get_artist_artwork_image_links(artistID))
