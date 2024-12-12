
MAX_RESOLUTION=8192

from typing import List
import torchvision

from .AlyVision import imagese
from alibabacloud_imageseg20191230.models import SegmentHairAdvanceRequest
from alibabacloud_tea_util.models import RuntimeOptions

import os
import datetime
import numpy as np
import folder_paths
import comfy.model_base
from pathlib import Path
from urllib.request import urlopen
from collections import defaultdict
from PIL.PngImagePlugin import PngInfo
from PIL import Image, ImageDraw, ImageFont
import nodes

from .utils import *

comfy_path = os.path.dirname(folder_paths.__file__)
custom_nodes_path = os.path.join(comfy_path, "custom_nodes")


class ALY_Seg_Hair:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {"required":
            {
                "image": ("IMAGE", {"default": "", "multiline": False})
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("image", "Width", "Height", "X", "Y")
    OUTPUT_NODE = True
    FUNCTION = "sample"
    CATEGORY = "CXH"

    def sample(self, image):
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        folder_path = os.path.join(custom_nodes_path, "Comfyui_ALY", "cache")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        cache_image = os.path.join(folder_path, f"{date_str}.png")

        # 零时缓存转换成阿里io.buff
        save_tensor_image(image, cache_image)

        imp1 = open(cache_image, 'rb')

        segment_hair_request = SegmentHairAdvanceRequest()
        segment_hair_request.image_urlobject = imp1

        runtime = RuntimeOptions()
        try:
            # 初始化Client
            client = imagese.create_client_json()
            response = client.segment_hair_advance(segment_hair_request, runtime)
            print(response.body)
            print(response.body.data.elements[0])
            image_url = response.body.data.elements[0].image_url
            width = response.body.data.elements[0].width
            height = response.body.data.elements[0].height
            X = response.body.data.elements[0].x
            Y = response.body.data.elements[0].y
        except Exception as error:
            # 获取整体报错信息
            print("==========错误 start===========")
            print(error)
            print("==========错误 end===========")

        img = io.BytesIO(urlopen(image_url).read())
        image2 = Image.open(img)
        source_img = pil2tensor(image2)
        return (source_img, width, height, X, Y)
