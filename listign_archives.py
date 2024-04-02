## Calculate scale from feature points

import argparse
import os
import sys
import cv2
import numpy as np

import base64
import io
import zipfile
import rarfile

output_file = os.path.join( "." , "output_image.jpg"  )

# Parameter 
IMG_QUALITY  = 40


def main(args):

    input_files_path = args.input_path
    output_file_name = args.output_file_name
    resize_ratio     = float(args.resize_ratio)
    jpeg_quality     = int(args.jpeg_quality)



    # Check Project path
    if not os.path.exists(input_files_path) :
        print("Not exists ",input_files_path)
        sys.exit(1)

    # ファイルリスト取得
    file_list = get_file_list_recursive( input_files_path )
    #DBG print("All File List :", file_list)

    # アーカイブファイルリスト取得
    archive_list = filter_archive_files( file_list )    # リストからアーカイブファイルのみ抽出
    #DBG print("Archive File List :", archive_list)

    # 下記3行は for if処理を一行で行うサンプルなので消さない
    ## sample modarchive_list = [ "_".join(path.split( os.path.sep ))  for path in archive_list ] # 区切り文字を_に変更
    ## sample modarchive_list = [s[1:] if s.startswith('.') else s for s in modarchive_list]      # 先頭がドットの場合削除
    ## sample modarchive_list = [s[1:] if s.startswith('_') else s for s in modarchive_list]      # 先頭が_の場合削除
    ## sample print("Mod Archive List", modarchive_list)


    image_list = []
    for file in archive_list:

        #フルファイルパスから 名前生成 
        rename = "_".join(file.split( os.path.sep))
        rename = rename.lstrip('.') if rename.startswith('.') else rename
        rename = rename.lstrip('_') if rename.startswith('_') else rename

        #DBG print( file )
        #DBG if zipfile.is_zipfile(file) :
        #DBG     print( " is Zip" )
        #DBG else :
        #DBG     print( " is Not" )

        if ( (file.endswith('.zip')) and  (zipfile.is_zipfile(file)) ) :
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zipfile_dir_list = zip_ref.namelist()                                         # アーカイブ内ファイルリスト取得
                zipfile_list = [path for path in zipfile_dir_list if not path.endswith('/') ] # ディレクトリのみの要素削除

                ## # 先頭のファイルを抽出
                file_in_zip = zipfile_list[0]
                #zip_ref.extract(file_to_extract, '抽出先のディレクトリのパス')
                #DBG print(file_in_zip , " を抽出しました")

                try:
                    with zip_ref.open(file_in_zip) as file:
                        data = file.read()  
                        arr = np.frombuffer(data, np.uint8)              # 読み込みデータ(バイナリ列)を numpyアレイに変換
                        img_np = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED) # OpenCVの画像フォーマットに変換
            
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality ]
                        resized_img = cv2.resize(img_np, None, fx=resize_ratio, fy=resize_ratio )     # リサイズ処理

                        success, jpg_data = cv2.imencode('.jpg', resized_img , encode_param) # OpenCV画像フォーマットからjpgバイナリに変換
                        if not success:
                            raise Exception("Failed to encode image to JPG format")

                        base64_jpg = base64.b64encode(jpg_data).decode('utf-8')  # jpgバイナリからbase64に変換

                        # base64形式のデータをファイルに保存しないで、表示または別の処理に使用する
                        #DBG print(type(base64_jpg))
                        ## DBGprint(base64_jpg)
                        #cv2.imwrite( output_file , resized_img)

                        list = [rename, base64_jpg]
                        image_list.append( list )
                except zipfile.BadZipFile as e:
                    print("Zip File [", file, "] is corrupt.... : ", e)
                except KeyError as e:
                    print("Not Found File.... : ", e)
                except Exception as e:
                    print("Unexpected Error.... : ", e)



    # ここで HTMLに出力 ファイル名と画像 をセットに出力する
    html = '<table style="border: 1px solid black; border-collapse: collapse;">'
    for  name, image in image_list:
        #html += f'<tr><td style="border: 1px solid black;"><img src="data:image/jpeg;base64,{image}" alt="{name}" width="100"></td><td style="border: 1px solid black;">{name}</td></tr>'
        html += f'<tr><td style="border: 1px solid black;"><img src="data:image/jpeg;base64,{image}" alt="{name}"></td><td style="border: 1px solid black;">{name}</td></tr>'
    html += '</table>'
    
    with open( output_file_name, 'w', encoding="utf-8") as file:
        file.write(html)


#######################################################################
### # zipファイルを読み込み
### with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
###     # アーカイブファイル内のファイルリストを取得
###     file_list = zip_ref.namelist()
###     print("アーカイブファイル内のファイルリスト:", file_list)
### 
###     # 特定のファイルを抽出
###     file_to_extract = 'example.txt'
###     zip_ref.extract(file_to_extract, '抽出先のディレクトリのパス')
###     print(f"{file_to_extract} を抽出しました")
### 


#######################################################################
### # rarファイルを読み込み
### with rarfile.RarFile(rar_file_path, 'r') as rar_ref:
###     # アーカイブファイル内のファイルリストを取得
###     file_list = rar_ref.namelist()
###     print("アーカイブファイル内のファイルリスト:", file_list)
### 
###     # 特定のファイルを抽出
###     file_to_extract = 'example.txt'
###     rar_ref.extract(file_to_extract, '抽出先のディレクトリ



## ============ argument パーサ
def parse_args():
    ''' parse args '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--input_path",
            required=True,
            help="Path to Input Files folder"
            )
    parser.add_argument(
            "--output_file_name",
            help="Path to Output HTML File Name",
            default="output.html"
            )
    parser.add_argument(
            "--resize_ratio",
            help="Image Resize Ratio 0.0 - 1.0",
            default=0.3
            )
    parser.add_argument(
            "--jpeg_quality",
            help="Jpeg Image Quality",
            default=40
            )
    args = parser.parse_args()
    return args


## ============ Float変換
def conv_float(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


## ============ ファイル再帰取得
def get_file_list_recursive(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

## ============ アーカイブファイルフィルタ
def filter_archive_files(file_list):
    archive_files = []
    for file in file_list:
        if file.endswith('.zip') or file.endswith('.rar'):
            archive_files.append(file)
    return archive_files



if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
