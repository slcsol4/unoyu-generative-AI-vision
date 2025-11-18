# 以下を「app.py」に書き込み
import os
import streamlit as st
import pandas as pd
import urllib.request
import json
from io import BytesIO
import base64

from PIL import Image
from dotenv import load_dotenv

# .env ファイルから環境変数をロード
load_dotenv()

if "answer" not in st.session_state:
   st.session_state["answer"] = ""
if "encode_image" not in st.session_state:
   st.session_state["encode_image"] = ""
   
# 画像を縦横補正
def correct_image_orientation(img: Image.Image) -> Image.Image:
    
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        # Exif情報にOrientationタグ（0x0112）があれば処理
        if exif is not None and 0x0112 in exif:
            orientation = exif[0x0112]
            
            # Orientationの値に応じて画像を回転させる
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(-90, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    return img
    
    
# チャットボットとやりとりする関数
def communicate():
    data={"reference_image" : st.session_state["img1_base64"]
        ,"test_image" : st.session_state["img2_base64"]
        ,"system_message":str(st.session_state["user_input"])}
    body = str.encode(json.dumps(data))

    url = 'https://unoyu-mls-workspace-bdajz.japaneast.inference.ml.azure.com/score'
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    api_key = os.environ.get('UNOYU_GPT4_API_KEY')
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")


    headers = {'Content-Type':'application/json', 'Accept': 'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        st.session_state["answer"] = response.read().decode('unicode-escape')

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))


# ユーザーインターフェイスの構築
st.set_page_config(
    layout="wide", 
    initial_sidebar_state="auto")

# メインエリア
st.title(" ソリューション本部 画像不具合検知 お試し")

user_input = st.text_area("設定するプロンプトを入力してください。", key="user_input", value="あなたはプロの欠陥検出者です。あなたの仕事は、テスト画像と参照画像を比較することです。「欠陥なし検出」または「欠陥検出」と答えてください。また、あなたの決定をできる限り詳しく説明してください。背景を無視して、中央に表示されているオブジェクトだけを比較してください。日本語で答えてください。")

col1, col2 = st.columns(2)
with col1:
 file_path1 = st.file_uploader('検証対象の比較元となる画像をアップロードしてください', type=['png', 'jpg', 'jpeg'], key="img_up1")
 if file_path1:
     img1 = Image.open(file_path1)
     st.image(correct_image_orientation(img1))
     buffered = BytesIO()
     img1.save(buffered, format="jpeg")
     st.session_state["img1_base64"] = base64.b64encode(buffered.getvalue()).decode("utf-8")
with col2:
 file_path2 = st.file_uploader('検証対象の比較先となる画像をアップロードしてください', type=['png', 'jpg', 'jpeg'], key="img_up2")
 if file_path2:
     img2 = Image.open(file_path2)
     st.image(correct_image_orientation(img2))
     buffered2 = BytesIO()
     img2.save(buffered2, format="jpeg")
     st.session_state["img2_base64"] = base64.b64encode(buffered2.getvalue()).decode("utf-8")
st.button("Do Check!", on_click=communicate, use_container_width=True, type="primary")

if st.session_state["encode_image"]:
    st.text_area("aaaa", key="user_input_img1_base64",value=st.session_state["encode_image"])
    decoded_image = base64.b64decode(st.session_state["encode_image"])
    decoded_image = Image.open(BytesIO(decoded_image))
    st.image(decoded_image, caption="デコードされた画像")

if st.session_state["answer"]:
    answer = st.session_state["answer"]
    st.write(answer)
    
# サイドバー
st.sidebar.title("機能群")
prompt = st.sidebar.page_link("https://google.com", label="不具合検知", icon="🏠")
prompt = st.sidebar.page_link("https://google.com", label="忘れ物チェック", icon="🏠")
prompt = st.sidebar.page_link("https://google.com", label="レンタカーチェック", icon="🏠")
