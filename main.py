# coding=UTF-8

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import os
import numpy as np
import cv2
import json

# 用意したGUI設定用ファイル
import designer


""" opencv用クラス """
class opencv():

	def __init__(self, parent=None):
		super(opencv, self).__init__()
		# キャプチャー開始
		self.cap = cv2.VideoCapture(0)

		#カメラの解像度を設定
		self.cap.set(3, 640)  # Width
		self.cap.set(4, 370)   # Height
		self.cap.set(5, 15)   # FPS

		# 背景画像を用意
		self.backgroundIMGsave()

		# 受けっとったデータ数のカウント
		self.countjson = len(jsonData)
		# 結果を入力するためのリスト作成
		self.AreaCalum = {}
		for self.x in range(self.countjson):
			self.AreaCalum[str(self.x)] = np.zeros(10)
		# ループ回数をカウント
		self.countloop = 0

	""" 背景画像を保存する """
	def backgroundIMGsave(self):
		# 画像をキャプチャーする
		ret, self.frame = self.cap.read()
		# RGBからgray画像に変換
		self.frame_gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
		# jpgファイルとして画像を保存
		cv2.imwrite('bg.jpg',self.frame_gray)


	""" メインプログラム """
	def capStart(self):
		# カメラから画像を取得し変換する
		self.img_caputure()
		# 受け取った条件分
		for self.x in range(self.countjson):
			# 受け取ったHSV情報を整理
			self.formatingHSV()
			# 画像処理
			self.img_diff()
			self.color_picup()
			# 抽出されたラベルをカウントし代入
			self.ret = self.AreaCal()
			# capstart()の呼ばれた回数によって分岐
			if self.countloop < 10:
				# リストに個数を代入
				self.AreaCalum[str(self.x)][self.countloop] = self.ret
			else :
				# リストから古い要素を削除し、末尾に追加
				self.AreaCalum[str(self.x)] =  np.delete(self.AreaCalum[str(self.x)],0)
				self.AreaCalum[str(self.x)] =  np.append(self.AreaCalum[str(self.x)],int(self.ret))
		# カウントを進める
		self.countloop += 1

		# 画像を保存
		cv2.imwrite('nw.jpg',self.frame)

		""" 結果を整理して返す """
		# 結果を整理する空のリストを作成
		self.result = np.zeros(self.countjson)
		# 条件の個数ループ
		for self.x in range(self.countjson):
			# リストに保存されている10個の要素の平均をとり四捨五入->返り値を整数に丸める
			self.result[self.x] = int(np.round(self.AreaCalum[str(self.x)].mean()))
		# 結果を返す
		if int(self.countjson) == 1:
			return str(self.result[0])
		elif int(self.countjson) == 2:
			return str(self.result[0]) + "," + str(self.result[1])
		else:
			return str(self.result[0]) + "," + str(self.result[1]) + "," + str(self.result[2])

	""" カメラから画像をキャプチャーし変換する """
	def img_caputure(self):
		# キャプチャー開始
		ret, self.frame = self.cap.read()
		# gray画像に変換
		self.frame_gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
		# HSV画像に変換
		self.frame_hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

	""" 差分画像の生成 """
	def img_diff(self):
		# 背景画像読み込み
		self.im_bg   = cv2.imread("bg.jpg",0)
		# 差分計算
		self.diff    = cv2.absdiff(self.frame_gray,self.im_bg)
		# 背景画像と同じ高さ・幅の画像生成
		self.hight   = self.im_bg.shape[0]
		self.width   = self.im_bg.shape[1]
		self.im_mask = np.zeros((self.hight,self.width),np.uint8)
		# 差分が閾値よりひくければTrue
		self.mask    = self.diff < jsonData[str(self.x)]["th"]
		# 背景部分を黒で描写
		self.im_mask[self.mask] = 255
		self.im_mask = 255 - self.im_mask
		# ゴマ塩ノイズ除去
		self.im_mask = cv2.medianBlur(self.im_mask,jsonData[str(self.x)]["blur"])

	""" 色抽出した画像の生成 """
	def color_picup(self):
		# 背景と差分のある領域のみを指定
		self.img_diff_mask = cv2.bitwise_and(self.frame_hsv,self.frame_hsv,mask = self.im_mask)
		# 色の範囲内のpxを探す
		self.img_picolo = cv2.inRange(self.img_diff_mask, self.low, self.up)
		# HITした領域を抽出
		self.img_diff_mask = cv2.bitwise_and(self.frame_hsv,self.frame_hsv,mask = self.img_picolo)
		# ゴマ塩ノイズ除去
		self.img_diff_mask = cv2.medianBlur(self.img_diff_mask,jsonData[str(self.x)]["blur"])

	""" 抽出された画像からカウントする """
	def AreaCal(self):
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
			if self.data[self.y,4] > 30:
				if self.area_max < self.data[self.y,4]:
					self.area_max = self.data[self.y,4]
				self.d_list.append( self.y )

		for self.y in self.d_list:
			cv2.circle(self.frame,(int(self.center[self.y][0]),int(self.center[self.y][1])), 10,(255, 0, 0), 2)


		# カウントした総数を返す
		return len(self.d_list)

	""" ループ回数をリセットする """
	def countreset(self):
		self.countloop = 0

	""" 受けっとたjsonデータを整理する """
	def formatingHSV(self):
		# jsonデータから値を受け取る
		self.up_H = int(jsonData[str(self.x)]["up"]["H"])
		self.up_S = int(jsonData[str(self.x)]["up"]["S"])
		self.up_V = int(jsonData[str(self.x)]["up"]["V"])

		self.low_H = int(jsonData[str(self.x)]["low"]["H"])
		self.low_S = int(jsonData[str(self.x)]["low"]["S"])
		self.low_V = int(jsonData[str(self.x)]["low"]["V"])

		# 受け取った値をリストに保存
		self.up  = np.array([self.up_H, self.up_S, self.up_V])
		self.low = np.array([self.low_H, self.low_S, self.low_V])

""" ウィンドウ用クラス """
class MyForm(QMainWindow):

	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		# PyQtで生成したGUIの読み込み
		self.ui = designer.Ui_MainWindow()
		self.ui.setupUi(self)

		# ボタンにイベントを設定
		self.ui.StartButton.setCheckable(True)
		self.ui.StartButton.toggled.connect(self.PushBttonSt)

		# タイマーに必要な変数を宣言
		self.timeCount = 0
		self.time = 0
		self.repeatTime = 1

		# Qtimerを用いるための宣言
		self.timer = QTimer(self.ui.caputureImg)
		self.timer.timeout.connect( self.TimerEvent )

		# 変数の宣言
		self.savecount = 1

	""" 値を外部ファイルに保存する """
	def save(self):
		# 質問文を読み込み
		self.linetext = self.ui.Question.text()
		# 質問文が変更されているか判定
		if self.linetext == "input Quetion":
			# 出力するテキストを作成
			self.savetext = "Q."+str(self.savecount)+"\n"+str(self.per)+"\n"
		# 質問文が更新されているか判定
		elif self.linetext == self.linetextOld:
			self.savetext = "Q."+str(self.savecount)+"\n"+str(self.per)+"\n"
		else:
			self.savetext = "Q."+str(self.savecount)+" "+str(self.linetextint)+"\n"+str(self.per)+"\n"
			# 質問文を保存
			self.linetextOld = str(self.linetext)
		# ファイルを開く
		f =  open("reslt.csv","a")
		# 結果を出力
		f.write(self.savetext)
		# ファイルを閉じる
		f.close()

	""" タイマーで呼び出される処理 """
	def TimerEvent(self):

		# カウントを進める
		self.timeCount += 1
		# カウントが割り切れるか判定
		if self.timeCount % 3 == 0 :
			# 現在のカウントを代入
			self.timeStr = str(int(self.timeCount/3))
			# ウィンドウにカウントを表示する
			self.ui.timer.setText(self.timeStr)

		# opencvのcaptureを呼び出し返り値を得る
		self.per = opencv.capStart()
		# 文字列としてあつかう
		self.per = str(self.per)
		# ウィンドウに結果を表示する
		self.ui.result.setText(self.per)

		# 画像をフレームにセット
		self.ViewImgSet()

	""" ボタンがクリックされたときの処理 """
	def PushBttonSt(self, checked):
		# ボタンがチェックされたとき
		if checked:
			# ボタンのテキストを書き換える
			self.ui.StartButton.setText('Stop')
			# 各タイマーに使用する変数、および表示を初期化
			self.timeCount = 0
			self.time = 0
			opencv.countreset()
			self.ui.timer.setText(str(self.timeCount))
			# repeatTimeで設定された値毎に関数を呼び出す
			self.timer.start(self.repeatTime)
		# ボタンのチェックが外れた時
		else:
			# ボタンのテキストを書き換える
			self.ui.StartButton.setText('Start')
			# タイマーをストップする
			self.timer.stop()
			# save関数を呼び出す
			self.save()

	""" 画像をフレームに設置する """
	def ViewImgSet(self):
		self.pixmap = QPixmap()
		self.pixmap.load("nw.jpg")
		self.scene = QGraphicsScene(self)
		self.item = QGraphicsPixmapItem(self.pixmap)
		self.scene.addItem(self.item)
		self.ui.caputureImg.setScene(self.scene)


if __name__ == "__main__":

	# jsonファイルの読み込み
	f =  open("setValue.json","r")
	jsonData = json.load(f)
	f.close()

	opencv = opencv()

	app = QApplication(sys.argv)
	myapp = MyForm()
	myapp.show()
	sys.exit(app.exec_())