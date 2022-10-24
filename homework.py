import sys
from pathlib import Path
import shutil
import re


image = []
video = []
documents = []
music = []
archives = []
unknown = []

extensions_dict = {
image: ['JPEG', 'PNG', 'JPG', 'SVG'],
video: ['AVI', 'MP4', 'MOV', 'MKV'],
documents: ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
music: ['MP3', 'OGG', 'WAV', 'AMR'],
archives: ['ZIP', 'GZ', 'TAR']
}

folders = []
file_extensions = set()
unknown_file_extensions = set()

def scan_folder(folder: Path) -> None:
    for item in folder.iterdir():
        if  item.is_dir():
            if item.name not in ('image', 'video', 'documents', 'music', 'archives', 'unknown'):
                folders.append(item)
                scan_folder(item)
            continue

        else:
            fullname = folder / item.name
            suf = Path(item.name).suffix[1:].upper()
            if not suf:
                unknown.append(fullname)
            else:
                for name_folder in extensions_dict:
                    if suf in extensions_dict[name_folder]:
                        file_extensions.add(suf)
                        name_folder.append(fullname)
                    else:
                        unknown_file_extensions.add(suf)
                        unknown.append(fullname)
            
cyrillic_symbols = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
translate = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

TRANS = {}
for c, l in zip(cyrillic_symbols, translate):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()

def normalize(name: str) -> str:
    trans_name = name.translate(TRANS)
    trans_name = re.sub(r'\W', '_', trans_name)
    return trans_name

def handle_file(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.stem) + filename.suffix)

def handle_archive(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()),
                              str(folder_for_file.resolve()))
    except shutil.ReadError:
        print(f'Це не архів {filename}!')
        folder_for_file.rmdir()
        return None
    filename.unlink()

def handle_folder(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        print(f'Помилка видалення папки {folder}')

def main(folder: Path):
    scan_folder(folder)
    for file in image:
        handle_file(file, folder / 'images')
    for file in video:
        handle_file(file, folder / 'video')
    for file in documents:
        handle_file(file, folder / 'documents')
    for file in music:
        handle_file(file, folder / 'music')
    for file in archives:
        handle_archive(file, folder / 'archives')
    for file in unknown:
        handle_file(file, folder / 'unknown')
  
    for folder in folders[::-1]:
        handle_folder(folder)

if __name__ == '__main__':
    if sys.argv[1]:
        folder_for_scan = Path(sys.argv[1])
        print(f'Start in folder {folder_for_scan.resolve()}')
        main(folder_for_scan.resolve())
