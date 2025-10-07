import shutil
from pathlib import Path

print('开始清理...')

# 1. 清理 admin_data 目录 (保留 book 文件夹)
admin_data = Path('admin_data')
if admin_data.exists():
    for item in admin_data.iterdir():
        if item.name != 'book':
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                print(f'已删除 admin_data/{item.name}')
            except:
                pass

# 2. 删除 user_data 目录
user_data = Path('user_data')
if user_data.exists():
    shutil.rmtree(user_data)
    print('已删除 user_data')

# 3. 清理 Python 缓存
for pycache in Path('.').rglob('__pycache__'):
    shutil.rmtree(pycache)
    print(f'已删除 {pycache}')

for pyc in Path('.').rglob('*.pyc'):
    pyc.unlink()

print('清理完成')