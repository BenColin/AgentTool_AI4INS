from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By

# 创建 WebDriver 对象，指明使用chrome/edge/firefox浏览器驱动
wd = webdriver.Edge(service=Service(r'D:\edgedriver_win32\msedgedriver.exe'))

# 调用implicitly_wait(n:int)方法，设置隐式等待时间
'''后续所有的 find_element 或者 find_elements 之类的方法调用 都会采用策略：
如果立刻找不到元素， 每隔 半秒钟 再去界面上查看一次， 直到找到该元素， 或者 过了n秒 最大时长。'''
wd.implicitly_wait(5)

# 调用WebDriver 对象的get方法 可以让浏览器打开指定网址
wd.get('https://core.ac.uk/search/?q=%28Chemical+Vapor+Deposition%29%28CVD%29%28Magnetic+Thin+Films%29%28Microstructure%29%28Magnetic+Properties%29&page=1&sort=relevance')

wd.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div[2]/div[1]/div[1]/div[1]/div[1]/button').click()

wd.find_element(By.XPATH, '//*[@id="modal-root"]/div/div[2]/div/div/fieldset/div/div[2]').click()

wd.find_element(By.XPATH, '//*[@id="modal-root"]/div/div[2]/div/div/footer/button[2]').click()

# 程序运行完会自动关闭浏览器，就是很多人说的闪退；加入等待用户输入，防止闪退
input('【避免闪退】请按回车键完全结束程序')