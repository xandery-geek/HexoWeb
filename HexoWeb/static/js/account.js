/*check password and repeat password*/
function password_check(form) {

    if(form.password.value === ''){
        form.password.focus();
        alert("请输入密码");
        return false;
    }

    if(form.re_password.value === ''){
        form.re_password.focus();
        alert("请确认密码");
        return false;
    }

    if(form.password.value !== form.re_password.value){
        form.re_password.focus();
        alert("密码不一致");
        return false;
    }

    let pattern = /^[A-Za-z0-9]{8,20}$/;
    if(!pattern.exec(form.password.value)){
        form.password.focus();
        alert("密码格式必须为8-20位字母或者数字 '^[A-Za-z0-9]{8,20}$'");
        return false;
    }

    return true
}

/*check the register form*/
function signup_check(form) {

    if(form.nick.value === ''){
        alert("请输入昵称");
        form.nick.focus();
        return false;
    }
    if(form.email.value === ''){
        alert("请输入邮箱地址");
        form.email.focus();
        return false;
    }

    return password_check(form);
}

/*check the login form*/
function login_check(form){

    if(form.email.value === ''){
        form.email.focus();
        alert("请输入邮箱地址");
        return false;
    }

    return true;
}

/*check the password reset form*/
function reset_check(form) {
    if(form.email.value === ''){
        form.email.focus();
        alert("请输入邮箱地址");
        return false;
    }

    if(form.verify_code.value === '') {
        form.email.focus();
        alert("请输入验证码");
        return false;
    }

    return password_check(form);
}

function getCookie(name) {
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

/*check the send verification code form*/
function get_verify_code(form) {
    if(form.email.value === '') {
        form.email.focus();
        alert("请输入邮箱地址");
        return;
    }

    let form_data = new FormData();
    form_data.append('email', form.email.value);
    let csrf_token = getCookie('csrftoken');
    form_data.append('csrfmiddlewaretoken', csrf_token);

    $.ajax({
        url:'/account/reset/',
        type: 'post',
        data: form_data,
        contentType: false,
        processData: false,
        success: function (data) {
            alert("验证码已发送！");
        },
        error: function (data) {
            alert('验证码发送失败，' + data['error']);
        }
    });

    return false;
}
