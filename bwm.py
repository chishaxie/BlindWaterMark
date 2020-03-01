#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import random

cmd = None
debug = False
seed = 20160930
alpha = 3.0

if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) < 2:
        print 'Usage: python bwm.py <cmd> [arg...] [opts...]'
        print '  cmds:'
        print '    encode <image> <watermark> <image(encoded)>'
        print '           image + watermark -> image(encoded)'
        print '    decode <image> <image(encoded)> <watermark>'
        print '           image + image(encoded) -> watermark'
        print '  opts:'
        print '    --debug,          Show debug'
        print '    --seed <int>,     Manual setting random seed (default is 20160930)'
        print '    --alpha <float>,  Manual setting alpha (default is 3.0)'
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd != 'encode' and cmd != 'decode':
        print 'Wrong cmd %s' % cmd
        sys.exit(1)
    if '--debug' in sys.argv:
        debug = True
        del sys.argv[sys.argv.index('--debug')]
    if '--seed' in sys.argv:
        p = sys.argv.index('--seed')
        if len(sys.argv) <= p+1:
            print 'Missing <int> for --seed'
            sys.exit(1)
        seed = int(sys.argv[p+1])
        del sys.argv[p+1]
        del sys.argv[p]
    if '--alpha' in sys.argv:
        p = sys.argv.index('--alpha')
        if len(sys.argv) <= p+1:
            print 'Missing <float> for --alpha'
            sys.exit(1)
        alpha = float(sys.argv[p+1])
        del sys.argv[p+1]
        del sys.argv[p]

import cv2
import numpy as np
import matplotlib.pyplot as plt

# OpenCV是以(BGR)的顺序存储图像数据的
# 而Matplotlib是以(RGB)的顺序显示图像的
def bgr_to_rgb(img):
    b, g, r = cv2.split(img)
    return cv2.merge([r, g, b])

def getImgAndWm(image, watermark):
    img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    if len(cv2.split(img)) < 4:
        img = cv2.imread(image)
        wm = cv2.imread(watermark)
    else:
        wm = cv2.imread(watermark, cv2.IMREAD_UNCHANGED)

    return img, wm

def encode(image, watermark):
    print 'image<%s> + watermark<%s>' % (image, watermark)
    img, wm = getImgAndWm(image, watermark)

    if debug:
        plt.subplot(231), plt.imshow(bgr_to_rgb(img)), plt.title('image')
        plt.xticks([]), plt.yticks([])
        plt.subplot(234), plt.imshow(bgr_to_rgb(wm)), plt.title('watermark')
        plt.xticks([]), plt.yticks([])

    # print img.shape # 高, 宽, 通道
    h, w = img.shape[0], img.shape[1]
    hwm = np.zeros((int(h * 0.5), w, img.shape[2]))
    if hwm.shape[0] < wm.shape[0]:
        return
    if hwm.shape[1] < wm.shape[1]:
        return

    hwm2 = np.copy(hwm)
    for i in xrange(wm.shape[0]):
        for j in xrange(wm.shape[1]):
            hwm2[i][j] = wm[i][j]

    random.seed(seed)
    m, n = range(hwm.shape[0]), range(hwm.shape[1])
    random.shuffle(m)
    random.shuffle(n)
    for i in xrange(hwm.shape[0]):
        for j in xrange(hwm.shape[1]):
            hwm[i][j] = hwm2[m[i]][n[j]]

    rwm = np.zeros(img.shape)
    for i in xrange(hwm.shape[0]):
        for j in xrange(hwm.shape[1]):
            rwm[i][j] = hwm[i][j]
            rwm[rwm.shape[0] - i - 1][rwm.shape[1] - j - 1] = hwm[i][j]

    if debug:
        plt.subplot(235), plt.imshow(bgr_to_rgb(rwm)), \
            plt.title('encrypted(watermark)')
        plt.xticks([]), plt.yticks([])

    f1 = np.fft.fft2(img)
    f2 = f1 + alpha * rwm
    _img = np.fft.ifft2(f2)

    if debug:
        plt.subplot(232), plt.imshow(bgr_to_rgb(np.real(f1))), \
            plt.title('fft(image)')
        plt.xticks([]), plt.yticks([])

    img_wm = np.real(_img)
    assert cv2.imwrite(image, img_wm, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

if cmd == 'encode':
    watermark = sys.argv[2]
    for x in range(3, len(sys.argv)):
        image =  sys.argv[x]
        encode(image, watermark)

elif cmd == 'decode':
    fn1 = sys.argv[2]
    fn2 = sys.argv[3]
    fn3 = sys.argv[4]

    print 'image<%s> + image(encoded)<%s> -> watermark<%s>' % (fn1, fn2, fn3)
    img = cv2.imread(fn1)
    img_wm = cv2.imread(fn2)

    if debug:
        plt.subplot(231), plt.imshow(bgr_to_rgb(img)), plt.title('image')
        plt.xticks([]), plt.yticks([])
        plt.subplot(234), plt.imshow(bgr_to_rgb(img_wm)), plt.title('image(encoded)')
        plt.xticks([]), plt.yticks([])

    random.seed(seed)
    m, n = range(int(img.shape[0] * 0.5)), range(img.shape[1])
    random.shuffle(m)
    random.shuffle(n)

    f1 = np.fft.fft2(img)
    f2 = np.fft.fft2(img_wm)

    if debug:
        plt.subplot(232), plt.imshow(bgr_to_rgb(np.real(f1))), \
            plt.title('fft(image)')
        plt.xticks([]), plt.yticks([])
        plt.subplot(235), plt.imshow(bgr_to_rgb(np.real(f1))), \
            plt.title('fft(image(encoded))')
        plt.xticks([]), plt.yticks([])

    rwm = (f2 - f1) / alpha
    rwm = np.real(rwm)

    if debug:
        plt.subplot(233), plt.imshow(bgr_to_rgb(rwm)), \
            plt.title('encrypted(watermark)')
        plt.xticks([]), plt.yticks([])

    wm = np.zeros(rwm.shape)
    for i in xrange(int(rwm.shape[0] * 0.5)):
        for j in xrange(rwm.shape[1]):
            wm[m[i]][n[j]] = np.uint8(rwm[i][j])
    for i in xrange(int(rwm.shape[0] * 0.5)):
        for j in xrange(rwm.shape[1]):
            wm[rwm.shape[0] - i - 1][rwm.shape[1] - j - 1] = wm[i][j]
    assert cv2.imwrite(fn3, wm)

    if debug:
        plt.subplot(236), plt.imshow(bgr_to_rgb(wm)), plt.title(u'watermark')
        plt.xticks([]), plt.yticks([])

    if debug:
        plt.show()
