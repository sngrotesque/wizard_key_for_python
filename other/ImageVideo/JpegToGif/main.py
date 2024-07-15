import imageio.v2 as imageio
from os import walk

def jpg2gif(in_dir_path :str, out_path :str, Interval_time :float = 0.15):
    print(f'>>>> 正在载入jpg图片...')
    in_dir_path = in_dir_path.strip('/').strip('\\')
    imgPathList = walk(in_dir_path).__next__()[2]
    imgPathList = [x for x in imgPathList
        if x[-3:] == 'jpg' or x[-3:] == 'jpeg']
    imgPathList = [f'{in_dir_path}/{x}' for x in imgPathList]
    print(f'>>>> 已载入{len(imgPathList)}张jpg图片.')
    
    print(f'>>>> 将jpg图片列表组合为gif图片数据.')
    print(f'>>>> 图片之间间隔时间: {Interval_time:.2f}')
    gif_image = [imageio.imread(x) for x in imgPathList]
    
    print(f'>>>> 将gif图片数据保存至[{out_path:<12}].')
    imageio.mimwrite(out_path, gif_image, duration = Interval_time)
    print(f'>>>> 保存成功.')

if __name__ == "__main__":
    in_path  = './'
    out_path = 'test.gif'
    
    jpg2gif(in_path, out_path)
