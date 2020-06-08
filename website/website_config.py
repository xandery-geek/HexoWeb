import yaml
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBSITE_BASE_PATH = os.path.join(BASE_DIR, '../user_website')
WEBSITE_TEMPLATE_PATH = os.path.join(BASE_DIR, 'template/website/blog')
THEME_TEMPLATE_PATH = os.path.join(BASE_DIR, 'template/theme')
SCRIPT_PATH = os.path.join(BASE_DIR, 'website/script')


def get_website_dir(user_id, website_id):
    user_dir = '%04d' % user_id
    website_dir = 'blog{}'.format(website_id)
    dst_path = os.path.join(WEBSITE_BASE_PATH, user_dir)
    dst_path = os.path.join(dst_path, website_dir)
    return dst_path


def create_website(path):
    if not os.path.exists(path):
        os.makedirs(path)

    if os.system('cp -r ' + WEBSITE_TEMPLATE_PATH + '/* ' + path) == 0:
        return True
    else:
        return False


def delete_website(path):
    if os.path.exists(path):
        os.system('rm -r ' + path)


def update_website_config(path, website):
    config_file = os.path.join(path, '_config.yml')

    try:
        with open(config_file, 'r') as f:
            y = yaml.safe_load(f)

        y['title'] = website.title
        y['subtitle'] = website.subtitle
        y['author'] = website.author
        y['url'] = website.url
        y['description'] = website.desc
        y['keywords'] = website.keyword
        y['index_generator']['per_page'] = website.per_page
        y['deploy']['repo'] = website.repository
        y['deploy']['branch'] = website.branch
        y['theme'] = website.cur_theme

        with open(config_file, 'w') as f:
            yaml.safe_dump(y, f, sort_keys=False, default_flow_style=False, encoding='utf-8', allow_unicode=True)
    except FileNotFoundError:
        return False
    return True


def deploy_website(path):
    script_file = os.path.join(SCRIPT_PATH, 'deploy.sh')
    command = "bash {} {}".format(script_file, path)
    return os.system(command) == 0


def change_theme(path, theme):
    config_file = os.path.join(path, '_config.yml')

    try:
        with open(config_file, 'r') as f:
            y = yaml.safe_load(f)

        y['theme'] = theme

        with open(config_file, 'w') as f:
            yaml.safe_dump(y, f, sort_keys=False, default_flow_style=False, encoding='utf-8', allow_unicode=True)
    except FileNotFoundError:
        return False
    return True
