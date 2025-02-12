import os 
import platform
import sys
import shutil
import subprocess
import tempfile
import psutil
import atexit
import uuid
import builtins
import inspect

from pathlib import Path
from typing import Optional, Set

from agno.utils.log import logger

def get_sandbox_code(user_script_path):
    # 讀取白名單模組
    whitelist_path = Path(__file__).parent / "agent_lib.txt"

    allowed_modules = load_allowed_modules(whitelist_path)
    # 例如有些內部函式可固定加入
    allowed_modules.add("safe_info")

    # 示範性的 blocked_modules（可自行調整）
    blocked_modules = {
        'os', 'subprocess', 'builtins', 'importlib', 
        'ctypes', 'pty', 'socket', 'pickle', 'marshal'
    }
    # 如果某些函式庫內部要用到 sys，就不要在這裡封鎖
    
    # 讀取白名單模組（你原有的邏輯）
    whitelist_path = Path(__file__).parent / "agent_lib.txt"
    allowed_modules = load_allowed_modules(whitelist_path)
    # 例如有些內部函式可固定加入
    allowed_modules.add("safe_info")
    # 示範性的 blocked_modules（可自行調整）
    blocked_modules = {
        'os', 'subprocess', 'builtins', 'importlib', 
        'ctypes', 'pty', 'socket', 'pickle', 'marshal'
    }
    
    # 這裡我們不替換整個 os、pathlib 模組，而只覆寫
    # os.path.expanduser 與 pathlib.Path.home 函式，利用 call stack 判斷來源。
    sandbox_code = f"""
import builtins, inspect
import os
import pathlib

# 記錄使用者程式碼路徑，用以判斷呼叫來源
USER_SCRIPT_PATH = r"{user_script_path}"

# 保存原始函式
_original_expanduser = os.path.expanduser
_original_home = pathlib.Path.home

def safe_expanduser(path):
    s = str(path)
    import inspect
    # 如果呼叫堆疊中出現使用者程式碼檔案，則回傳假家目錄
    if any(USER_SCRIPT_PATH in frame.filename for frame in inspect.stack()):
        if path == "~" or s.startswith("~/"):
            return s.replace("~", "/home/sandbox", 1)
    # 否則使用原始函式
    return _original_expanduser(s)

def safe_home():
    import inspect
    if any(USER_SCRIPT_PATH in frame.filename for frame in inspect.stack()):
        return pathlib.Path("/home/sandbox")
    return _original_home()

# 將這兩個函式掛在原模組上
os.path.expanduser = safe_expanduser
# 注意：Path.home 是 class method，故用 staticmethod 包裝
pathlib.Path.home = staticmethod(safe_home)

# 以下為原有的 sandbox 限制措施（例如限制內建函式、封鎖敏感模組）
# 建立 restricted builtins，並覆寫 __import__ 等：
_original_import = builtins.__import__
def _is_from_user_code():
    import inspect
    return any(USER_SCRIPT_PATH in frame.filename for frame in inspect.stack())

def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    if _is_from_user_code():
        mod_base = name.split(".")[0]
        if mod_base in {blocked_modules} and mod_base not in {allowed_modules}:
            raise ImportError(f"模組 '{{name}}' 出於安全考量已被禁用")
    return _original_import(name, globals, locals, fromlist, level)

def _guarded_function_factory(func_name):
    def _wrapped(*args, **kwargs):
        if _is_from_user_code():
            raise NameError(f"'{{func_name}}' is not allowed")
        return getattr(builtins, func_name)(*args, **kwargs)
    return _wrapped

restricted_builtins = dict(builtins.__dict__)
for sensitive in ['exec', 'eval', 'compile']:
    restricted_builtins[sensitive] = _guarded_function_factory(sensitive)
restricted_builtins['open'] = _guarded_function_factory('open')
restricted_builtins['__import__'] = restricted_import

# 建立 restricted_globals 供 user code 執行
restricted_globals = {{
    '__builtins__': restricted_builtins,
    '__name__': '__main__',
    '__file__': USER_SCRIPT_PATH,
}}

# --- 讀取並編譯使用者程式碼 ---
with open(USER_SCRIPT_PATH, 'rb') as f:
    user_code = compile(f.read(), USER_SCRIPT_PATH, 'exec')

# 最後，執行使用者程式碼
exec(user_code, restricted_globals, restricted_globals)
"""
    return sandbox_code

def load_allowed_modules(whitelist_path: Path) -> Set[str]:
    """
    從 agent_lib.txt 中讀取白名單模組列表
    每行格式如：numpy==1.0.1
    返回模組名稱集合，例如 {'numpy', 'pandas', ...}
    """
    allowed = set()
    try:
        with whitelist_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # 只取模組名稱部分（以 '==' 為分隔）
                parts = line.split("==")
                module_name = parts[0].strip()
                if module_name:
                    allowed.add(module_name)
    except Exception as e:
        logger.error(f"讀取白名單失敗: {e}", exc_info=True)
    return allowed

class VenvPythonExecutor:
    """A Python code executor using lightweight isolation with a whitelist for safe libraries.
    
    透過沙盒機制限制敏感模組與函數，
    同時允許 agent 透過白名單讀取正常第三方庫（例如 numpy、pandas 等）。

    改寫重點：
    - 由原來「雙層 venv」改成「單層 venv」，直接使用當前環境 (sys.executable) 作為執行環境。
    - 其他沙盒防護措施（例如覆寫 builtins 與 __import__）維持不變。
    """
    def __init__(self,
                 venv_dir: Optional[Path] = None,
                 work_dir: Optional[Path] = None):
        self.is_windows = platform.system() == 'Windows'
        # 單層 venv 下，不額外建立 venv 目錄，僅用來記錄（可作 log 或暫存檔案用）
        self.venv_dir = venv_dir or Path(tempfile.mkdtemp(prefix='py_single_env_'))
        self.work_dir = work_dir or Path.cwd()
        self.active_processes: Set[int] = set()
        # 如果 agent_lib.txt 與此檔案在同一目錄，調整路徑
        
        logger.debug(f"初始化執行器: windows={self.is_windows}, venv_dir={self.venv_dir}, work_dir={self.work_dir}")
        
        self.work_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"工作目錄: {self.work_dir}")
        atexit.register(self._cleanup_resources)

    def run_file(self,
                 file_path: Path,
                 variable_to_return: Optional[str] = None) -> tuple[bool, str]:
        """
        Execute a Python file in an isolated environment with dynamic defenses.
        Args:
            file_path: Path to the Python file to execute.
            variable_to_return: Optional variable name to return after execution.
        Returns:
            tuple[bool, str]: (success, output or error message)
        """
        try:
            self._cleanup_resources()
            # 單層 venv: 直接採用當前 Python 執行檔，不建立新的虛擬環境
            python_executable = self._prepare_venv()
            success, output = self._execute_in_venv(
                python_executable,
                file_path,
                variable_to_return
            )
            return success, output
        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            return False, str(e)
        finally:
            self._cleanup_resources()

    def _create_safe_env(self) -> dict:
        """建立安全的環境變數"""
        logger.debug("建立安全的環境變數")
        # 可以視需求維持 PATH 或部分環境變數；這裡示範僅帶入一些必備的變數
        return {
            'PATH': os.environ.get('PATH', ''),
            'PYTHONNOUSERSITE': '1',
            'PYTHONDONTWRITEBYTECODE': '1',
            'PYTHONUNBUFFERED': '1',
            'LANG': 'en_US.UTF-8'
        }
    
    def _prepare_venv(self) -> Path:
        """
        準備單層 venv 執行環境：
        不建立新的虛擬環境，而是直接回傳當前環境的 Python 執行檔路徑。
        """
        logger.debug("使用單層 venv：直接採用當前環境 (sys.executable)")
        return Path(sys.executable)

    def _execute_in_venv(self,
                         python_executable: Path,
                         script_path: Path,
                         variable_to_return: Optional[str] = None) -> tuple[bool, str]:
        """在單層環境中執行沙盒腳本"""
        try:
            sandbox_script = self._build_restriction_script(script_path)
            
            # 構建最小可行的執行環境
            minimal_env = {
                'HOME': '/home/sandbox',
                'PWD': str(self.work_dir),
                'LANG': 'zh_TW.UTF-8',
                'PATH': '/usr/local/bin:/usr/bin:/bin',
                'PYTHONDONTWRITEBYTECODE': '1',
                'PYTHONUNBUFFERED': '1'
            }
            if self.is_windows:
                minimal_env.update({
                    'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                    'TEMP': os.environ.get('TEMP', ''),
                    'TMP': os.environ.get('TMP', '')
                })

            # 此處直接使用傳入的 python_executable（單層 venv 下就是 sys.executable）
            python_bin = str(python_executable)
            logger.debug(f"使用執行環境 Python: {python_bin}")

            process = subprocess.run(
                [python_bin, '-E', str(sandbox_script)],
                env=minimal_env,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.work_dir
            )

            logger.debug(f"Return Code: {process.returncode}")
            logger.debug(f"STDOUT: {process.stdout}")
            logger.debug(f"STDERR: {process.stderr}")

            success = (process.returncode == 0)
            output = process.stdout if success else f"執行失敗:\n{process.stderr}"
            return success, output.strip()
        except subprocess.TimeoutExpired:
            logger.error("執行超時")
            return False, "執行超時"
        except Exception as e:
            logger.error(f"執行錯誤: {e}", exc_info=True)
            return False, str(e)

    def _build_restriction_script(self, user_script_path: Path) -> Path:
        """
        建立沙盒腳本：
        1. 建立 restricted_builtins：複製自內建 builtins.__dict__，僅在 user code 呼叫時阻擋敏感函式。
        2. 定義 restricted_import：只在 user code 試圖 import 封鎖名單模組時阻擋，其餘放行。
        3. 編譯並執行使用者程式碼 (user_script)，讓它以 restricted_builtins 為 __builtins__。
        """
        try:
            logger.debug(f"建立沙盒腳本: user_script={user_script_path}")

            sandbox_init = get_sandbox_code(user_script_path)

            temp_file = Path(tempfile.mktemp(prefix='sandbox_init_', suffix='.py'))
            logger.debug(f"儲存沙盒腳本: {temp_file}")
            temp_file.write_text(sandbox_init, encoding='utf-8')
            return temp_file
        except Exception as e:
            logger.error(f"建立限制腳本失敗: {e}", exc_info=True)
            raise

    def _cleanup_resources(self):
        """清理所有資源，包括子程序（單層 venv 下不刪除系統環境）"""
        logger.info("清理資源...")
        for pid in list(self.active_processes):
            try:
                process = psutil.Process(pid)
                process.terminate()
                self.active_processes.remove(pid)
            except psutil.NoSuchProcess:
                self.active_processes.remove(pid)
            except Exception as e:
                logger.error(f"終止進程 {pid} 失敗: {e}")
        # 單層 venv 下，不需要刪除 venv 目錄，只刪除我們產生的暫存檔（例如 sandbox_init_*.py）
        # 如果需要清理 self.venv_dir 裡的其他檔案，可根據需求調整
        try:
            if self.venv_dir and self.venv_dir.exists():
                shutil.rmtree(self.venv_dir, ignore_errors=True)
                logger.info(f"已清理暫存目錄: {self.venv_dir}")
        except Exception as e:
            logger.error(f"清理暫存目錄失敗: {e}")