import json
import os
from pathlib import Path

# ========== 配置 ==========
INPUT_JSON = 'messages_with_local_paths.json'
OUTPUT_HTML = 'report.html'
IMAGE_DIR = 'downloaded_images'

def main():
    if not os.path.exists(INPUT_JSON):
        print(f"❌ 找不到 {INPUT_JSON}，请先运行 extract_and_download_images.py")
        return

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    # 开始构建 HTML
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>消息图文报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }
        .message { 
            background: white; 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 16px; 
            margin-bottom: 20px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .id-time { color: #666; font-size: 0.9em; margin-bottom: 8px; }
        .text { margin: 10px 0; line-height: 1.5; }
        .images { margin-top: 10px; }
        .images img { 
            max-width: 300px; 
            height: auto; 
            margin: 5px; 
            border: 1px solid #eee; 
            border-radius: 4px;
        }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>消息图文报告</h1>
'''

    for msg in messages:
        text = msg.get('text', '').replace('\n', '<br>')
        createtime = msg.get('createtime', '未知时间')
        msg_id = msg.get('id', '未知ID')

        html += f'''
    <div class="message">
        <div class="id-time">ID: {msg_id} | 时间: {createtime}</div>
        <div class="text">{text}</div>
'''

        local_paths = msg.get('local_pic_paths', [])
        if local_paths:
            html += '        <div class="images">\n'
            for path in local_paths:
                # 转为相对路径（确保 HTML 能找到图片）
                rel_path = Path(path).as_posix()  # 保证是 / 而不是 \
                html += f'            <img src="{rel_path}" alt="图片">\n'
            html += '        </div>\n'

        html += '    </div>\n'

    html += '''
</body>
</html>
'''

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML 报告已生成: {OUTPUT_HTML}")
    print("💡 请用浏览器打开查看图文内容。")

if __name__ == '__main__':
    main()