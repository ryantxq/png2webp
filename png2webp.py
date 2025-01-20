import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QSlider, QFileDialog, QProgressBar, QScrollArea, QMessageBox
)
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QIcon
from PyQt5.QtCore import Qt, QRect
from PIL import Image
import os


class ImageConverterApp(QWidget):
    def __init__(self):
        """
        初始化主窗口类。
        """
        super().__init__()
        self.quality = 80  # 设置默认的图片转换质量为80
        self.selected_files = []  # 用于存储用户拖入的文件路径
        self.initUI()  # 调用初始化UI的方法

    def initUI(self):
        """
        初始化主窗口的UI布局。
        """
        self.setWindowTitle('PNG to WebP')  # 设置窗口标题
        self.resize(1600, 1000)  # 设置窗口大小
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.center()  # 调用方法将窗口居中
        self.setAcceptDrops(True)  # 启用窗口的拖放功能

        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), 'moonstone.jpg')
        self.setWindowIcon(QIcon(icon_path))

        # 创建主布局管理器
        layout = QVBoxLayout()

        # 创建滚动区域，用于显示图片
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # 确保滚动区域内的内容可以自适应大小
        layout.addWidget(self.scroll_area)

        # 默认提示标签，提示用户拖入图片
        self.drop_label = QLabel('拖入需要转换的图片', self)
        self.drop_label.setAlignment(Qt.AlignCenter)  # 设置标签内容居中
        self.drop_label.setStyleSheet("QLabel { background-color : lightgray; }")  # 设置标签背景颜色
        self.scroll_area.setWidget(self.drop_label)  # 将提示标签设置为滚动区域的初始内容

        # 文件数量标签布局
        file_count_layout = QHBoxLayout()
        file_count_layout.addStretch(1)  # 添加伸缩因子，使标签右对齐
        self.file_count_label = QLabel(f'已选择 0 张图片', self)  # 显示已选择的图片数量
        file_count_layout.addWidget(self.file_count_label)
        layout.addLayout(file_count_layout)

        # 控制布局（滑块、标签、按钮）
        control_layout = QHBoxLayout()
        self.slider = self.create_quality_slider()  # 创建质量滑块
        control_layout.addWidget(self.slider)
        self.slider_label = QLabel(f'质量：{self.quality}%', self)  # 显示当前质量值
        self.slider_label.setFixedWidth(200)  # 设置标签宽度
        control_layout.addWidget(self.slider_label)
        self.btn_convert = QPushButton('开始转换', self)  # 转换按钮
        self.btn_convert.setFixedWidth(150)  # 设置按钮宽度
        self.btn_convert.clicked.connect(self.convert_images)  # 绑定按钮点击事件
        control_layout.addWidget(self.btn_convert)
        layout.addLayout(control_layout)

        # 进度条
        self.progress_bar = self.create_progress_bar()  # 创建进度条
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)  # 将主布局设置为窗口的布局

    def center(self):
        """
        将窗口居中显示在屏幕上。
        """
        screen_rect = QApplication.desktop().screenGeometry()  # 获取屏幕尺寸
        screen_center = screen_rect.center()  # 计算屏幕中心点
        window_rect = self.frameGeometry()  # 获取窗口的几何形状
        window_rect.moveCenter(screen_center)  # 将窗口的中心点移动到屏幕中心点
        self.move(window_rect.topLeft())  # 更新窗口位置

    def create_quality_slider(self):
        """
        创建用于调整图片质量的滑块。
        """
        slider = QSlider(Qt.Horizontal, self)  # 创建水平滑块
        slider.setMinimum(10)  # 设置最低质量值
        slider.setMaximum(100)  # 设置最高质量值
        slider.setValue(self.quality)  # 设置默认质量值
        slider.valueChanged.connect(self.update_quality)  # 绑定值改变事件
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #d3d3d3;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #4d4d4d;
                width: 10px;
                margin: -4px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal:hover {
                background: rgb(36, 121, 206);
            }
            QSlider::handle:horizontal:pressed {
                background: rgb(20, 94, 139);
            }
        """)
        return slider

    def create_progress_bar(self):
        """
        创建进度条。
        """
        progress_bar = QProgressBar(self)  # 创建进度条
        progress_bar.setValue(0)  # 设置初始进度为0
        progress_bar.setFormat("%p%")  # 设置进度条显示格式
        progress_bar.setAlignment(Qt.AlignCenter)  # 设置进度条文本居中
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d3d3d3;
                border-radius: 2px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #62abff;
                width: 1px;
            }
        """)
        return progress_bar

    def update_quality(self, value):
        """
        更新图片质量值和滑块标签。
        """
        self.quality = value  # 更新质量值
        self.slider_label.setText(f'质量：{self.quality}%')  # 更新标签显示

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        处理拖入事件，检查拖入的内容是否为文件。
        """
        if event.mimeData().hasUrls():  # 检查是否包含文件路径
            event.accept()  # 接受拖入
        else:
            event.ignore()  # 忽略拖入

    def dropEvent(self, event: QDropEvent):
        """
        处理文件拖放事件。
        """
        files = [u.toLocalFile() for u in event.mimeData().urls()]  # 获取拖入的文件路径
        new_files = [f for f in files if f.endswith('.png') and f not in self.selected_files]  # 筛选PNG文件
        self.selected_files.extend(new_files)  # 将新文件添加到选中文件列表

        if self.selected_files:  # 如果有选中的文件
            self.build_grid_layout()  # 重新构建网格布局
            self.scroll_area.setWidget(self.grid_widget)  # 更新滚动区域的内容
            self.file_count_label.setText(f'已选择 {len(self.selected_files)} 张图片')  # 更新文件数量标签
            self.progress_bar.setValue(0)  # 重置进度条
            self.progress_bar.setFormat("%p%")  # 恢复进度条格式
        else:
            self.scroll_area.setWidget(self.drop_label)  # 如果没有选中的文件，恢复提示标签

    def build_grid_layout(self):
        """
        构建用于显示图片的网格布局。
        """
        self.grid_layout = QGridLayout()  # 创建网格布局
        self.grid_layout.setSpacing(5)  # 设置网格间距
        self.grid_widget = QWidget()  # 创建容器
        self.grid_widget.setLayout(self.grid_layout)

        max_width = (self.scroll_area.width() - 200) // 4  # 计算每张图片的最大宽度
        row, col = 0, 0  # 初始化行和列计数器
        for file_path in self.selected_files:  # 遍历选中的文件
            container = self.create_image_container(file_path, max_width)  # 创建图片容器
            self.grid_layout.addWidget(container, row, col)  # 将容器添加到网格布局
            col += 1
            if col > 3:  # 每行显示4张图片
                col = 0
                row += 1

        self.scroll_area.setWidget(self.grid_widget)  # 将网格布局设置到滚动区域

    def create_image_container(self, file_path, max_width):
        """
        创建包含图片和删除按钮的容器。
        """
        container = QWidget(self)  # 创建容器
        container_layout = QVBoxLayout()  # 创建垂直布局
        container_layout.setSpacing(0)  # 设置布局间距为0
        container.setLayout(container_layout)
        container.setStyleSheet("QWidget { border: 1px solid lightgray; padding: 2px; }")  # 设置容器样式

        label = QLabel(self)  # 创建图片标签
        label.setAlignment(Qt.AlignCenter)  # 设置图片居中
        pixmap = QPixmap(file_path)  # 加载图片
        thumbnail = pixmap.scaled(max_width, max_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # 缩放图片
        label.setPixmap(thumbnail)
        label.setStyleSheet("QLabel { border: none; }")  # 设置图片标签无边框

        remove_button = QPushButton('x', self)  # 创建删除按钮
        remove_button.setFixedSize(20, 20)  # 设置按钮大小
        remove_button.setStyleSheet("QPushButton { border: none; background-color: white; }")  # 设置按钮样式
        remove_button.clicked.connect(lambda checked, path=file_path, label=label, container=container:
                                      self.remove_image(path, label, container))  # 绑定删除事件

        button_layout = QHBoxLayout()  # 创建水平布局用于放置删除按钮
        button_layout.addStretch(1)  # 添加伸缩因子
        button_layout.addWidget(remove_button)

        container_layout.addWidget(label)  # 将图片标签添加到容器布局
        container_layout.addLayout(button_layout)  # 将按钮布局添加到容器布局
        return container

    def remove_image(self, file_path, label, container):
        """
        删除选中的图片。
        """
        if file_path in self.selected_files:  # 检查文件是否在选中列表中
            self.selected_files.remove(file_path)  # 从列表中移除文件
        label.deleteLater()  # 删除图片标签
        container.deleteLater()  # 删除容器
        self.build_grid_layout()  # 重新构建网格布局
        self.file_count_label.setText(f'已选择 {len(self.selected_files)} 张图片')  # 更新文件数量标签

    def convert_images(self):
        """
        转换选中的图片为WebP格式。
        """
        if not self.selected_files:  # 如果没有选中的文件
            self.progress_bar.setFormat("未选择图片")  # 更新进度条提示
            self.progress_bar.setValue(0)  # 重置进度条
            QMessageBox.warning(self, "警告", "未选择任何图片！")  # 弹出警告框
            return

        self.progress_bar.setValue(0)  # 重置进度条
        total_files = len(self.selected_files)  # 获取文件总数
        for idx, file_path in enumerate(self.selected_files):  # 遍历选中的文件
            try:
                image = Image.open(file_path)  # 使用Pillow打开图片
                webp_path = file_path.replace('.png', '.webp')  # 生成WebP文件路径
                image.save(webp_path, 'WEBP', quality=self.quality)  # 保存为WebP格式
                self.progress_bar.setValue(int((idx + 1) / total_files * 100))  # 更新进度条
            except Exception as e:  # 捕获异常
                self.progress_bar.setFormat(f"转换错误：{file_path}: {str(e)}")  # 更新进度条提示
                self.progress_bar.setValue(0)  # 重置进度条
                QMessageBox.critical(self, "错误", f"转换失败：{file_path}\n{str(e)}")  # 弹出错误框
                return

        self.progress_bar.setFormat("转换完成")  # 更新进度条提示
        self.progress_bar.setValue(100)  # 设置进度条为100%
        QMessageBox.information(self, "完成", "所有图片已成功转换！", QMessageBox.Ok)  # 弹出完成框

        # 清空选中文件列表并恢复初始状态
        self.selected_files = []
        self.file_count_label.setText(f'已选择 0 张图片')  # 更新文件数量标签

        # 重新创建提示标签并设置到滚动区域
        self.drop_label = QLabel('拖入需要转换的图片', self)
        self.drop_label.setAlignment(Qt.AlignCenter)  # 设置标签内容居中
        self.drop_label.setStyleSheet("QLabel { background-color : lightgray; }")  # 设置标签背景颜色
        self.scroll_area.setWidget(self.drop_label)  # 设置滚动区域的内容

        # 重置进度条
        self.progress_bar.setFormat("%p%")  # 清空进度条格式
        self.progress_bar.setValue(0)  # 重置进度条值


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建QApplication实例
    ex = ImageConverterApp()  # 创建主窗口实例
    ex.show()  # 显示主窗口
    sys.exit(app.exec_())  # 运行应用程序