#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import sys
import requests
import re
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QInputDialog, QMessageBox,QFileDialog
from .album import album
from .fileutil import get_file_realpath,check_and_create_dir


class kd163PhotoDownloader(QWidget):
    def __init__(self):
        super().__init__()
        loadUi(get_file_realpath("kd163PhotoDownloader.ui"), self)
        self.user_id = None
        self.album_thread = album()
        self.album_thread.show_status_signal.connect(self.add_show_info)

#     获取相册列表
    @pyqtSlot()
    def on_pb_query_list_clicked(self):
        blog_name = self.le_blog_name.text()
        self.create_dir(blog_name)

        self.album_thread.blog_name = self.le_blog_name.text()
        self.catelog_items = self.album_thread.query_list()
        self.lw_list.clear()
        for item in self.catelog_items:
            self.lw_list.addItem("{}({})".format(item["name"], item["count"]))

    # ~ 生成个人的备份目录
    def create_dir(self, blog_name):
        path = self.le_path.text()
        if path.rindex("/") + 1 != len(path):
            path += "/"
        self.backup_dir = path + blog_name + "的相册/"
        self.album_thread.backup_dir = self.backup_dir
        check_and_create_dir(self.backup_dir)

    def add_show_info(self, msg):
        self.tb_result.append(msg)
        self.tb_result.moveCursor(self.tb_result.textCursor().End)

    def get_user_id(self):
        if self.user_id is not None:
            pass
        else:
            print("开始查询用户id")
            r = requests.get("http://" + self.le_blog_name.text() + ".blog.163.com/")
            # ~ print("返回的结果:"+ r.text)
            pt_user_id = re.compile(r'(?<=userId:").+?(?=,userName)')
            user_id = pt_user_id.match(r.text)
            user_id = re.search("(?<=userId:).+?(?=,)", r.text).group()
            print("您的用户id是", user_id)
            self.add_show_info("您的用户id是" + user_id)
            self.user_id = user_id

    @pyqtSlot()
    def on_pb_download_list_clicked(self):
        blog_name = self.le_blog_name.text()
        self.create_dir(blog_name)

        text_list = self.lw_list.selectedItems()
        selected_albums = [i.text() for i in list(text_list)]
        if len(selected_albums) == 0:
            QMessageBox.information(self, "提示", "请先选择相册", QMessageBox.Yes)
            return

        self.add_show_info("开始下载相册:" + ",".join(selected_albums))
        # ~ 启动下载线程
        self.album_thread.selected_albums = selected_albums
        self.album_thread.start()

    @pyqtSlot()
    def on_pb_open_website_clicked(self):
        webbrowser.open_new_tab(
            "http://photo.163.com/{}".format(self.le_blog_name.text())
        )

    @pyqtSlot()
    def on_pb_save_path_clicked(self):
        filename = QFileDialog.getExistingDirectory(self,"选择保存位置",self.le_path.text())
        if filename:
            self.le_path.setText(filename)
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    win = kd163PhotoDownloader()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()