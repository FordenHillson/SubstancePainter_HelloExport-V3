import os
import urllib.request
import urllib.error
import json
import zipfile
import tempfile
import shutil

REPO_OWNER = "FordenHillson"
REPO_NAME = "SubstancePainter_HelloExport-V3"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"

def get_plugin_folder():
    return os.path.dirname(os.path.abspath(__file__))

def get_download_url(tag_name):
    return f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/tags/{tag_name}.zip"

def parse_version(version_str):
    try:
        parts = version_str.lstrip('v').split('.')
        return tuple(int(p) for p in parts)
    except:
        return (0, 0, 0)

def compare_versions(v1, v2):
    p1 = parse_version(v1)
    p2 = parse_version(v2)
    if p1 < p2:
        return -1
    elif p1 > p2:
        return 1
    return 0

def fetch_github_releases():
    try:
        req = urllib.request.Request(
            API_URL,
            headers={"User-Agent": "SubstancePainter-HelloExport-Plugin"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            releases = []
            for item in data:
                tag = item.get("tag_name", "")
                date = item.get("published_at", "")[:10] if item.get("published_at") else ""
                zip_url = item.get("zipball_url", "")
                if tag and zip_url:
                    releases.append({"tag": tag, "date": date, "zip_url": zip_url})
            return releases
    except Exception as e:
        print(f"Failed to fetch releases: {e}")
        return []

def check_for_updates(current_version):
    releases = fetch_github_releases()
    if not releases:
        return (False, None, None, [])
    
    latest = releases[0]
    has_update = compare_versions(current_version, latest["tag"]) < 0
    
    return (has_update, latest["tag"], latest, releases)

def download_and_extract(zip_url, target_folder, version_tag=None):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "update.zip")
    
    try:
        req = urllib.request.Request(
            zip_url,
            headers={"User-Agent": "SubstancePainter-HelloExport-Plugin"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            with open(zip_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            root_folder = zf.namelist()[0]
            for member in zf.namelist():
                if member == root_folder:
                    continue
                member_path = os.path.join(target_folder, member[len(root_folder):])
                if member.endswith('/'):
                    os.makedirs(member_path, exist_ok=True)
                else:
                    parent = os.path.dirname(member_path)
                    if parent and not os.path.exists(parent):
                        os.makedirs(parent, exist_ok=True)
                    with zf.open(member) as source, open(member_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
        
        if version_tag:
            version_str = version_tag.lstrip('v')
            version_file = os.path.join(target_folder, "version.txt")
            with open(version_file, 'w') as f:
                f.write(version_str)
        
        return True
    except Exception as e:
        print(f"Download/extraction failed: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def get_current_version_from_file():
    version_file = os.path.join(get_plugin_folder(), "version.txt")
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as f:
                return f.read().strip()
        except:
            pass
    return None