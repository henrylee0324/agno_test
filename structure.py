import os

def list_project_structure(directory, indent=""):
    """遞迴列出專案目錄的結構，並跳過 __pycache__。"""
    try:
        items = sorted(item for item in os.listdir(directory) if item != "__pycache__")
    except PermissionError:
        print(indent + "[權限不足]")
        return
    
    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        is_last = index == len(items) - 1
        prefix = "└── " if is_last else "├── "
        print(indent + prefix + item)
        
        if os.path.isdir(path):
            new_indent = indent + ("    " if is_last else "│   ")
            list_project_structure(path, new_indent)

if __name__ == "__main__":
    project_dir = "./tools"  # 使用當前工作目錄
    print(project_dir)
    list_project_structure("./tools")
