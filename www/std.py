import logging
import os
import sys
sys.path.append(os.path.dirname(
    os.path.realpath(__file__)) + '\..\\')  # 添加到模块搜索路径中

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s]  %(message)s')
