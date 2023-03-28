from selenium.common.exceptions import JavascriptException

class abreCV(object):
    def __init__(self):
        pass

    def __call__(self, driver):
        try:
            driver.execute_script("""window.frames.frameModalPreview.abreCV()""")
            return True
        except JavascriptException:
            return False
        
class tabs(object):
    def __init__(self, equals=-1, more_than=-1, less_than=-1):
        self.equals = equals
        self.more_than = more_than
        self.less_than = less_than

    def __call__(self, driver):
        if (self.equals != -1):
            if len(driver.window_handles) == self.equals:
                return True
        elif (self.more_than != -1):
            if len(driver.window_handles) > self.more_than:
                return True
        elif (self.less_than != -1):
            if len(driver.window_handles) < self.less_than:
                return True
        return False