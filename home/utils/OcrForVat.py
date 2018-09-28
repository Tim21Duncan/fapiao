import xmlToDict
import cv2
import Detect
import FindCircle
import matplotlib.pyplot as pl
import muban
import fp
import flow
import lineToAttribute.getAtbt
import copy
import muban


def mubanDetect(filepath):
    # 预留
    midProcessResult = [None, None]
    midProcessResult[0] = filepath
    midProcessResult[1] = 11
    # vat发票专票
    VATInvoiceTemplet = {
    }

    dic = xmlToDict.XmlTodict('VATInvoiceSimpleMuban.xml')

    # tplt = [dic['QRCode'][0], dic['QRCode'][1], dic['figureX'][0] + dic['figureX'][2] / 2, dic['figureX'][1] + dic['figureX'][3] / 2]
    tplt = [dic['figureX'][0] + dic['figureX'][2] / 2, dic['figureX'][1] + dic['figureX'][3] / 2]
    # print(tplt)
    '''
    for c in tplt:
        if c == None:
            print('Templet VATInvoice error')
    '''
    TemType = {}
    if midProcessResult[1] == 11:  # 增值税专用
        for item in dic:
            if item != 'QRCode' and item != 'figureX':
                # print(item)
                # tmp = MakeFileInV([[int(dic.get(item)[0]), int(dic.get(item)[1])], [int(dic.get(item)[2]), int(dic.get(item)[3])]], box, symbol, filePath, item, tplt)
                VATInvoiceTemplet[item] = [int(dic.get(item)[0]), int(dic.get(item)[1]), int(dic.get(item)[2]),
                                           int(dic.get(item)[3])]
        TemType = VATInvoiceTemplet

    fcv = cv2.imread(filepath, 1)
    # print(fcv)
    try:
        w1 = fcv.shape
    except:
        print("picture is None")

    if w1[0] + w1[1] > 1500:
        rate = 0.5
        print("rate : 0.5")

    if midProcessResult[1] == 11:
        # box = Detect.detect(cv2.imread(midProcessResult[0]), rate)
        figureP = FindCircle.findSymbol(filepath)
        # StBox = sortBox(box)
        # print(box)
        # print(figureP)
        # print(StBox)
        Templet = simplyAdjust(TemType, [figureP[0], figureP[1]], tplt, w1)  # 增值税专票

    '''
    im = cv2.imread(filepath, 0)
    rec = []
    for c in TemType:
        rec.append(TemType[c])
    vis_textline0 = fp.util.visualize.rects(im, rec)
    # vis_textline1 = fp.util.visualize.rects(im, rects, types)
    # 显示
    pl.figure(figsize=(15, 10))
    pl.subplot(2, 2, 1)
    pl.imshow(im, 'gray')

    pl.subplot(2, 2, 2)
    pl.imshow(vis_textline0)
    pl.show()
    '''

    attributeLine = lineToAttribute.getAtbt.compute(textline(midProcessResult[0]), Templet)

    # print(attributeLine)
    # print(type(attributeLine))
    # print(attributeLine['departCity'])
    jsonResult = flow.cropToOcr(midProcessResult[0], attributeLine, midProcessResult[1])  # ocr和分词
    print(jsonResult)
    return jsonResult


def textline(filepath):
    show_textline = False
    # --- 初始化 ---
    # 读取文件夹下图片
    # dset_dir = 'E:/DevelopT/pycharm_workspace/Ocr/pic'
    # jpgs = fp.util.path.files_in_dir(dset_dir, '.jpg')
    # jpgs = filepath
    # fp.util.path.files_in_dir(filepath)
    # 创建 字符行检测器 （检测结果为：若干可能为字符行的矩形框）

    thresh_pars = dict(mix_ratio=0.1, rows=1, cols=3, ksize=11, c=9)
    train_ticket_pars = dict(thresh_pars=thresh_pars, char_expand_ratio=0.4)
    detect_textlines = fp.frame.textline.Detect(pars=train_ticket_pars, debug=True)
    # 创建 字符行分类器 （分类结果为：印刷字符、针式打印字符等）
    # classify_textlines = fp.frame.textline.Classify()
    # print(jpgs[0])
    # 读第一个图片
    im = cv2.imread(filepath, 0)
    # 检测字符行，并分类
    rects = detect_textlines(im)

    if show_textline:
        # 绘制结果
        vis_textline0 = fp.util.visualize.rects(im, rects)
        # vis_textline1 = fp.util.visualize.rects(im, rects, types)
        # 显示
        pl.figure(figsize=(15, 10))
        pl.subplot(2, 2, 1)
        pl.imshow(im, 'gray')

        pl.subplot(2, 2, 2)
        pl.imshow(vis_textline0)
        pl.show()

    return rects


def adjustToTextLine(mubandict, box, typeT, templet):  # box顺序需要调整

    if typeT != 11:
        midbox = sortBox(box)
    else:
        midbox = box
    # print(midbox)

    mubanBox = []
    if typeT == 1:
        mubanBox = [526, 272, 634, 379]  # [x1,y1,x2,y2]
    if typeT == 2:
        # mubanBox = [483, 259, 632, 439]
        # mubanBox = [365, 234, 425, 297]#[[365, 297], [365, 234], [425, 234], [425, 297]]
        # [[601, 409], [507, 408], [508, 318], [602, 319]]
        mubanBox = [508, 318, 601, 409]  # use TR009.JPG
    if typeT == 11:
        mubanBox = templet

    w = midbox[2] - midbox[0]
    h = midbox[3] - midbox[1]

    for x in mubandict:
        tempArray = copy.deepcopy(mubandict[x])
        mubandict[x][0] = midbox[2] - (int)((mubanBox[2] - tempArray[0]) / (mubanBox[2] - mubanBox[0]) * w)
        mubandict[x][1] = midbox[3] - (int)((mubanBox[3] - tempArray[1]) / (mubanBox[3] - mubanBox[1]) * h)
        mubandict[x][2] = tempArray[2] / (mubanBox[2] - mubanBox[0]) * w
        mubandict[x][3] = tempArray[3] / (mubanBox[3] - mubanBox[1]) * h

        if mubandict[x][0] < 0:
            mubandict[x][0] = 0
        if mubandict[x][1] < 0:
            mubandict[x][1] = 0

    print(mubandict)

    if typeT == 1:
        # 调整蓝票框
        mubandict = muban.de_muban(mubandict, 0.8)
    if typeT == 11:
        mubandict = muban.de_muban(mubandict, 0.9)

    return mubandict


def simplyAdjust(mubandict, box, tplt, shape):
    for x in mubandict:
        mubandict[x][0] = mubandict[x][0] + box[0] - tplt[0]
        mubandict[x][1] = mubandict[x][1] + box[1] - tplt[1]
    if mubandict[x][0] < 0:
        mubandict[x][0] = 0
    if mubandict[x][1] < 0:
        mubandict[x][1] = 0
    if mubandict[x][0] + mubandict[x][2] > shape[1]:
        mubandict[x][0] = shape[1] - mubandict[x][2]
    if mubandict[x][1] + mubandict[x][3] > shape[0]:
        mubandict[x][1] = shape[0] - mubandict[x][3]
    print(mubandict)

    mubandict = muban.de_muban(mubandict, 1.1)
    return mubandict


def sortBox(box):
    # box[[536, 387], [534, 280], [641, 279], [643, 386]]
    a = []
    b = []
    for x in box:
        a.append(x[0])
        b.append(x[1])

    return [min(a), min(b), max(a), max(b)]


def init(filepath):
    '''
    mage = cv2.imread(filepath,0)
    str_info, position = recog_qrcode(image, roi=None)

    #二维码无法识别
    if str_info == None:
    '''
    mubanDetect(filepath)
    '''
    else:
        js = InterfaceType.JsonInterface.invoice()
        js.setInfo(str_info)
        jsoni = js.dic

        return json.dumps(jsoni).encode().decode("unicode-escape")
    '''


'''dset_dir = 'E:/DevelopT/pycharm_workspace/Ocr/Image'
jpgs = fp.util.path.files_in_dir(dset_dir, '.png')
print(jpgs[9])
'''
# init('Image_00178.jpg')