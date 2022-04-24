import os
import sys
import glob
import json
import logging
import zipfile
import shutil
from zipfile import ZipFile
from urllib.request import urlretrieve

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()

def get_dependencies(dependencies):
    if os.path.isdir('.cache'):
        logger.info(f'clearing .cache')
        files = glob.glob('.cache/*.zip')
        for f in files:
            os.remove(f)
    else:
        logger.info(f'creating .cache')
        os.mkdir('.cache')

    for dependency in dependencies:
        dst_path = f'.cache/{dependency["name"]}'
        dst_zip = dst_path+'.zip'

        if 'local' in dependency:
            src_path = dependency['local']
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            elif zipfile.is_zipfile(src_path):
                shutil.copyfile(src_path, dst_zip)
                with ZipFile(dst_zip) as f:
                    logger.info(f'extracting {dst_zip}')
                    f.extractall(dst_path)
        elif 'url' in dependency:
            url = dependency["url"]
            extensions = ['']
            success = False
            if 'github.com' in url and not url.endswith('.zip'):
                extensions.append('/archive/master.zip')
                extensions.append('/archive/main.zip')

            for ext in extensions:
                logger.info(f'Attempting to retrieve {dependency["name"]} from {url+ext}')
                urlretrieve(url+ext, dst_zip)
                if zipfile.is_zipfile(dst_zip):
                    with ZipFile(dst_zip) as f:
                        logger.info(f'extracting {dst_zip}')
                        f.extractall(dst_path)
                    success = True
                    break
            if not success:
                raise RuntimeError(f'Failed to retrieve dependency {dependency["name"]}. Check the url and try again.')
        else:
            raise RuntimeError(f'{dependency["name"]} does not have a url or path field.')

def install_dependencies(install_path, namespaces, dependencies):
    if isinstance(namespaces, str):
        namespaces = [namespaces]
    cleaned_dirs = []
    cleaned_files = []
    for dependency in dependencies:
        path = f'.cache/{dependency["name"]}'
        dp_path = path
        if 'path' in dependency and len(dependency['path']) > 0:
            dp_path = path + '/' + dependency['path']
            if not os.path.isdir(dp_path):
                dirs = os.listdir(path)
                dp_path = f'{path}/{dirs[0]}/{dependency["path"]}'
                if not os.path.isdir(dp_path):
                    raise RuntimeError(f'Told to search for datapack at {dp_path}, but that isn''t a directory!')

        queue = [dp_path]
        found_directory = False
        while len(queue) > 0:
            current_path = queue[0]
            queue.remove(queue[0])

            if current_path.endswith('/data'):
                dp_path = current_path
                found_directory = True
                break
            else:
                for dir in os.listdir(current_path):
                    new_path = f'{current_path}/{dir}'
                    if os.path.isdir(new_path):
                        queue.append(new_path)

        if not found_directory:
            raise RuntimeError(f'failed to locate data directory at {dp_path}')
        logger.info(f'located data directory at {dp_path}')

        top_dirs = os.listdir(dp_path)
        for dir in top_dirs:
            clean_path = install_path + '/' + dir
            if dir not in namespaces and dir not in cleaned_dirs and os.path.isdir(clean_path):
                logger.info(f'cleaning {clean_path}')
                shutil.rmtree(clean_path)
                cleaned_dirs.append(dir)
        
        for dir in top_dirs:
            files = glob.glob('**/*.*', recursive=True, root_dir=f'{dp_path}/{dir}')
            for f in files:
                src_path = f'{dp_path}/{dir}/{f}'
                dst_path = f'{install_path}/{dir}/{f}'

                if os.path.isfile(dst_path):
                    if dir in namespaces and src_path not in cleaned_files:
                        logging.info(f'Cleaning file {dst_path}')
                        os.remove(dst_path)
                        copy_file(src_path, dst_path)
                    elif src_path.endswith('.json'):
                        merge_function_tags(src_path, dst_path)
                    else:
                        logger.warning(f'File {dst_path} already exists. Skipping.')
                elif os.path.isfile(src_path):
                    copy_file(src_path, dst_path)

def append_function_tags(dir_path, tags):
    if tags is None:
        return
    
    for tag in tags:
        split = tag['tag'].split(':')
        path = f'{dir_path}/{split[0]}/tags/functions/{split[1]}.json'
        merge_into_function_tag(path, tag['value'])
    
def get_optional(dict, entry):
    if entry in dict:
        return dict[entry]
    else:
        return None

def copy_file(src, dst):
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    except PermissionError:
        logger.warning(f'Failed to copy file {src} to {dst} - PermissionError')

def merge_function_tags(src, dst):
    logger.info(f'merging {src} into {dst}')
    assert os.path.isfile(src) and os.path.isfile(dst) and src != dst
    merge = ''
    with open(src, 'r') as f_src:
        with open(dst, 'r') as f_dst:
            src_contents = json.loads(f_src.read())
            dst_contents = json.loads(f_dst.read())
            for entry in src_contents['values']:
                if entry not in dst_contents['values']:
                    dst_contents['values'].append(entry)
            merge = json.dumps(dst_contents)
    with open(dst, 'w') as f_dst:
        f_dst.write(merge)

def merge_into_function_tag(path, value):
    logger.info(f'merging {value} into {path}')
    assert os.path.isfile(path)
    merge = ''
    with open(path, 'r') as f:
        contents = json.loads(f.read())
        if value not in contents['values']:
            contents['values'].append(value)
        merge = json.dumps(contents)
    with open(path, 'w') as f_dst:
        f_dst.write(merge)

def main(path):
    try:
        file = open(path, 'r')
    except:
        print(f'Unable to locate file {path}')
        return
    
    dependencies_json = json.loads(file.read())
    logger.debug(f'dependencies file: {dependencies_json}')

    print('Attempting to download dependencies...')
    get_dependencies(dependencies_json['dependencies'])
    print('All dependencies successfully downloaded.')

    print('Installing dependencies...')
    dir_path = path[:path.rfind('/')] + '/data'
    install_dependencies(dir_path, get_optional(dependencies_json, 'namespaces'), dependencies_json['dependencies'])
    print('All dependencies installed.')

    print('Appending function tags...')
    append_function_tags(dir_path, get_optional(dependencies_json,'append_function_tags'),)
    print('Finished. Build successful.')

if __name__ == "__main__":
    if len(sys.argv) == 1:
        path = "dependencies.json"
    else:
        path = sys.argv[1]
        if not path.endswith("dependencies.json"):
            path += "/dependencies.json"
    try:
        main(path)
    except Exception as e:
        logger.error(e)
