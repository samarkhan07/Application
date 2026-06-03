import time
import threading
import requests
import logging
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==================== HARDCODED URLS ====================

# Bot Hosting Server URL
BOT_HOSTING_URL = "http://fi13.bot-hosting.cloud:20767" 

# Secret key for authentication
STREAMLIT_SECRET_KEY = "darkstar-secret-key-2024-xyz789abc123"

# ==================== CONFIGURATION ====================

RUNNING_TASKS = {}
SHARED_DRIVER = None
DRIVER_LOCK = threading.Lock()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== API FUNCTIONS ====================

def get_headers():
    """Get headers for bot hosting API"""
    return {
        'X-Streamlit-Secret': STREAMLIT_SECRET_KEY,
        'Content-Type': 'application/json'
    }

def fetch_active_tasks():
    """Fetch active tasks from bot hosting"""
    try:
        url = f'{BOT_HOSTING_URL}/api/streamlit/tasks'
        resp = requests.get(url, headers=get_headers(), timeout=10)
        
        if resp.status_code == 200:
            tasks = resp.json().get('tasks', [])
            logger.info(f"Fetched {len(tasks)} active tasks")
            return tasks
        else:
            logger.error(f"Failed to fetch tasks: {resp.status_code}")
            return []
    except Exception as e:
        logger.error(f"Fetch tasks error: {str(e)}")
        return []

def notify_restart():
    """Notify bot hosting that Streamlit restarted - get all tasks"""
    try:
        url = f'{BOT_HOSTING_URL}/api/streamlit/restart'
        resp = requests.get(url, headers=get_headers(), timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"Restart notification sent. {data.get('count', 0)} tasks to resume")
            return True
        else:
            logger.error(f"Restart notification failed: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"Restart notification error: {str(e)}")
        return False

def send_log(task_id, msg):
    """Send log to bot hosting"""
    try:
        url = f'{BOT_HOSTING_URL}/api/streamlit/log'
        requests.post(url, headers=get_headers(), json={'task_id': task_id, 'message': msg}, timeout=5)
    except Exception as e:
        logger.error(f"Log send error: {str(e)}")

def update_status(task_id, msgs, running, status='running'):
    """Update task status on bot hosting"""
    try:
        url = f'{BOT_HOSTING_URL}/api/streamlit/update'
        requests.post(url, headers=get_headers(),
                     json={'task_id': task_id, 'messages_sent': msgs, 'is_running': running, 'status': status},
                     timeout=5)
    except Exception as e:
        logger.error(f"Status update error: {str(e)}")

def keep_alive():
    """Keep Streamlit alive - send health check every 30 seconds"""
    while True:
        try:
            time.sleep(30)
            url = f'{BOT_HOSTING_URL}/api/health'
            requests.get(url, timeout=5)
            logger.debug("Keep-alive ping sent")
        except:
            pass

# ==================== LOGGING ====================

def log_msg(msg, task_id):
    """Log message with timestamp"""
    ts = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{ts}] {msg}"
    send_log(task_id, formatted)
    logger.info(f"[{task_id[:8]}] {msg}")

# ==================== BROWSER MANAGEMENT ====================

def setup_browser(task_id):
    """Setup Chrome browser"""
    log_msg('Browser setup starting...', task_id)
    
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-setuid-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    for path in ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/chrome']:
        if Path(path).exists():
            opts.binary_location = path
            log_msg(f'Found Chromium at: {path}', task_id)
            break
    
    try:
        driver = webdriver.Chrome(options=opts)
        driver.set_window_size(1920, 1080)
        log_msg('Browser setup completed!', task_id)
        return driver
    except Exception as e:
        log_msg(f'Browser setup failed: {str(e)[:100]}', task_id)
        raise

def get_driver(task_id):
    """Get or create shared driver"""
    global SHARED_DRIVER
    with DRIVER_LOCK:
        if SHARED_DRIVER is None:
            SHARED_DRIVER = setup_browser(task_id)
        return SHARED_DRIVER

def close_driver():
    """Close shared driver"""
    global SHARED_DRIVER
    with DRIVER_LOCK:
        if SHARED_DRIVER:
            try:
                SHARED_DRIVER.quit()
                logger.info("Browser closed")
            except:
                pass
            SHARED_DRIVER = None

# ==================== MESSAGE INPUT ====================

def find_input(driver, task_id):
    """Find message input field"""
    log_msg('Finding message input...', task_id)
    time.sleep(5)
    
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except:
        pass
    
    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]'
    ]
    
    for sel in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            for elem in elements:
                try:
                    is_visible = driver.execute_script("return arguments[0].offsetParent !== null;", elem)
                    if is_visible:
                        editable = driver.execute_script(
                            "return arguments[0].contentEditable === 'true' || "
                            "arguments[0].tagName === 'TEXTAREA' || "
                            "arguments[0].tagName === 'INPUT';", elem)
                        if editable:
                            log_msg('Message input found!', task_id)
                            return elem
                except:
                    pass
        except:
            pass
    
    log_msg('Message input not found!', task_id)
    return None

# ==================== TASK EXECUTION ====================

class TaskState:
    def __init__(self, task_id):
        self.task_id = task_id
        self.running = True
        self.msg_count = 0
        self.msg_idx = 0
        self.cookie_idx = 0
        self.consecutive_fails = 0

def send_task(task):
    """Send messages to Facebook E2EE"""
    task_id = task['id']
    driver = None
    state = TaskState(task_id)
    RUNNING_TASKS[task_id] = state
    
    try:
        log_msg('Task started', task_id)
        driver = get_driver(task_id)
        
        log_msg('Navigating to Facebook...', task_id)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        cookies_list = []
        if task['cookie_type'] == 'single':
            cookies_list = [task['cookies']]
        else:
            cookies_list = [c.strip() for c in task['cookies'].split('\n') if c.strip()]
        
        if not cookies_list or not cookies_list[0]:
            log_msg('ERROR: No cookies provided!', task_id)
            update_status(task_id, 0, False, 'failed')
            return
        
        log_msg('Adding cookies...', task_id)
        cookie_str = cookies_list[state.cookie_idx % len(cookies_list)]
        
        for c in cookie_str.split(';'):
            c = c.strip()
            if c and '=' in c:
                try:
                    name, value = c.split('=', 1)
                    driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com', 'path': '/'})
                except:
                    pass
        
        if task['chat_id']:
            chat_id = task['chat_id'].strip()
            log_msg(f'Opening chat: {chat_id[:15]}...', task_id)
            driver.get(f'https://www.facebook.com/messages/e2ee/t/{chat_id}')
            time.sleep(5)
            if '/e2ee/' not in driver.current_url:
                driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_msg('Opening messages page...', task_id)
            driver.get('https://www.facebook.com/messages')
        
        time.sleep(15)
        
        msg_input = find_input(driver, task_id)
        if not msg_input:
            log_msg('ERROR: Message input not found!', task_id)
            update_status(task_id, 0, False, 'failed')
            return
        
        delay = int(task['delay'])
        msgs = [m.strip() for m in task['messages'].split('\n') if m.strip()]
        if not msgs:
            msgs = ['Hello!']
        
        log_msg(f'Config: Delay={delay}s, Messages={len(msgs)}, Cookies={len(cookies_list)}', task_id)
        
        while state.running and task_id in RUNNING_TASKS:
            try:
                msg = msgs[state.msg_idx % len(msgs)]
                state.msg_idx += 1
                
                if task.get('name_prefix'):
                    msg = f"{task['name_prefix']} {msg}"
                
                if len(cookies_list) > 1:
                    new_idx = state.msg_count % len(cookies_list)
                    if new_idx != state.cookie_idx:
                        state.cookie_idx = new_idx
                        log_msg(f'Switching to cookie #{new_idx + 1}/{len(cookies_list)}', task_id)
                        
                        driver.delete_all_cookies()
                        driver.get('https://www.facebook.com/')
                        time.sleep(5)
                        
                        cookie_str = cookies_list[state.cookie_idx]
                        for c in cookie_str.split(';'):
                            c = c.strip()
                            if c and '=' in c:
                                try:
                                    name, value = c.split('=', 1)
                                    driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com', 'path': '/'})
                                except:
                                    pass
                        
                        driver.get(f'https://www.facebook.com/messages/e2ee/t/{task["chat_id"]}')
                        time.sleep(10)
                        msg_input = find_input(driver, task_id)
                        
                        if not msg_input:
                            log_msg('ERROR: Input not found after cookie switch!', task_id)
                            state.consecutive_fails += 1
                            continue
                
                driver.execute_script("""
                    const elem = arguments[0];
                    const text = arguments[1];
                    elem.scrollIntoView({behavior: 'smooth', block: 'center'});
                    elem.focus();
                    elem.click();
                    if (elem.tagName === 'DIV') {
                        elem.innerHTML = text;
                        elem.textContent = text;
                    } else {
                        elem.value = text;
                    }
                    elem.dispatchEvent(new Event('input', {bubbles: true}));
                    elem.dispatchEvent(new Event('change', {bubbles: true}));
                """, msg_input, msg)
                
                time.sleep(1)
                
                sent = driver.execute_script("""
                    const btns = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                    for (let btn of btns) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                """)
                
                if not sent:
                    driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));", msg_input)
                
                state.msg_count += 1
                state.consecutive_fails = 0
                update_status(task_id, state.msg_count, True, 'running')
                
                log_msg(f'Message #{state.msg_count} sent', task_id)
                time.sleep(delay)
                
            except Exception as e:
                state.consecutive_fails += 1
                log_msg(f'Error: {str(e)[:50]}', task_id)
                
                if state.consecutive_fails > 100:
                    log_msg('6+ hours failed. Stopping...', task_id)
                    update_status(task_id, state.msg_count, False, 'failed_6h')
                    return
                
                time.sleep(5)
        
        log_msg(f'Task completed. Total: {state.msg_count} messages', task_id)
        update_status(task_id, state.msg_count, False, 'stopped')
        
    except Exception as e:
        log_msg(f'Fatal: {str(e)[:100]}', task_id)
        update_status(task_id, state.msg_count if 'state' in locals() else 0, False, 'failed')
    
    finally:
        if task_id in RUNNING_TASKS:
            del RUNNING_TASKS[task_id]

# ==================== TASK MANAGER ====================

def task_manager():
    """Main task manager loop"""
    logger.info(f"Task manager started - Bot Hosting URL: {BOT_HOSTING_URL}")
    
    # On restart, notify bot hosting to send all active tasks
    notify_restart()
    
    previous_task_ids = set()
    
    while True:
        try:
            tasks = fetch_active_tasks()
            current_task_ids = {t['id'] for t in tasks}
            
            for task in tasks:
                if task['id'] not in RUNNING_TASKS:
                    logger.info(f"Starting task: {task['task_name']} ({task['id'][:8]})")
                    thread = threading.Thread(target=send_task, args=(task,), daemon=True)
                    thread.start()
            
            stopped_ids = previous_task_ids - current_task_ids
            for task_id in stopped_ids:
                if task_id in RUNNING_TASKS:
                    RUNNING_TASKS[task_id].running = False
                    logger.info(f"Stopped task: {task_id[:8]}")
            
            previous_task_ids = current_task_ids
            
            logger.info(f"Active: {len(RUNNING_TASKS)}, Messages: {sum(s.msg_count for s in RUNNING_TASKS.values())}")
            
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Task manager error: {str(e)}")
            time.sleep(10)

# ==================== MAIN ====================

if __name__ == '__main__':
    logger.info(f"""
╔════════════════════════════════════════════════════╗
║   DARKSTAR E2EE - STREAMLIT BACKGROUND WORKER     ║
║   Bot Hosting URL: {BOT_HOSTING_URL:<32} ║
║   Keep-Alive: ENABLED (30s interval)             ║
║   Restart Recovery: ENABLED                      ║
║   No UI - Background Automation Only             ║
╚════════════════════════════════════════════════════╝
    """)
    
    # Start keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    try:
        task_manager()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        close_driver()
        exit(0)
