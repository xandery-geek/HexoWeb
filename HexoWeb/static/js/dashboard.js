function get_cookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function goto_link(url) {
    window.location.href = url;
}

function get_n_parent(node, n) {
    let parent = node;
    for (let i=0; i<n; i++)
    {
        parent = parent.parentNode;
    }
    return parent;
}

function prevent_form_enter(event) {
    let keycode = event.which | event.keyCode;
    return keycode !== 13;
}

function ajax_post(url, form_data, success, error) {
    $.ajax({
            url: url,
            type: 'post',
            data: form_data,
            contentType: false,
            processData: false,
            cache: false,
            success: success,
            error: error
        }
    );
}

function ajax_get(url, success, error) {
    $.ajax({
            url: url,
            type: 'get',
            cache: false,
            success: success,
            error: error
        }
    );
}

const dropdown_class1 = 'blog-tri-down';
const dropdown_class2 = 'blog-tri-up';

function _change_dropdown_class(target, class_name) {
    let class_list = target.className;
    class_list = class_list.split(' ');
    class_list[0] = class_name;
    class_name = '';
    for(let c of class_list){
        class_name = class_name.concat(c + ' ');
    }
    target.className = class_name;
}


function change_dropdown_class(target, index, total) {
    let id = 'dropdown-btn';

    let class_list = target.className;
    class_list = class_list.split(' ');
    if(class_list[0] === dropdown_class1) {
        class_list[0] = dropdown_class2;
        for(let i=1; i<=total; i++)
        {
            if(i !== index){
                let btn_id = id + i.toString();
                let btn = document.getElementById(btn_id);
                _change_dropdown_class(btn, dropdown_class1);
            }
        }
    }
    else {
        class_list[0] = dropdown_class1;
    }

    let class_name = '';
    for(let c of class_list){
        class_name = class_name.concat(c + ' ');
    }
    target.className = class_name;
}


/*for website*/
function delete_website(id, email) {
    if(email === '')
    {
        return;
    }

    let url = '/website/delete/';
    let csrf_token = get_cookie('csrftoken');
    let form_data = new FormData();
    form_data.append('csrfmiddlewaretoken', csrf_token);
    form_data.append('id', id);
    form_data.append('email', email);

    $.ajax({
            url: url,
            type: 'post',
            data: form_data,
            contentType: false,
            processData: false,
            cache: false,
            success: function (data) {
                $('#deleteModal').modal('hide');
                if(data['url'])
                {
                    goto_link(data['url']);
                }
                else if(data['tip'])
                {
                    alert(data['tip']);
                }
            },
            error: function (data) {
                $('#deleteModal').modal('hide');
                let tip = '删除网站失败';
                alert(tip);
            }
        }
    );
}

function check_form_filed(field_list) {

    for(let field of field_list) {
        if (field.value === "") {
            alert('请填写' + field.previousElementSibling.innerHTML);
            field.focus();
            return false;
        }
    }
    return true
}

function check_website_basic(form) {

    let field_list = [form.inputTitle, form.inputSubtitle, form.inputDescription, form.inputKeyword, form.inputPerPage]
    let status = check_form_filed(field_list);

    if(status === false){
        return false;
    }

    try {
        let per_page = Number(form.inputPerPage.value);
        if(isNaN(per_page) || per_page <=0 )
        {
            alert(form.inputPerPage.previousElementSibling.innerHTML+'必须为大于0的数字');
            return false;
        }
    }
    catch (e) {
        alert(form.inputPerPage.previousElementSibling.innerHTML+'必须为大于0的数字');
        return false;
    }

    return true;
}

function check_website_deploy(form) {
    let field_list = [form.inputUrl, form.inputRepository, form.inputBranch, form.inputKeyword, form.inputUsername,
        form.inputPassword]
    let status = check_form_filed(field_list);

    return status !== false;
}

function check_website_form(form) {
    return check_website_basic(form) && check_website_deploy(form);
}

function delete_theme(target) {
    let id = target.getAttribute('data-id');
    let name = target.getAttribute('data-name');
    let url = '/website/themes/' + id + '/' + name +  '/delete/';

    let csrf_token = get_cookie('csrftoken');
    let form_data = new FormData();
    form_data.append('csrfmiddlewaretoken', csrf_token);

    function success(data){
        if(data['url']) {
            goto_link(url);
        }
        else if(data['tip']){
            alert(data['tip']);
        }
    }

    function error(data){
        if(data['tip']){
            alert(data['tip']);
        }
    }

    ajax_post(url, form_data, success, error);
}


/*for blog*/
function load_editor_preview(view_id, text_id) {
    editormd.markdownToHTML(view_id, {
        markdown : $(text_id).text(),
        emoji    : true,
        taskList : true,
        tex      : true,
        // htmlDecode : true,  // Enable / disable HTML tag encode.
        htmlDecode : "style,script,iframe",  // Note: If enabled, you should filter some dangerous HTML tags for website security.
    });
}

function update_post(data) {
    let post = document.getElementById('postDetail');
    post.innerHTML = "";

    let h2 = document.createElement('h2');
    h2.className = 'blog-title';
    h2.innerHTML = data['post_title'];

    let p = document.createElement('p');
    p.localName = 'blog-date';
    p.innerHTML = data['post_update'];

    let div = document.createElement('div');
    for(let tag of data['post_tags'])
    {
        let tag_div = document.createElement('div');
        tag_div.className = 'blog-tag';
        tag_div.innerHTML = tag;
        div.appendChild(tag_div);
    }

    let horizontal_bar = document.createElement('div');
    horizontal_bar.className = 'horizontal-bar';
    horizontal_bar.style.height = '2px';

    let content = document.createElement('div');
    content.className = 'blog-content';

    let content_div = document.createElement('div');
    content_div.id = 'markdown-view';
    let label = document.createElement('label');
    label.setAttribute('for', 'markdown-append-text');
    let text_area = document.createElement('textarea');
    text_area.id = 'markdown-append-text';
    text_area.setAttribute('style', 'display:none;')
    text_area.innerHTML = data['post_content'];

    content_div.appendChild(label);
    content_div.appendChild(text_area);

    content.appendChild(content_div);

    post.appendChild(h2);
    post.appendChild(p);
    post.appendChild(div);
    post.appendChild(horizontal_bar);
    post.appendChild(content);

    load_editor_preview("markdown-view", "#markdown-append-text");
}

function update_post_list(data) {
    let post_list = document.getElementById('postList');
    post_list.innerHTML = '';

    let posts = data['posts'];
    for(let post of posts){
        let div = document.createElement('div');
        div.className = 'blog-article-item';

        let div2 = document.createElement('div');
        let div3 = document.createElement('div');
        div3.className = 'blog-article-title';
        div3.innerHTML = post['title'];
        div3.setAttribute('name', post['id']);
        div3.setAttribute('onclick', 'get_post(this);');

        let span1 = document.createElement('span');
        span1.className = 'blog-article-edit';
        span1.setAttribute('data-id', post['id']);
        span1.setAttribute('onclick', 'edit_post(this);');

        let span2 = document.createElement('span');
        span2.className = 'blog-article-delete';
        span2.setAttribute('data-id', post['id']);
        span2.setAttribute('data-toggle', 'modal');
        span2.setAttribute('data-target', '#deleteModal');

        div2.appendChild(div3);
        div2.appendChild(span1);
        div2.appendChild(span2);

        let p = document.createElement('p');
        p.className = 'blog-article-date';
        p.innerHTML = post['update_time'];

        div.appendChild(div2);
        div.appendChild(p);
        post_list.appendChild(div);
    }
}

function get_post(target) {
    let url = '/blog/id/'
    let id = target.getAttribute('name');
    url = url + id + '/'

    $.ajax({
        url: url,
        type: 'get',
        cache: false,
        success: function (data) {
            if(data['tip'])
            {
                alert(data['tip']);
            }
            else {
                update_post(data);
            }
        },
        error: function (data) {
            alert('获取文章失败 ' + data['tip']);
        }
        }
    );
}

function get_post_list(url) {
    $.ajax({
            url: url,
            type: 'get',
            cache: false,
            success: function (data) {
                if(data['tip'])
                {
                    alert(data['tip']);
                }
                else {
                    update_post_list(data);
                }
            },
            error: function (data) {
                alert('获取文章失败 ' + data['tip']);
            }
        }
    );
}

function get_post_by_category(target) {
    let url = '/blog/category/';
    let id = target.getAttribute('name');
    url = url + id + '/';
    get_post_list(url);
}

function get_post_by_tag(target) {
    let url = '/blog/tag/';
    let id = target.getAttribute('name');
    url = url + id + '/';
    get_post_list(url);
}

function get_all_post() {
    let url = '/blog/all/';
    get_post_list(url)
}

function get_draft() {
    let url = '/blog/draft/';
    get_post_list(url)
}

function search_post(event, target) {
    let keyword = target.value;
    if(keyword === '')
    {
        return;
    }

    let keycode = event.which | event.keyCode;
    if (keycode === 13 ) //回车键是13
    {
        let url = '/blog/search/'
        url = url + keyword;
        get_post_list(url);
        $('#searchModal').modal('hide');
        return true;
    }
}

function edit_post(target) {
    let id = target.getAttribute('data-id');
    window.location.href = '/edit/' + id + '/edit/';
}

function delete_post(id) {
    let url = '/blog/id/' + id + '/delete/';

    let csrf_token = get_cookie('csrftoken');
    let form_data = new FormData();
    form_data.append('csrfmiddlewaretoken', csrf_token);

    $.ajax({
            url: url,
            type: 'post',
            data: form_data,
            contentType: false,
            processData: false,
            cache: false,
            success: function (data) {
                $('#deleteModal').modal('hide');

                if (data['tip']){
                    alert(data['tip']);
                }
                else {
                    window.location.href = data['url'];
                }
            },
            error: function (data) {
                $('#deleteModal').modal('hide');
                alert('删除文章失败' + data['tip']);
            }
        }
    );
}

function update_all_post() {
    let url = '/blog/id/0/update/';
    let csrf_token = get_cookie('csrftoken');
    let form_data = new FormData();
    form_data.append('csrfmiddlewaretoken', csrf_token);

    $.ajax({
            url: url,
            type: 'post',
            data: form_data,
            contentType: false,
            processData: false,
            cache: false,
            success: function (data) {
                $('#updateModal').modal('hide');
                if(data['tip']){
                    alert(data['tip']);
                }
                else {
                    alert('更新文章成功');
                }
            },
            error: function (data) {
                $('#updateModal').modal('hide');
                alert('更新文章失败' + data['tip']);
            }
        }
    );
}

function select_category(target) {
    let cate_select = document.getElementById('categorySelect');
    let cate = cate_select.getAttribute('data-cate');
    if(cate !== '')
    {
        let i = 0;
        for(let option = cate_select.firstElementChild; option !== null; option=option.nextElementSibling)
        {
            if (cate === option.textContent)
            {
                cate_select.selectedIndex = i;
                break;
            }
            i++;
        }
    }
}

/*for editor*/
class Editor {

    title_changed = false;
    content_changed = true;
    cate_changed = false;
    tag_changed = false;

    _save_post(url, success_func, error_func) {

        let form_data = new FormData();
        form_data.append('csrfmiddlewaretoken', get_cookie('csrftoken'));

        let draft_switch = document.getElementById('draftSwitch');
        let disable = draft_switch.getAttribute('disabled');
        let checked = draft_switch.getAttribute('checked');
        if(disable !== null && checked!==null)
        {
            form_data.append('status', 'draft');
        }

        if(this.title_changed){
            let title_input = document.getElementById('postTitle');
            let title = title_input.value;
            if(title === '')
            {
                alert('标题不能为空');
                return;
            }
            form_data.append('title', title);
        }

        if(this.content_changed){
            let editor = $('.editormd-markdown-textarea');
            let content =  editor.val();
            form_data.append('content', content);
        }

        if(this.cate_changed) {
            let cate_select = document.getElementById('categorySelect');
            let cate = null;

            if(cate_select.selectedIndex === 0)
            {
                cate = '';
            }
            else
            {
                cate = cate_select.options[cate_select.selectedIndex].innerText;
            }
            form_data.append('category', cate);
        }

        if(this.tag_changed){
            let tag_group = document.getElementById('tagGroup');
            let tag_list = [];

            for(let tag=tag_group.firstElementChild; tag.type !== 'button';
                tag = tag.nextElementSibling)
            {
                tag_list.push(tag.firstElementChild.innerHTML);
            }
            form_data.append('tag', tag_list.toString());
        }
        let obj = this;

        $.ajax({
                url: url,
                type: 'post',
                data: form_data,
                contentType: false,
                processData: false,
                cache: false,
                success: function(data){
                    let status = success_func(data);
                    if(status){
                        obj.content_changed = true;
                        obj.cate_changed = false;
                        obj.tag_changed = false;
                        obj.title_changed = false;
                    }
                },
                error: error_func,
            }
        );
    }

    _add_option_to_select(select, inner) {
        let option = document.createElement('option');
        option.innerHTML = inner;
        select.appendChild(option);
    }

    save_post(target) {
        let id = target.getAttribute('data-id');
        let url = '/blog/id/' + id + '/save/';

        function success(data) {
            if (data['tip'])
            {
                alert('保存失败，' + data['tip']);
                return false;
            }
            else if(data['id'])
            {
                window.location.href = '/edit/' + data['id'] +'/edit/';
                return true;
            }
            else{
                alert('已保存');
                return true;
            }
        }

        function error(data) {
            alert('保存失败' + data['tip']);
        }

        this._save_post(url , success, error);
    }

    release_post(target) {
        let id = target.getAttribute('data-id');
        let url = '/blog/id/' + id + '/release/';

        function success(data) {
            if (data['tip'])
            {
                alert('发布失败，' + data['tip']);
                return false;
            }
            else{
                alert('已发布');
                return true;
            }
        }

        function error(data) {
            alert('发布失败' + data['tip']);
        }

        this._save_post(url , success, error);
    }

    add_tag(tag) {
        let tag_select = document.getElementById('tagSelect');
        this._add_option_to_select(tag_select, tag);
    }

    remove_tag(target) {
        let parent = get_n_parent(target, 1);
        let tag_group = document.getElementById('tagGroup');
        tag_group.removeChild(parent);
        this.tag_changed = true;
    }

    insert_tag(tag) {
        let tag_group = document.getElementById('tagGroup');
        for(let t = tag_group.firstElementChild; t.type!=='button'; t = t.nextElementSibling)
        {
            if(t.firstElementChild.innerHTML === tag)
            {
                alert('该标签已选择！');
                return;
            }
        }

        let div = document.createElement('div');
        div.className = 'editor-closeable-tag';
        let span1 = document.createElement('span');
        span1.className = 'editor-span';
        span1.innerHTML = tag;

        let span2 = document.createElement('span');
        span2.className = 'editor-close-btn';
        span2.setAttribute('onclick', 'post_editor.remove_tag(this);');
        div.appendChild(span1);
        div.appendChild(span2);

        tag_group.prepend(div);
        this.tag_changed = true;
    }

    create_category(form) {
        let name = form.name.value;
        if(name === '') {
            return false;
        }

        let url = form.action;
        let form_data = new FormData();
        form_data.append('name', name);
        form_data.append('csrfmiddlewaretoken', form.csrfmiddlewaretoken.value);
        let obj = this;
        $.ajax({
                url: url,
                type: 'post',
                data: form_data,
                contentType: false,
                processData: false,
                cache: false,
                success: function (data) {
                    $('#categoryModal').modal('hide');
                    if (data['tip'])
                    {
                        alert('添加分类失败,' + data['tip']);
                        return;
                    }
                    alert('分类已添加');
                    obj.add_category(name);
                },
                error: function (data) {
                    $('#categoryModal').modal('hide');
                    alert('添加分类失败 ' + data['tip']);
                }
            }
        );

        return false;
    }

    create_tag(target) {
        let parent = get_n_parent(target, 1);
        let input = parent.firstElementChild.nextElementSibling;
        let name = input.value;

        if(name === '') {
            return;
        }

        let url = '/blog/tag/0/create/';
        let form_data = new FormData();
        form_data.append('name', name);
        form_data.append('csrfmiddlewaretoken', get_cookie('csrftoken'));
        let obj = this;

        $.ajax({
                url: url,
                type: 'post',
                data: form_data,
                contentType: false,
                processData: false,
                cache: false,
                success: function (data) {
                    $('#tagModal').modal('hide');
                    if (data['tip'] !== undefined)
                    {
                        alert('添加标签失败,' + data['tip']);
                        return;
                    }
                    alert('标签已添加');
                    obj.add_tag(name);
                },
                error: function (data) {
                    $('#tagModal').modal('hide');

                    alert('添加标签失败 ' + data['tip']);
                }
            }
        );
    }

    add_tag_to_group() {
        let tag_select = document.getElementById('tagSelect');
        let index = tag_select.selectedIndex;
        if (index === 0)
        {
            return;
        }

        let cur_selected = tag_select[index];
        this.insert_tag(cur_selected.innerHTML);
        this.tag_changed = true;
    }

    add_category(cate) {
        let cate_select = document.getElementById('categorySelect');
        this._add_option_to_select(cate_select, cate);
    }

    on_cate_changed() {
        this.cate_changed = true;
    }

    on_title_changed(){
        this.title_changed = true;
    }
}

var post_editor = new Editor();
