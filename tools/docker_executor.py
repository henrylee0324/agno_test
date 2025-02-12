import docker
import ast
from pathlib import Path
from typing import Optional
from docker.errors import DockerException

from agno.utils.log import logger

class DockerPythonExecutor:
    """A Python code executor using Docker containers for isolation.
    
    This class provides functionality to safely execute Python code within Docker containers,
    with built-in security controls and resource limitations.
    
    Attributes:
        image_name: Docker image name to use for execution
        work_dir: Working directory for file operations
        containers: Set of active container IDs
        """
    FORBIDDEN_COMMANDS = frozenset({
    'system', 'popen', 'subprocess', 'pip', 'easy_install', 'pty'
})
    
    def __init__(self, 
                 image_name: str = "python_agent_env:1.0.0",
                 work_dir: Optional[Path] = None):

        self.client = docker.from_env()
        self.image_name = image_name
        self.work_dir = work_dir or Path.cwd()
        self.containers = set()  

        try:
            self.client.ping()
            logger.info("Docker 連線成功")
        except Exception as e:
            logger.error(f"Docker 連線失敗: {e}")
            raise
        
        logger.info(f"工作目錄: {self.work_dir}")
        logger.info(f"Docker Image: {self.image_name}")
        
        import atexit
        atexit.register(self._cleanup_containers)
    
    def run_file(self,
                file_path: Path,
                variable_to_return: Optional[str] = None) -> tuple[bool, str]:
        """Execute a Python file in a Docker container with safety checks.
    
        This method handles:
        1. Code validation
        2. Container creation and execution
        3. Result collection
        4. Container cleanup
        
        Args:
            file_path: Path to the Python file to execute
            variable_to_return: Optional variable name to return after execution
            
        Returns:
            tuple[bool, str]: A tuple containing:
                - bool: Execution success status
                - str: Output message or error description
        """
        try:
            self._cleanup_containers()

            # Validate
            self._validate_file(file_path)
            
            # Prepare
            container = self._create_container(file_path)
            
            # Execute
            success, output = self._execute_container(container)

            return success, output
            
        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            return False, str(e)
            
        finally:
            if container:
                self._cleanup_containers()
    
    # ====================== Private function  ======================


    def _validate_code(self, code: str) -> tuple[bool, str]:
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # 檢查 import 和 from import
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name in self.FORBIDDEN_COMMANDS:
                            return False, f"禁止匯入: {name.name}"
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.FORBIDDEN_COMMANDS:
                        return False, f"禁止匯入: {node.module}"
                
                # 檢查系統命令執行
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in self.FORBIDDEN_COMMANDS:
                            return False, f"禁止使用: {node.func.attr}"

            return True, "驗證通過"
                
        except SyntaxError as e:
            return False, f"語法錯誤: {str(e)}"
            
    def _validate_file(self, file_path: Path) -> bool:
        code = file_path.read_text()
        logger.info("Validating code safety...")
        
        is_valid, message = self._validate_code(code)
        if not is_valid:
            logger.error(f"程式碼驗證失敗: {message}")
            raise ValueError(f"驗證失敗: {message}")
            
    def _create_container(self, file_path: Path):
        try:
            container = self.client.containers.run(
                self.image_name,
                command=['python', f'/app/code/{file_path.name}'],
                volumes={
                    str(file_path.parent): {
                        'bind': '/app/code',
                        'mode': 'ro'
                    }
                },
                working_dir='/app/code',
                user='agent',
                security_opt=['no-new-privileges:true'],
                mem_limit='256m',
                cpu_quota=50000,
                cpu_period=100000,
                network_mode='none',
                detach=True
            )
            
            self.containers.add(container.id)
            logger.info(f"Container started: {container.id[:12]}")
            return container
            
        except docker.errors.DockerException as e:
            logger.error(f"Docker 操作錯誤: {e}")
            raise  

    def _execute_container(self, container) -> tuple[bool, str]:
        try:
            logger.info(f"開始執行容器: {container.id[:12]}")
            result = container.wait(timeout=45)
            success = result['StatusCode'] == 0
            output = container.logs().decode('utf-8').strip()

            if not success:
                logger.error(f"執行失敗: {output}")

            # 如果沒有輸出但執行成功
            if not output and success:
                logger.warning(f"容器 {container.id[:12]} 沒有產生任何輸出")
                
                container.reload()
                logger.debug(f"容器最後狀態: {container.status}")
                logger.debug(f"容器詳細資訊: {container.attrs}")
                
                inspect_result = container.client.api.inspect_container(container.id)
                logger.debug(f"容器檢查結果: {inspect_result['State']}")
                
                return True, "容器執行完成但無輸出"
            return success, output 
        except Exception as e:
            logger.error(f"容器執行錯誤: {e}")
            return False, str(e)

    def _cleanup_containers(self):
        logger.info("開始清理所有容器...")
        try:
            logger.info("開始清理已結束的容器...")
            
            # 只列出exited狀態的指定image容器
            containers = self.client.containers.list(
                all=True,
                filters={
                    "ancestor": self.image_name,
                    "status": ["exited"]  # 只清理已結束的
                }
            )
            
            cleaned_count = 0
            for container in containers:
                try:
                    logger.info(f"移除已結束容器: {container.id[:12]}")
                    container.remove()
                    cleaned_count += 1
                    
                except Exception as e:
                    logger.error(f"清理容器 {container.id[:12]} 時發生錯誤: {e}")
                    
            if cleaned_count:
                logger.info(f"清理完成,共清理 {cleaned_count} 個已結束容器")
                
        except Exception as e:
            logger.error(f"清理過程發生錯誤: {e}")
