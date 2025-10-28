import json
import os
import re
import requests
from urllib.parse import urlparse
import csv
from pathlib import Path
import mimetypes
import hashlib

# ========== 配置 ==========
INPUT_JSON = 'xhr_data.json'          # 你的原始 XHR 数据文件
OUTPUT_DIR = 'downloaded_images'     # 图片保存目录
OUTPUT_JSON = 'messages_with_local_paths.json'
OUTPUT_CSV = 'messages.csv'

# 创建图片目录
Path(OUTPUT_DIR).mkdir(exist_ok=True)


def get_ext_from_url_or_content_type(url, content_type=''):
    """尽量从 URL 或 Content-Type 推断扩展名"""
    # 方法1: 从 URL 中找
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path:
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            return ext
    # 方法2: 从 Content-Type 推断
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(';')[0])
        if ext:
            return ext
    # 默认
    return '.jpg'

def download_image(url, folder):
    try:
        url = url.strip()
        if not url:
            return None
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 获取扩展名
        content_type = response.headers.get('content-type', '')
        ext = get_ext_from_url_or_content_type(url, content_type)

        # 生成唯一文件名：用 URL 的 hash 避免冲突
        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        filename = f"img_{url_hash}{ext}"
        local_path = os.path.join(folder, filename)

        # 如果已存在，说明已下载（可选：也可强制覆盖）
        if os.path.exists(local_path):
            return local_path

        with open(local_path, 'wb') as f:
            f.write(response.content)
        return local_path

    except Exception as e:
        print(f"⚠️ 下载失败 {url[:50]}...: {e}")
        return None
# ========== 主处理逻辑 ==========
def main():
    # 1. 读取原始数据
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    all_messages = []

    # 2. 遍历所有 XHR 响应
    for item in raw_data:
        if 'data' in item and 'list' in item['data']:
            for msg_item in item['data']['list']:
                raw_msg_str = msg_item.get('msg', '')
                createtime = msg_item.get('createtime')
                msg_id = msg_item.get('id')

                # 3. 解析嵌套的 msg 字符串
                try:
                    content_parts = json.loads(raw_msg_str)
                except json.JSONDecodeError:
                    # 尝试用正则修复（如截取最外层 [...]）
                    match = re.search(r'^\s*(\[.*\])', raw_msg_str)
                    if match:
                        try:
                            content_parts = json.loads(match.group(1))
                        except:
                            continue
                    else:
                        continue

                texts = []
                remote_urls = []
                local_paths = []

                # 4. 提取文本和图片 URL
                for part in content_parts:
                    if part.get('type') == 'text':
                        text = part.get('msg', '').strip()
                        if text:
                            texts.append(text)
                    elif part.get('type') == 'pic':
                        url = part.get('url', '').strip()
                        if url:
                            remote_urls.append(url)

                # 5. 下载图片
                for url in remote_urls:
                    local_path = download_image(url, OUTPUT_DIR)
                    if local_path:
                        local_paths.append(local_path)

                # 6. 保存结构化消息
                all_messages.append({
                    'id': msg_id,
                    'createtime': createtime,
                    'text': '\n'.join(texts),
                    'remote_pic_urls': remote_urls,
                    'local_pic_paths': local_paths
                })

    # 7. 保存结果
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_messages, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'createtime', 'text', 'remote_pic_urls', 'local_pic_paths'
        ])
        writer.writeheader()
        for m in all_messages:
            writer.writerow({
                'id': m['id'],
                'createtime': m['createtime'],
                'text': m['text'].replace('\n', ' ').replace('\r', ' '),
                'remote_pic_urls': '; '.join(m['remote_pic_urls']),
                'local_pic_paths': '; '.join(m['local_pic_paths'])
            })

    print(f"✅ 处理完成！")
    print(f"   - 消息总数: {len(all_messages)}")
    print(f"   - 图片保存目录: ./{OUTPUT_DIR}/")
    print(f"   - 结构化数据: {OUTPUT_JSON}, {OUTPUT_CSV}")

if __name__ == '__main__':
    main()