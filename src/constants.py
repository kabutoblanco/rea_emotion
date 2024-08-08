mesh_annotation = {
    "silhouette": [
        10,  338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
        397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
        172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109
    ],

    "lipsUpperOuter": [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291],
    "lipsLowerOuter": [146, 91, 181, 84, 17, 314, 405, 321, 375, 291],
    "lipsUpperInner": [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308],
    "lipsLowerInner": [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308],

    "rightEyeUpper0": [246, 161, 160, 159, 158, 157, 173],
    "rightEyeLower0": [33, 7, 163, 144, 145, 153, 154, 155, 133],
    "rightEyeUpper1": [247, 30, 29, 27, 28, 56, 190],
    "rightEyeLower1": [130, 25, 110, 24, 23, 22, 26, 112, 243],
    "rightEyeUpper2": [113, 225, 224, 223, 222, 221, 189],
    "rightEyeLower2": [226, 31, 228, 229, 230, 231, 232, 233, 244],
    "rightEyeLower3": [143, 111, 117, 118, 119, 120, 121, 128, 245],

    "rightEyebrowUpper": [156, 70, 63, 105, 66, 107, 55, 193],
    "rightEyebrowLower": [35, 124, 46, 53, 52, 65],

    "rightEyeIris": [473, 474, 475, 476, 477],

    "leftEyeUpper0": [398, 384, 385, 386, 387, 388, 466],
    "leftEyeLower0": [362, 382, 381, 380, 374, 373, 390, 249, 263],
    "leftEyeUpper1": [467, 260, 259, 257, 258, 286, 414],
    "leftEyeLower1": [359, 255, 339, 254, 253, 252, 256, 341, 463],
    "leftEyeUpper2": [342, 445, 444, 443, 442, 441, 413],
    "leftEyeLower2": [446, 261, 448, 449, 450, 451, 452, 453, 464],
    "leftEyeLower3": [372, 340, 346, 347, 348, 349, 350, 357, 465],

    "leftEyebrowUpper": [383, 300, 293, 334, 296, 336, 285, 417],
    "leftEyebrowLower": [265, 353, 276, 283, 282, 295],

    "leftEyeIris": [468, 469, 470, 471, 472],

    "rightEyeOut": [334, 450, 265, 465],
    "leftEyeOut": [105, 230, 35, 245],

    "midwayBetweenEyes": [168],

    "noseTip": [1],
    "noseBottom": [2],
    "noseRightCorner": [98],
    "noseLeftCorner": [327],

    "rightCheek": [205],
    "leftCheek": [425]
}

classes = ['ANGRY', 'DISGUST', 'FEAR', 'HAPPY', 'SAD', 'SURPRISE', 'NEUTRAL']
colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (255,0,50), (0,255,200)]

envs = {
    'B': { 'gain_range': (5,7), 'd_gain_range': (10,15), 'exposuretimerange': (5,10) },
    'B1': { 'gain_range': (7,10), 'd_gain_range': (10,15), 'exposuretimerange': (7,12) },
    'D': { 'gain_range': (5,5), 'd_gain_range': (6,6), 'exposuretimerange': (0.03,36) },
    'N': None,
}

def gstreamer_pipeline(
    capture_width=640,
    capture_height=360,
    display_width=640,
    display_height=360,
    framerate=60,
    flip_method=0,
    mode=None,
):
    extra = [capture_width,
             capture_height,
             framerate,
             flip_method,
             display_width,
             display_height]
    if mode:
        gain_range = *mode['gain_range'],
        d_gain_range = *mode['d_gain_range'],
        exposuretimerange = mode['exposuretimerange']
        exposuretimerange = (exposuretimerange[0] * 1e6, exposuretimerange[1] * 1e6)
        extra = [gain_range, d_gain_range, exposuretimerange, *extra]
        print(*extra)
    return ( 
        f"nvarguscamerasrc {'' if mode else '!'}"
        "wbmode=0 awblock=true gainrange=\"%s %s\" ispdigitalgainrange=\"%s %s\" exposuretimerange=\"%s %s\" aelock=true ! " if mode else ""
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv ! videobalance brightness=0 ! nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! " 
        "appsink drop=True"
        % (
            *extra,
        )
    )
