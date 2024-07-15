from PIL import Image
from os import mkdir
from os.path import exists

def checkDir(infile, saveDir, saveName):
    if not infile or not saveDir:
        exit(f'>>>> 图像路径: {infile}\n>>>> 保存目录: {saveDir}')
    if not exists(infile):
        exit(f'>>>> 图像路径不存在: {infile}')

    if not exists(saveDir):
        print(f'>>>> 目录{saveDir}不存在，将创建.')
        mkdir(saveDir)
    
    print(
        f'>>>> 导入文件: {infile}\n'
        f'>>>> 保存目录: {saveDir}\n'
        f'>>>> 保存名称: {saveName}'
    )

def dir_remake(saveDir):
    if saveDir[-1] == '/' or saveDir[-1] == '\\':
        return saveDir[:-1]
    return saveDir

def processImage(infile, saveDir, saveName):
    ''' Source: https://stackoverflow.com/questions/10269099/pil-convert-gif-frames-to-jpg '''
    saveDir = dir_remake(saveDir)
    checkDir(infile, saveDir, saveName)
    
    img = Image.open(infile)
    mypalette = img.getpalette()

    serialNumber = 1
    try:
        while True:
            print(f'\r>>>> [{serialNumber:>4}]', end='')
            try:
                img.putpalette(mypalette)
            except:
                pass
            new_im = Image.new("RGBA", img.size)
            new_im.paste(img)
            new_im.save(f'{saveDir}/{saveName}{serialNumber:0>4}.png')
            img.seek(img.tell() + 1)
            serialNumber += 1
    except EOFError:
        print(f'\n', end='')
        print(f'>>>> 导出完毕.')
        pass # end of sequence

if __name__ == "__main__":
    imgPath = './20220912120424.gif'
    saveDir = '1234'
    saveName = '___YS_BCSZ___'

    processImage(imgPath, saveDir, saveName)

    # Genshin Impact
    # Yae Miko


