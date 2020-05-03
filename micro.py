import csv
import zipfile
import time
import random
import string
import requests
import os.path
import threading
import imaplib
import getpass, os, imaplib, email
import tkinter as tk
import names
import pybase64
import schedule
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from email.parser import HeaderParser
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from random import randint


def read_config_data():
    with open('city.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        global list_city
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if (line_count % 2) == 0:
                    line_count += 1
                    continue
                city = {}
                city['City Name'] = row[0]
                city['Postal Code'] = row[1]
                city['State'] = row[2]
                list_city.append(city)
                line_count += 1

                
        
        print(f'Processed {line_count} lines.')



# Create random Email
def Create_email():
    letters = string.ascii_lowercase
    email = ''.join(random.choice(letters) for i in range(randint(5,7)))
    for j in range(randint(4,6)):
        email += str(randint(0,9))
    email += "@liveemail24.de"
    return email

# Create agent list. as much as user inupt
def Create_agent_list(num_account):
    
    for i in range(num_account):
        index = randint(1,city_limit)
        amount_proxy = len(list_proxy)-1
        agent = {}
        agent['Email'] = Create_email()
        agent['City'] = list_city[index]['City Name']
        agent['Postal Code'] = list_city[index]['Postal Code']
        agent['State'] = list_city[index]['State']
        agent['First Name'] = names.get_first_name(gender='male')
        agent['Last Name'] = names.get_last_name()
        agent['Proxy Ip'] = list_proxy[randint(0,amount_proxy)]['IP']
        agent['Proxy Port'] = list_proxy[randint(0,amount_proxy)]['Port']
        agent['Email Pwd'] = ""
        list_agent.append(agent)

def read_proxy_data():
    with open('proxy.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        global list_proxy
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                proxy = {}
                proxy['IP'] = row[0]
                proxy['Port'] = row[1]
                list_proxy.append(proxy)
                line_count += 1
        print(f'Processed {line_count} lines.')

# Generate Password (should not involve continusly number or letter)
def generate_password(stringLength=10):
    letters = string.ascii_lowercase
    password =  ''
    for i in range(4):
        newnum = str(randint(0,9))
        newletter = random.choice(letters)
        password += newnum + newletter
    return password


# Create Chrome driver
def Create_driver(address = "23.88.195.47:23667", username = "mare", userpass = "WuBA8ujAD"):
    proxy = {'address': address,
            'username': username,
            'password': userpass}

    capabilities = dict(DesiredCapabilities.CHROME)
    capabilities['proxy'] = {'proxyType': 'MANUAL',
                            'httpProxy': proxy['address'],
                            'ftpProxy': proxy['address'],
                            'sslProxy': proxy['address'],
                            "noProxy":None,
                            "proxyType":"MANUAL",
                            "class":"org.openqa.selenium.Proxy",
                            "autodetect":False}


    # capabilities['proxy']['socksUsername'] = proxy['username']
    # capabilities['proxy']['socksPassword'] = proxy['password']

    options = Options()
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors", "safebrowsing-disable-download-protection", "safebrowing-disable-auto-update", "disable-client-side-phishing-detection"])
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=default')
    options.add_argument('--incognito')
    options.add_argument('--disable-plugin-discovery')
    options.add_argument('--start-maximized')
    options.add_argument("--enable-automation")
    options.add_argument("--test-type=browser")
    options.add_argument('--proxy-server=%s' %  proxy['address'])

    driver = webdriver.Chrome(executable_path="chromedriver", options = options,desired_capabilities=capabilities)
    # driver = webdriver.Chrome(executable_path="chromedriver", options = options)
    # desired_capabilities=capabilities
    time.sleep(3)
    upgrade_status(proxy['address'])
    
    return driver

def pass_captcha(img_url):
    img = pybase64.b64encode(requests.get(img_url).content)
    if img.decode("utf-8").strip() == "":
        return "Error No Image"
    API_KEY = '7c2e86703284311b6e6b09845f815bf3' 
    url = 'http://2captcha.com/in.php'
    data = {'key': API_KEY, 'method': 'base64' , 'body':img}
    res = requests.post(url, data=data)
    if res.status_code == 200:
        upgrade_status(res.text)
        if len(res.text.split("|")) > 1:
            id = res.text.split("|")[1]
            upgrade_status(id)
            url = "https://2captcha.com/res.php?key=%s&action=get&id=%s"%(API_KEY,id)
            recaptcha_answer = requests.get(url).text
            while 'CAPCHA_NOT_READY' in recaptcha_answer:
                time.sleep(5)
                recaptcha_answer = requests.get(url).text
                upgrade_status("[:--->> waiting token......")
            upgrade_status(recaptcha_answer.split('|')[1])
            return recaptcha_answer.split('|')[1].replace(" ","")
    else:
        upgrade_status("error")
        return "Error Response"


def email_verify():
    try:
        conn = imaplib.IMAP4_SSL(host='ha01s015.org-dns.com')
        (retcode, capabilities) = conn.login("fifa@liveemail24.de","j*j1sY20")
    
    except:
        return "Error Log in"
    init_amount = 0
    comming = False
    for i in range(20):
        # conn.select(readonly = 1)
        time.sleep(1)
        typ, mcount = conn.select("Inbox")
        (retcode, message) = conn.search(None,'(UNSEEN)')
        mail_ids = []
        for block in message:
            mail_ids += block.split()
        if comming and len(mail_ids) !=0:
            break
        if len(mail_ids) == 0:
            comming = True
        if init_amount !=0 and init_amount !=len(mail_ids):
            break
        init_amount = len(mail_ids)
        
    if len(mail_ids) == 0:
        return "Error No Email Received"
    for i in mail_ids:
        conn.store(i, '+FLAGS', '\Seen') 
        status, data = conn.fetch(i, '(RFC822)')
        # print(data)
        code = ''
        try:
            if  str(data).count("Microsoft account") > 0:
                code = str(data).split("this security code:")[1].split("If you didn")[0].replace("\\n","").replace("\\r","").strip()
                # return link
                upgrade_status(code)
            else:
                # print(str(data)
                upgrade_status("not from Microsoft")
        except:
            upgrade_status("invalid format")
        conn.store(i, '+FLAGS', '\Seen')

    if len(code) == 4:
        return code
    return "Error Verification Failed"

# save account information
def save_all_data(Email = "", firstname = "", lastname = "",  password = "",  birth_day = "", online_id = "", email_pwd = "", proxy = "", status = "", Country = "", City = "",State = "", Postal_code = ""):
    upgrade_status("[:--->> Saving result data...")
    write_header = False
    if not os.path.exists('account.csv'):
        write_header = True
    with open('account.csv', 'a', newline='') as csvfile:

        fieldnames = ['Email','Password', 'Country','Language','Date of birth','City','State/Province','Postal Code','Online ID','First Name','Last Name','Email PW','Proxy','Result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({'Email' : Email,'Password': password, 'Country': Country,'Language':"English",'Date of birth':birth_day,
                        'City': City,'State/Province': State ,'Postal Code': Postal_code,'Online ID' : online_id,'First Name' : firstname,'Last Name' : lastname,'Email PW' :email_pwd,'Proxy' : proxy, 'Result' : status})

# save log file
def export_logfile(data):
    with open("Log.txt","a") as f:
        f.write(" \n\n\n @@ : " + time.ctime())
        f.write("\n")
        f.write(data)
        f.write("\n")

def export_blocked_proxy(data):
    with open("blocked_proxy.txt","a") as f:
        f.write("\n")
        f.write(data)

def page_one(driver, index):
    try:
        #start first page
        while True:
            try:
                input_email = driver.find_element_by_xpath( '//*[@id="MemberName"]' )
                break
            except:
                time.sleep(1)
        input_email.send_keys(list_agent[index]['Email'])
        btn_next = driver.find_element_by_xpath('//*[@id="iSignupAction"]')
        btn_next.click()
    except:
        return "Unknown Error_1"
    time.sleep(2)
    try:
        btn_next = driver.find_element_by_xpath('//*[@id="iSignupAction"]')
        error_message = driver.find_element_by_xpath('//*[@id="MemberNameError"]').get_attribute('innerHTML')
        return error_message
    except:
        return "Success"

def page_second(driver, index):
    try:
        while True:
            try:
                input_password = driver.find_element_by_xpath('//*[@id="PasswordInput"]')
                break
            except:
                time.sleep(1)
        global Password
        Password = generate_password()
        input_password.send_keys(Password)
        btn_next = driver.find_element_by_xpath('//*[@id="iSignupAction"]')
        btn_next.click()
        time.sleep(3)
        try:
            err_msg = driver.find_element_by_xpath('//*[@id="PasswordError"]')
            upgrade_status(err_msg)
            return err_msg
        except:
            pass
        return "Success"
    except:
        return "Unknown Error_2"

def page_third(driver, index):

    try:
        while True:
            try:
                input_firstname = driver.find_element_by_xpath('//*[@id="FirstName"]')
                break
            except:
                time.sleep(1)
        input_lastname = driver.find_element_by_xpath('//*[@id="LastName"]')
        input_firstname.send_keys(list_agent[index]['First Name'])
        input_lastname.send_keys(list_agent[index]['Last Name'])
        btn_next = driver.find_element_by_xpath('//*[@id="iSignupAction"]')
        btn_next.click()
        return "Success"
    except:
        return "Unknown Error_3"

def page_four(driver, index):
    try:
        while True:
            try:
                select_country = Select(driver.find_element_by_xpath('//*[@id="Country"]'))
                break
            except:
                time.sleep(1)

        select_month = Select(driver.find_element_by_xpath('//*[@id="BirthMonth"]'))
        select_day = Select(driver.find_element_by_xpath('//*[@id="BirthDay"]'))
        select_year = Select(driver.find_element_by_xpath('//*[@id="BirthYear"]'))
        birth_month = randint(1,12)
        birth_year = randint(1978,1990)
        birth_day = randint(1,28)
        select_month.select_by_value(str(birth_month))
        select_day.select_by_value(str(birth_day))
        select_year.select_by_value(str(birth_year))
        select_country.select_by_value("US")
        
        global Birthday
        Birthday = str(birth_month) + "/" + str(birth_day) + "/" + str(birth_year)

        btn_next = driver.find_element_by_xpath('//*[@id="iSignupAction"]')
        btn_next.click()
        return "Success"
    except:
        return "Unknown Error_4"

def page_five(driver, index):
    try:
        while True:
            try:
                input_verify_code = driver.find_element_by_xpath('//*[@id="VerificationCode"]')
                break
            except:
                time.sleep(1)
        input_verify_code.send_keys(email_verify())
        btn_next = driver.find_element_by_xpath('//*[@id="iSignupAction"]')
        btn_next.click()
        time.sleep(3)
        try:
            msg_error = driver.find_element_by_xpath('//*[@id="VerificationCodeError"]')
            upgrade_status(msg_error)
        except:
            pass
        return "Success"
    except:
        return "Unknown Error_5"

def page_six(driver, index):
    time.sleep(3)
    try:
        phone_require = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div/div[3]/div[1]/div[5]/div/div/form/div[2]/div[4]/div[1]/div[2]/label').get_attribute("innerHTML")
        upgrade_status(phone_require)
        if phone_require == "Phone number":
            return "Error. Require phone"
        upgrade_status(phone_require)
    except:
        pass
    #captcha
    time.sleep(3)
    try:
        captcha_container = driver.find_element_by_class_name("win-scroll").get_attribute("innerHTML")
        if "Enter the characters you see" not in captcha_container:
            return "No captcha"
        input_code = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[5]/div/div/form/div[5]/div[3]/input')
                                                
        btn_next = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[5]/div/div/form/div[7]/div/div/div[2]/input')
        btn_refresh = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[5]/div/div/form/div[5]/div[2]/a[1]')

        for i in range(3):            
            cap_image = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[5]/div/div/form/div[5]/div[1]/img').get_attribute("src")            
            cap_code = (pass_captcha(cap_image))
            upgrade_status(cap_code)
            if "Error" in cap_code:
                btn_refresh.click()
                continue
            input_code.send_keys(cap_code)
            btn_next.click()
            for j in range(3):
                time.sleep(3)
                try:
                    me_ctrl_trigger = driver.find_elements_by_xpath('//*[@id="mectrl_main_trigger"]')
                    return "Success"
                except:
                    pass
        return "Error Failed avoid captcha"
        
    except:
        return "Unknown Error_6"
def page_seven(driver, index):
    print("this is step 7")
    time.sleep(3)
    try:
        phone_require = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[5]/div/div/form/div[5]/div[1]/div[2]/label').get_attribute("innerHTML")                                          
        upgrade_status(phone_require)
        if phone_require == "Phone number":
            return "Error. Require phone"
        upgrade_status(phone_require)
    except:
        return "Success"

def _loop(index):

    url = "https://signup.live.com/"
    
    proxy_index = randint(0,len(list_proxy)-1)
    
    while True:
        driver = Create_driver(list_proxy[randint(0,proxy_index)]['IP'] + ":"  + list_proxy[randint(0,proxy_index)]['Port'])
        driver.get(url)
        time.sleep(5)
        upgrade_status("start")
        try:
            msg_no_internet = driver.find_element_by_xpath('//*[@id="main-message"]/p').get_attribute('innerHTML')
            driver.close()
            upgrade_status(msg_no_internet)
            upgrade_status("Blocked proxy : " + list_proxy[proxy_index]['IP'])
            damaged_proxy_list.append(list_proxy[proxy_index]['IP'])
            while True:
                proxy_index = randint(0,len(list_proxy)-1)
                doublicated = False
                for i in range(len(damaged_proxy_list)):
                    if proxy_index == damaged_proxy_list[i]:
                        doublicated = True
                        break
                if doublicated == False:
                    break
        except:
            break

    
    time.sleep(2)
    result = page_one(driver,index)
    upgrade_status(result)
    if "Error" in result:
        save_all_data(Email = list_agent[index]["Email"],State = list_agent[index]["State"], Postal_code = list_agent[index]["Postal Code"], City = list_agent[index]["City"]  ,password = Password, status = result)
        driver.close()
        return
    result = page_second(driver, index)
    upgrade_status(result)
    if "Error" in result:
        save_all_data(Email = list_agent[index]["Email"],State = list_agent[index]["State"], Postal_code = list_agent[index]["Postal Code"], City = list_agent[index]["City"]  ,password = Password, status = result)
        driver.close()
        return
    result = page_third(driver, index)
    upgrade_status(result)
    if "Error" in result:
        save_all_data(Email = list_agent[index]["Email"],State = list_agent[index]["State"], Postal_code = list_agent[index]["Postal Code"], City = list_agent[index]["City"]  ,password = Password, status = result)
        driver.close()
        return
    result =  page_four(driver, index)
    upgrade_status(result)
    if "Error" in result:
        save_all_data(Email = list_agent[index]["Email"],State = list_agent[index]["State"], Postal_code = list_agent[index]["Postal Code"], City = list_agent[index]["City"]  ,password = Password, status = result)
        driver.close()
        return
    result =  page_five(driver, index)
    upgrade_status(result)
    if "Error" in result:
        save_all_data(Email = list_agent[index]["Email"],State = list_agent[index]["State"], Postal_code = list_agent[index]["Postal Code"], City = list_agent[index]["City"]  ,password = Password, status = result)
        driver.close()
        return
    result =  page_six(driver, index)
    upgrade_status(result)
    if "Error" in result:
        save_all_data(Email = list_agent[index]["Email"],State = list_agent[index]["State"], Postal_code = list_agent[index]["Postal Code"], City = list_agent[index]["City"]  ,password = Password, status = result)
        driver.close()
        return
    result = page_seven(driver,index)
    if "Error" in result:
        save_all_data(Email = list_agent[index]["Email"],State = list_agent[index]["State"], Postal_code = list_agent[index]["Postal Code"], City = list_agent[index]["City"]  ,password = Password, status = result)
        driver.close()
        return
    upgrade_status("[:--->> Saving result data...")
    save_all_data(Email = list_agent[index]["Email"],
        firstname = list_agent[index]["First Name"],
        lastname = list_agent[index]["Last Name"],
        password = Password,
        birth_day = Birthday,
        email_pwd = list_agent[index]["Email Pwd"],
        proxy = list_agent[index]['Proxy Ip'] + ":" +list_agent[index]['Proxy Port'],
        status = "Success",
        City = list_agent[index]["City"],
        State = list_agent[index]["State"],
        Postal_code = list_agent[index]["Postal Code"])
    driver.close()
    return

def upgrade_status(status):
    print(status)
    T.insert(END, status +  "\n")
    T.see("end")
    root.update_idletasks()


def disable_status():

    Entry_number_account['state'] = 'disable'
    Btn_start['state'] = 'disable'


def enable_status():
    Entry_number_account['state'] = 'normal'
    Btn_start['state'] = 'normal'



def Start():

    threading.Thread(target=main_loop).start()

def Start_Cron():


    Start()

def main_loop():
    # driver = Create_driver()
    # driver.get("https://id.sonyentertainmentnetwork.com/create_account/")
    # verify_result = email_verify(driver,list_agent[0]['Email'], list_agent[0]['Email Pwd'])
    # upgrade_status( verify_result )
    # _loop(1)
    # i = 1
    # for i in range (len()):
        # _loop(i)
    disable_status()
    if Entry_number_account.get() == "":
        messagebox.showerror("Error", "Please input number of accounts")
        return
    total_number = int(Entry_number_account.get())
    
    try:
        if total_number < 0:
            messagebox.showerror("Error", "Number of account should above 1")
    except:
        messagebox.showerror("Error", "Invalid input")
    Create_agent_list(total_number)
    print(list_agent)
    for i in range(total_number):
        if(i% 10 ==1):
            upgrade_status("Cron Running!")
            time.sleep(60 * int(Entry_time_cron.get()))
        _loop(i)

    file_directory = os.path.dirname(os.path.abspath(__file__))
    export_logfile(T.get('1.0', END))
    for i in range(len(damaged_proxy_list)):
        export_blocked_proxy(str(damaged_proxy_list[i]))
    upgrade_status("********All task Finished******** \n result data saved in %s \ acount.csv"%file_directory)   
    enable_status()


if __name__ == '__main__':

    list_city = []
    list_agent = []
    list_proxy = []
    damaged_proxy_list = []
    Password =''
    Birthday = ''
    read_config_data()
    read_proxy_data()
    print(len(list_proxy))
    city_limit = len(list_city)
    print(city_limit)
    root = Tk() 
    root.geometry("700x250")
    root.title("Microsoft account Creator")
    root.wm_attributes("-topmost", 1)


    root.grid_columnconfigure(0, weight = 1)
    root.grid_columnconfigure(1, weight = 3)
    root.grid_columnconfigure(2, weight = 1)

    Label_number_account =  Label(root, text="Number of Accounts", width = 20)
    Label_number_account.grid(row = 1, column = 0 , sticky = E)
    Entry_number_account =  Entry(root, bd =2, width = 30)
    Entry_number_account.grid(row = 1, column = 1)
    Label_time_cron =  Label(root, text="Time of Cron(Min)", width = 20)
    Label_time_cron.grid(row = 2, column = 0 , sticky = E)
    Entry_time_cron =  Entry(root, bd =2, width = 30)
    Entry_time_cron.grid(row = 2, column = 1)

    Btn_start = Button(root, width = 20, text = "Start", command = lambda: Start_Cron())
    Btn_start.grid( row = 1, column = 2, sticky = W + E)
    Btn_start.grid(padx=30, pady=5)

    Label_status =  Label(root, text="Current status", width = 20)
    Label_status.grid(row = 3, column = 0 , sticky = E)

    output_status = Frame(root,width = 700,height = 10, background = "pink")
    output_status.grid(columnspan = 5, row = 4,rowspan = 8, sticky = W+E,padx=20, pady=5)

    S = Scrollbar(output_status)
    T = Text(output_status, height=10, width=700, state="normal")
    S.pack(side=RIGHT, fill=Y)
    T.pack(side=TOP, fill=Y)
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)


    mainloop()