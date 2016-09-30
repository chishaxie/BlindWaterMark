# BlindWaterMark

盲水印 by python

### 文件说明

* bwm.py 程序文件
* hui.png 无水印的原图
* wm.png 水印图
* hui_with_wm.png 有盲水印的图
* wm_from_hui.png 反解出来的水印图

### Demo

合成盲水印图

    python bwm.py encode hui.png wm.png hui_with_wm.png

![image](https://github.com/chishaxie/BlindWaterMark/raw/master/hui.png)

+

![image](https://github.com/chishaxie/BlindWaterMark/raw/master/wm.png)

->

![image](https://github.com/chishaxie/BlindWaterMark/raw/master/hui_with_wm.png)

提取图中的盲水印 (需要原图)

    python bwm.py decode hui.png hui_with_wm.png wm_from_hui.png

![image](https://github.com/chishaxie/BlindWaterMark/raw/master/hui.png)

+

![image](https://github.com/chishaxie/BlindWaterMark/raw/master/hui_with_wm.png)

->

![image](https://github.com/chishaxie/BlindWaterMark/raw/master/wm_from_hui.png)

### Usage

    Usage: python bwm.py <cmd> [arg...] [opts...]
      cmds:
        encode <image> <watermark> <image(encoded)>
               image + watermark -> image(encoded)
        decode <image> <image(encoded)> <watermark>
               image + image(encoded) -> watermark
      opts:
        --debug,          Show debug
        --seed <int>,     Manual setting random seed (default is 20160930)
        --alpha <float>,  Manual setting alpha (default is 3.0)
