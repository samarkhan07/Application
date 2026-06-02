import streamlit as st
import time
import requests
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- STREAMLIT KEEP-ALIVE SYSTEM ENVIRONMENT SHIELD ---
st.set_page_config(page_title="Darkstar Engine Worker Base", page_icon="⚡", layout="centered")
st.markdown("""
    <style>
        .stApp { background-color: #030712; }
        .shield-banner {
            text-align:center; padding:45px; margin-top:40px;
            background: linear-gradient(135deg, #0f172a 0%, #022c22 100%);
            border-radius:24px; border:1px solid #10b981;
            box-shadow: 0 0 25px rgba(16,185,129,0.15);
        }
        h1, p { font-family: 'Outfit', sans-serif; }
    </style>
    <div class="shield-banner">
        <h1 style="color:#10b981; font-size:26px; font-weight:800; letter-spacing:1px;">⚡ DARKSTAR CORE RECOVERY ENGINE</h1>
        <p style="color:#94a3b8; font-size:14px; margin-top:10px;">Execution state: Active background compilation array matrix loop is ongoing.</p>
    </div>
""", unsafe_allow_html=True)

# ---- CENTRAL CONFIG PLATFORM DATA MAPPING & SECURE TUNNEL ----
# ==================== ADVANCED CONFIGURATION MATRIX ====================
# Apne Bot Hosting ka exact URL yahan dalein (Bina slash '/' ke end me)
BOT_HOSTING_URL = "http://your-bot-portfolio.pterodactyl.io"  
WORKER_SECRET_TOKEN = "DARKSTAR_SECURE_PASSPHRASE_2026"
# =======================================================================

# Request headers inject authentic parameters
HEADERS = {
    "Authorization": WORKER_SECRET_TOKEN,
    "Origin": "https://share.streamlit.io", # Standard origin masking
    "Referer": "https://share.streamlit.io/"
}

# --- PERSISTENT SINGLE INSTANCE CHROMIUM ALLOCATION ---
@st.cache_resource
def get_shared_browser_instance():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    chromium_paths = ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/chrome']
    for path_element in chromium_paths:
        if Path(path_element).exists():
            chrome_options.binary_location = path_element
            break
            
    driver_instance = webdriver.Chrome(options=chrome_options)
    driver_instance.set_window_size(1920, 1080)
    return driver_instance

def find_editable_input_field(driver):
    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        '[role="textbox"]',
        'textarea'
    ]
    for sel in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in elements:
                if el.is_displayed():
                    return el
        except: continue
    return None

def push_sync_update_to_base(task_id, payload):
    payload['id'] = task_id
    try:
        requests.post(f"{BOT_HOSTING_URL}/api/worker/update", json=payload, headers=HEADERS, timeout=12)
    except: pass

# ---- SYSTEM BACKGROUND WORKER RUNNER LOOP ----
def core_background_processing_pipeline():
    try:
        driver = get_shared_browser_instance()
    except Exception as initialization_error:
        st.error(f"Chromium instance binding crash notice: {initialization_error}")
        return

    task_execution_timers_map = {}

    while True:
        try:
            # Sync central array matrices tasks data sets via dynamic route
            response = requests.post(f"{BOT_HOSTING_URL}/api/worker/sync", headers=HEADERS, timeout=12)
            if response.status_code != 200:
                time.sleep(8)
                continue
                
            active_tasks_list = response.json().get('tasks', [])
            
            for current_task in active_tasks_list:
                task_id = current_task['id']
                loop_delay = int(current_task['delay'])
                current_epoch_time = time.time()
                
                # Verify schedule matrix frequency allocation maps
                if task_id in task_execution_timers_map:
                    if current_epoch_time - task_execution_timers_map[task_id] < loop_delay:
                        continue
                
                task_execution_timers_map[task_id] = current_epoch_time
                push_sync_update_to_base(task_id, {"log": "Accessing synchronized matrix payload profile sequence..."})
                
                cookies_input_data = current_task.get('cookies', '')
                cookies_list = [c.strip() for c in cookies_input_data.split('\n') if c.strip()] if current_task['cookie_type'] == 'multiple' else [cookies_input_data]
                messages_list = [m.strip() for m in current_task['messages'].split('\n') if m.strip()]
                
                if not cookies_list or not messages_list:
                    push_sync_update_to_base(task_id, {"log": "Parsing parameters validation error: Inputs matrix is void."})
                    continue

                try:
                    # COMPLETE ISOLATION FLUSH: Pure safety initialization profile
                    driver.delete_all_cookies()
                    driver.execute_script("window.localStorage.clear();")
                    driver.execute_script("window.sessionStorage.clear();")
                    
                    driver.get("https://www.facebook.com/")
                    time.sleep(4)
                    
                    current_rotation_index = current_task['messages_sent'] % len(cookies_list)
                    targeted_cookie_string = cookies_list[current_rotation_index]
                    
                    for parsed_cookie_pair in targeted_cookie_string.split(';'):
                        if '=' in parsed_cookie_pair:
                            c_name, c_val = parsed_cookie_pair.strip().split('=', 1)
                            try:
                                driver.add_cookie({'name': c_name, 'value': c_val, 'domain': '.facebook.com', 'path': '/'})
                            except: pass
                            
                    # Context Routing redirection
                    driver.get(f"https://www.facebook.com/messages/e2ee/t/{current_task['chat_id']}")
                    time.sleep(8)
                    
                    if '/messages/e2ee' not in driver.current_url and '/e2ee/t/' not in driver.current_url:
                        driver.get(f"https://www.facebook.com/messages/t/{current_task['chat_id']}")
                        time.sleep(8)

                    input_element_box = find_editable_input_field(driver)
                    if not input_element_box:
                        raise Exception("Target terminal chat injection field element interface not matched.")

                    raw_msg_body = messages_list[current_task['messages_sent'] % len(messages_list)]
                    final_compiled_payload_text = f"{current_task['name_prefix']} {raw_msg_body}".strip()

                    # Trigger browser DOM text modification mappings
                    driver.execute_script("""
                        const el = arguments[0];
                        el.focus();
                        if(el.tagName === 'DIV') {
                            el.textContent = arguments[1];
                            el.innerHTML = arguments[1];
                        } else { el.value = arguments[1]; }
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    """, input_element_box, final_compiled_payload_text)
                    time.sleep(2)

                    # Dispatch transmission event interfaces
                    is_sent_via_button = driver.execute_script("""
                        const btn = document.querySelector('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                        if(btn && btn.offsetParent !== null) { btn.click(); return true; }
                        return false;
                    """)

                    if not is_sent_via_button:
                        driver.execute_script("""
                            arguments[0].focus();
                            arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true}));
                        """, input_element_box)

                    # Update internal tracking counters configurations
                    updated_total_sent_count = current_task['messages_sent'] + 1
                    push_sync_update_to_base(task_id, {
                        "messages_sent": updated_total_sent_count,
                        "failed_since": None,
                        "log": f"Success: Dispatched message chunk payload tracking data #{updated_total_sent_count}"
                    })

                except Exception as individual_task_loop_error:
                    error_string_log = str(individual_task_loop_error)[:75]
                    push_sync_update_to_base(task_id, {"log": f"Processing Exception Interrupt: {error_string_log}"})
                    
                    if not current_task.get('failed_since'):
                        current_timestamp_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        push_sync_update_to_base(task_id, {"failed_since": current_timestamp_stamp})
                        
        except Exception as global_pipeline_system_error:
            time.sleep(6)
        time.sleep(1)

# Initialize single pipeline processing execution thread matrix securely
if "pipeline_thread_lock" not in st.session_state:
    st.session_state["pipeline_thread_lock"] = True
    import threading
    system_execution_thread = threading.Thread(target=core_background_processing_pipeline, daemon=True)
    system_execution_thread.start()
