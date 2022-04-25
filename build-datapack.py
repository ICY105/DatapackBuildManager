import os
import sys
import glob
import json
import logging
import zipfile
import shutil
from zipfile import ZipFile
from urllib.request import urlretrieve

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
logger = logging.getLogger()

file_name = 'dependencies.json'
help_text="""
build-datapack.py will install dependencies into a datapack based on a provided
dependencies.json file (see git repo for reference). This file goes in the
same folder as your pack.mcmeta.

Ussage:
    build-datapack.py <path> <flags...>

Path:
    Accepts top-level datapack path, or path to dependencies.json

Flags:
    -h --help: prints this message
    -c --clean: removes installed dependencies without re-installing them. 
                It's recommended to run this before removing a dependency.
    -l --local: skips grabbing step, building from anything left in the cache
    -t --no-tags: skips appending function tags step
"""

def get_dependencies(dependencies):
    """
    Copies dependency files into the .cache directory, downloading from a url
    if needed and extracts zip files.
    :param dependencies: list of dependencies to install, from dependencies.json
    """
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
                    success = True
                    break
            if not success:
                raise RuntimeError(f'Failed to retrieve dependency {dependency["name"]}. Check the url and try again.')
        else:
            raise RuntimeError(f'{dependency["name"]} does not have a url or path field.')

        if zipfile.is_zipfile(dst_zip):
            with ZipFile(dst_zip) as f:
                logger.info(f'extracting {dst_zip}')
                f.extractall(dst_path)

def find_dp_paths(dependencies):
    """
    Locates the '/data' folder for dependencies.
    :param dependencies: list of dependencies from dependencies.json
    """
    paths = []
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
            raise RuntimeError(f"failed to locate '/data' directory at {dp_path}")

        logger.info(f'located data directory at {dp_path}')
        paths.append(dp_path)
    return paths

def clean_dependencies(dp_paths, install_path, namespaces):
    """
    Removes existing dependencies at install location
    :param dp_paths: list of paths to copy from
    :param install_path: path to copy to
    :namespaces: list of protected namespaces
    """
    if isinstance(namespaces, str):
        namespaces = [namespaces]
    cleaned_dirs = []
    
    for dp_path in dp_paths:
        top_dirs = os.listdir(dp_path)
        for dir in top_dirs:
            clean_path = install_path + '/' + dir
            if dir not in namespaces and dir not in cleaned_dirs and os.path.isdir(clean_path):
                logger.info(f'cleaning {clean_path}')
                shutil.rmtree(clean_path)
                cleaned_dirs.append(dir)

def install_dependencies(dp_paths, install_path, namespaces):
    """
    Installs dependencies by copying files and merging where pratical
    :param dp_paths: list of paths to copy from
    :param install_path: path to copy to
    :namespaces: list of protected namespaces
    """
    if isinstance(namespaces, str):
        namespaces = [namespaces]
    cleaned_files = []
    
    for dp_path in dp_paths:
        top_dirs = os.listdir(dp_path)
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
                        merge_tag_files(src_path, dst_path)
                    else:
                        logger.warning(f'File {dst_path} already exists. Skipping.')
                elif os.path.isfile(src_path):
                    copy_file(src_path, dst_path)

def append_tag_files(dir_path, tags):
    """
    Appends provided values to tags.
    :param dir_path: path of '/data' folder containing tags
    :param tags: list of tag:value pairs from dependencies.json
    """
    if tags is None:
        return
    
    for tag in tags:
        split = tag['tag'].split(':')
        path = f'{dir_path}/{split[0]}/tags/functions/{split[1]}.json'
        append_tag_file(path, tag['value'])

def merge_tag_files(src, dst):
    """ Appends a single line value to a tag
        :param path: file to append (must be a tag file, like function tags)
        :param value: value to append (example, 'my_datapack:load')
    """
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

def append_tag_file(path, value):
    """ Appends a single line value to a tag
        :param path: file to append (must be a tag file, like function tags)
        :param value: value to append (example, 'my_datapack:load')
    """
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

def has_tag(short, long):
    return short in sys.argv or long in sys.argv

def main(path):
    with open(f'{path}/{file_name}', 'r') as f:
        dependencies_json = json.loads(f.read())
        logger.debug(f'dependencies file: {dependencies_json}')
        dir_path = path[:path.rfind('/')] + '/data'

        # Step 1: copy/download/extract dependencies to cache
        if not has_tag('-l', '--local'):
            print('Grabbing dependencies...')
            get_dependencies(dependencies_json['dependencies'])

        # Step 2: find dependency datapack paths
        dependency_paths = find_dp_paths(dependencies_json['dependencies'])

        # Step 3: clean existing dependencies
        print('Cleaning dependencies...')
        clean_dependencies(dependency_paths, dir_path, get_optional(dependencies_json, 'namespaces'))

        if not has_tag('-c', '--clean'):
            # Step 4: install dependencies
            print('Installing dependencies...')
            install_dependencies(dependency_paths, dir_path, get_optional(dependencies_json, 'namespaces'))

            # Step 5: Append to function tags
            if not has_tag('-t', '--no-tags'):
                print('Appending function tags...')
                append_tag_files(dir_path, get_optional(dependencies_json,'append_function_tags'))

        print('Finished. Build successful.')

if __name__ == "__main__":
    if has_tag('-h', '--help') or len(sys.argv) == 1:
        print(help_text)
    else:
        path = sys.argv[1]
        if path.endswith(file_name):
            path = path[:-len(file_name)]
        try:
            main(path)
        except Exception as e:
            logger.error(e)
