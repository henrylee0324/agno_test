import os
import fnmatch

def load_gitignore(directory):
    """讀取 .gitignore 檔案並解析忽略的目錄與檔案規則"""
    gitignore_path = os.path.join(directory, ".gitignore")
    ignored_patterns = set()
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # 跳過空行與註解
                    ignored_patterns.add(line)
    
    return ignored_patterns

def is_ignored(path, ignored_patterns, root_directory):
    """判斷路徑是否符合 .gitignore 規則"""
    rel_path = os.path.relpath(path, root_directory)  # 轉換成相對路徑
    for pattern in ignored_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
    return False

def list_project_structure(directory, indent="", ignored_patterns=None, root_directory=None, output_lines=None):
    """遞迴列出專案目錄的結構，根據 .gitignore 忽略對應的資料夾與檔案"""
    if ignored_patterns is None:
        ignored_patterns = load_gitignore(directory)  # 讀取 .gitignore 規則
        root_directory = directory  # 記住根目錄
        output_lines = []

    try:
        items = sorted(item for item in os.listdir(directory) 
                       if item != "__pycache__" and not is_ignored(os.path.join(directory, item), ignored_patterns, root_directory))
    except PermissionError:
        output_lines.append(indent + "[權限不足]")
        return output_lines

    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        is_last = index == len(items) - 1
        prefix = "└── " if is_last else "├── "
        output_lines.append(indent + prefix + item)

        if os.path.isdir(path):
            new_indent = indent + ("    " if is_last else "│   ")
            list_project_structure(path, new_indent, ignored_patterns, root_directory, output_lines)

    return output_lines

if __name__ == "__main__":
    project_dir = "./"  # 使用當前工作目錄
    structure_output = list_project_structure(project_dir)
    
    output_file = "project_structure.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(structure_output))
    
    print(f"專案結構已輸出到 {output_file}")