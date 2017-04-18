# coding=UTF-8

import numpy as np
import cv2
import sys
import json
import csv

""" opencv用クラス """
class opencv():

	def __init__(self, parent=None):
		super(opencv, self).__init__()
		# キャプチャー開始
		self.cap = cv2.VideoCapture(0)

		#カメラの解像度を設定
		self.cap.set(3, 640)  # Width
		self.cap.set(4, 320)   # Height
		self.cap.set(5, 15)   # FPS

		# 背景画像を用意
		self.backgroundIMGsave()

		# 必要な変数を宣言
		self.clickcheck = False
		self.con = 0
		self.text = {}
		self.count = 0
		self.Val = {}
		self.text_val = {}

		self.font = cv2.FONT_HERSHEY_PLAIN
		self.font_size = 0.9
		self.length=20
		self.from_edge = 15

		self.area_list = []
		self.area_average = []
		self.setValue()

		self.save_con = 0


	""" 背景画像を保存する """
	def backgroundIMGsave(self):
		# 画像をキャプチャーする
		ret, self.frame = self.cap.read()
		# gray画像に変換 -> save
		self.frame_gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
		# jpgファイルとして画像を保存
		cv2.imwrite('bg.jpg',self.frame_gray)


	""" カメラをキャプチャーし処理を行う """
	def caputure(self):

		""" カメラから画像をキャプチャーし変換する """
		# キャプチャー開始
		ret, self.frame = self.cap.read()
		# gray画像に変換
		self.frame_gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
		# HSV画像に変換
		self.frame_hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

		""" 差分画像の生成 """
		# 背景画像読み込み
		self.im_bg   = cv2.imread("bg.jpg",0)
		# 差分計算
		self.diff    = cv2.absdiff(self.frame_gray,self.im_bg)
		# 背景画像と同じ高さ・幅の画像生成
		self.hight   = self.im_bg.shape[0]
		self.width   = self.im_bg.shape[1]
		self.im_mask = np.zeros((self.hight,self.width),np.uint8)
		# 差分が閾値よりひくければTrue
		self.mask    = self.diff < self.th
		# 背景部分は黒
		self.im_mask[self.mask] = 255
		self.im_mask = 255 - self.im_mask
		# ゴマ塩ノイズ除去
		self.im_mask = cv2.medianBlur(self.im_mask,self.blur)

		""" 色抽出した画像の生成 """
		# 背景と差分のある領域のみを指定
		self.img_diff_mask = cv2.bitwise_and(self.frame_hsv,self.frame_hsv,mask = self.im_mask)
		# 色の範囲内のpxを探す
		self.img_picolo = cv2.inRange(self.img_diff_mask, self.low, self.up)
		# HITした領域を抽出
		self.img_diff_mask = cv2.bitwise_and(self.frame_hsv,self.frame_hsv,mask = self.img_picolo)
		# ゴマ塩ノイズ除去
		self.img_diff_mask = cv2.medianBlur(self.img_diff_mask,self.blur)

		""" 抽出された画像からカウントする """
		# 色抽出を行い作成したマスクを二値画像に変換
		self.rgb = cv2.cvtColor(self.img_diff_mask, cv2.COLOR_HSV2BGR)
		self.gray = cv2.cvtColor(self.rgb, cv2.COLOR_BGR2GRAY)
		ret, self.bin = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
		# 白の連続したまとまりをカウントする
		self.label = cv2.connectedComponentsWithStats(self.bin)
		# 値の整理
		self.n = self.label[0] - 1
		self.data = np.delete(self.label[2], 0, 0)
		# center
		self.center = np.delete(self.label[3], 0, 0)
		# 結果を保存するためのリスト生成
		self.d_list = []
		self.area_max = 0
		# リストから面積がしきい値より大きいものをカウント
		for self.y in range(self.n):
			if self.data[self.y,4] > self.area_slider:
				if self.area_max < self.data[self.y,4]:
					self.area_max = self.data[self.y,4]
				self.d_list.append( self.y )

		for self.y in self.d_list:
			cv2.circle(self.frame,(int(self.center[self.y][0]),int(self.center[self.y][1])), 10,(255, 0, 0), 5)


		# カウントした総数を保存
		self.const =  len(self.d_list)

		# 結果を画像に書き込む処理を行う
		self.writeIMG()

	""" 画像へ出力と保存している条件の個数を書き込む """
	def writeIMG(self):
		cv2.putText(self.img_diff_mask,"HSV_up:"+str(self.up),(self.length,self.hight-self.length-self.from_edge-40),self.font, self.font_size,(255,255,0))
		cv2.putText(self.img_diff_mask,"HSV_low:"+str(self.low),(self.length,self.hight-self.length-self.from_edge-20),self.font, self.font_size,(255,255,0))
		# カウントされた個数を書き込む
		cv2.putText(self.img_diff_mask,"count:"+str(self.const),(self.length,self.hight-self.length-self.from_edge),self.font, self.font_size,(255,255,0))
		# 保存されている条件の個数を書き込む
		cv2.putText(self.img_diff_mask,"Area_max:"+str(self.area_max),(self.length,self.hight-self.length-self.from_edge+20),self.font, self.font_size,(255,255,0))

	""" スライダーの値を整理する関数 """
	def setValue(self):
		# スライダーから値を取得する
		self.area_slider = cv2.getTrackbarPos('Area','setting')
		self.th = cv2.getTrackbarPos('th','setting')
		self.blur = cv2.getTrackbarPos('blur','setting')
		# blurの値を奇数になるよう整理
		self.blur = 2 * self.blur + 3

		self.H_slider	= cv2.getTrackbarPos('H','setting')
		self.S_1_slider = cv2.getTrackbarPos('S_1','setting')
		self.V_1_slider = cv2.getTrackbarPos('V_1','setting')
		self.S_2_slider = cv2.getTrackbarPos('S_2','setting')
		self.V_2_slider = cv2.getTrackbarPos('V_2','setting')
		self.area_slider = cv2.getTrackbarPos('Area','setting')

		# スライダーの数値分減算する
		self.H_low = self.H_slider*15 - 15
		self.V_low = self.V_1_slider
		self.S_low = self.S_1_slider
		# 0以下になった場合0にする
		if self.H_low < 0:
			self.H_low = 0
		if self.S_low < 0:
			self.S_low = 0
		if self.V_low < 0:
			self.V_low = 0

		# スライダーの数値分加算する
		self.H_up = self.H_slider*15 +15
		self.V_up = self.V_2_slider
		self.S_up = self.S_2_slider

		# 255以上になった場合255にする
		if self.H_up > 180:
			self.H_up = 180
		if self.S_up > 255:
			self.S_up = 255
		if self.V_up > 255:
			self.V_up = 255

		# 整理した値からリストを作成する
		self.low = np.array([self.H_low,self.S_low,self.V_low])
		self.up  = np.array([self.H_up,self.S_up,self.V_up])


	""" 値を辞書型の変数に代入する """
	def saveValue(self):
		# 各パラメータを変数に代入する
		self.text[self.con] = {}
		self.text[self.con]["th"]   = int(self.th)
		self.text[self.con]["blur"] = int(self.blur)
		self.text[self.con]["low"]  = {}
		self.text[self.con]["low"]["H"]  = int(self.low[0])
		self.text[self.con]["low"]["S"]  = int(self.low[1])
		self.text[self.con]["low"]["V"]  = int(self.low[2])
		self.text[self.con]["up"]   = {}
		self.text[self.con]["up"]["H"]   = int(self.up[0])
		self.text[self.con]["up"]["S"]   = int(self.up[1])
		self.text[self.con]["up"]["V"]   = int(self.up[2])
		self.text[self.con]["area"]      = int(self.area_slider)

	def save(self):
		cv2.imwrite('now'+str(self.save_con)+'.jpg',self.frame)
		cv2.imwrite('mask'+str(self.save_con)+'.jpg',self.img_diff_mask)
		self.save_con += 1

# スライダーの変更を検出したときの関数
def changeSlider(val):
	opencv.setValue()

# switchスライダーの変更を検出した時の関数
def switchVal(val):
	opencv.save()

if __name__ == '__main__':

	# スライダーを「setting」ウィンドウに生成する
	cv2.namedWindow('setting')
	cv2.createTrackbar('th','setting',50,100,changeSlider)
	cv2.createTrackbar('blur','setting',0,10,changeSlider)
	cv2.createTrackbar('H','setting',1,12, changeSlider)
	cv2.createTrackbar('S_1','setting',50,250,changeSlider)
	cv2.createTrackbar('V_1','setting',50,250,changeSlider)
	cv2.createTrackbar('S_2','setting',200,250,changeSlider)
	cv2.createTrackbar('V_2','setting',200,250,changeSlider)
	cv2.createTrackbar('Area','setting',10,500,changeSlider)
	cv2.createTrackbar('switch','setting',0,1,switchVal)

	opencv = opencv()

	""" メインプログラム """
	# ループさせる
	while (True):
		opencv.caputure()
		# ウィンドウを表示する
		cv2.imshow('now', opencv.frame)
		cv2.imshow('mask', opencv.img_diff_mask)

		# KEY入力を受け付ける
		k = cv2.waitKey(1) & 0xFF
		# 押されたKEYが「Esc」の場合
		if k == 27:
			# 変数に中身が存在するか判定
			if len(opencv.text) != 0:
				# ファイルを書き込み用として開く
				f =  open("setValue.json","w")
				# 辞書型の変数をjsonとして書き出す
				json.dump(opencv.text, f, ensure_ascii=False)
				# 書き出された中身をコンソールに出力する
				print(opencv.text)
				# ファイルを閉じる
				f.close()
				# ループを終了
				break

	# キャプチャーを開放して終了
	opencv.cap.release()
	cv2.destroyAllWindows()