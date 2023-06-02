import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions 
from selenium.webdriver.support.ui import WebDriverWait
import re
from bs4 import BeautifulSoup
 
# Log in the qq zone
def login(my_qq):
 
    browser = webdriver.Chrome()
    browser.get('https://i.qq.com/')
    #browser.maximize_window()
    time.sleep(2)
    browser.switch_to.frame("login_frame")
    time.sleep(2)

    try:
        find = browser.find_element(by=By.ID, value='img_out_%s' %my_qq)
        find.click()
        time.sleep(2)

    except Exception as error:
        print('Log Error! %s' %error)

    else:
        print("Successfully Logged!")
        browser.switch_to.default_content()
    return browser

# Use regular expression to match the text pattern
def getText(match,text,group=1):
    tmp = re.search(match,text,re.S)
    if (tmp==None):
        return ""
    else:
        return tmp.group(group)

# Get the text from the website and analyze it
def get(html, num_message, num_page):

    print('Trying to get shuoshuos')
    time.sleep(2)
    soup = BeautifulSoup(html, "html.parser")
    shuoshuos = soup.find_all(name="li", attrs={"class":"feed"})
    print('There are %d messages.' %len(shuoshuos))

    for i in range(len(shuoshuos)):
        text=shuoshuos[i].get_text()
        print(text)

        user = getText(r"(.*?)[ ](.*)查看详情(.*)举报赞(.*)", text)
        content = getText(r"(.*?)[ ](.*)查看详情(.*)举报赞(.*)", text, group=2)
        sendtime = getText(r"(.*?)[ ](.*)查看详情(.*)举报赞(.*)", text, group=3)
        else_stuff = getText(r"(.*?)[ ](.*)查看详情(.*)举报赞(.*)", text, group=4)

        if (num_message+i) == 0:
            f = open('./out/%s.txt' %user, 'w', encoding='utf-8')
        else:
            f = open('./out/%s.txt' %user, 'a', encoding='utf-8')

        f.write('%d\n' %(num_message+i+1))
        f.write('%s\n' %user)
        f.write('%s\n' %sendtime)
        f.write('%s\n' %content)
        f.write('%s\n' %else_stuff)
        f.write('On page %s\n' %num_page)
        f.write('\n')
        print("\033[0;31mWriting contents of %s_%s_%s.txt\033[0m" %(user,str(i+1), sendtime))
 
    return (num_message + len(shuoshuos))

def main():
    # Log in
    my_qq = ''
    driver = login(my_qq)

    # Get to the friend's qq zone
    friendlist = ['']
    print('Trying to get into the qq zone')
    time.sleep(2)

    driver.get('https://user.qzone.qq.com/' + friendlist[0] + '/311')
    print('Get in!')
    num_message = 0
    num_page = 1

    # If you occur the problem of the website and have to stop in the middle, you can add the input() function
    # And restart the program to switch to the page where you stopped before the program starts again
    # input()

    # Get the contents
    while(1):
        # Move to the qq zone frame
        iframe = driver.find_element(by=By.ID, value='app_canvas_frame')
        time.sleep(2)
        wait_element = WebDriverWait(driver, 20)
        wait_element.until(expected_conditions.frame_to_be_available_and_switch_to_it(iframe))

        # Find the unfold buttons and click them
        while(1):
            try:
                print('Trying to find unfold button')
                buttons = driver.find_elements(by=By.XPATH, value='//a[contains(@class, "has_more_con") and contains(text(), "展开查看全文")]')
                for button in buttons:
                    print(button)
                    time.sleep(5)
                    driver.execute_script('arguments[0].scrollIntoView(false);', button)
                    time.sleep(2)
                    button.click()
                break
            except Exception as error:
                    print('\033[0;31mUnfold error! %s \033[0m' %error)
                    continue

        # Get the html source code
        time.sleep(2)
        html = driver.page_source
        num_message = get(html, num_message, num_page)
        num_retry = 0
        while(1):
            try:
                nextpage = driver.find_element(by=By.XPATH, value='//a[@title="下一页"]')
                nextpage.click()
                num_page += 1
                print('\033[0;33m\nMove to page %d!\033[0m' %num_page)
                break
            except Exception as error:
                num_retry += 1
                print('\033[0;31mNext page error! %s \033[0m' %error)
                print('\033[0;32mRetry for %d time\033[0m' %num_retry)
                time.sleep(1)

        driver.switch_to.default_content()
    driver.close()
 
if __name__ == '__main__':
    main()
