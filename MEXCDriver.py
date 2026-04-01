import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MEXCDriver:
    def __init__(self, startup_url: str = "https://www.mexc.com/", options: uc.ChromeOptions = uc.ChromeOptions()):
        self.driver = uc.Chrome(options=options)
        self.driver.get(startup_url)

    def max_slider(self):
        xpath = "/html/body/div[3]/section/div[3]/div[7]/section/div[2]/div[2]/div[1]/div/div/div[4]/div[2]/div/div[3]/span[5]"
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        element.click()
    
    def buy(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "component_longBtn__eazYU"))
        )
        element.click()
    
    def sell(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "component_shortBtn__x5P3I"))
        )
        element.click()
   
    def flash_close_position(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "FastClose_flashCloseBtn__4uyRa"))
        )
        element.click()
    
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def refresh(self):
        self.driver.refresh()

    def close(self):
        self.driver.quit()
    
    def goto(self, url: str):
        self.driver.get(url)