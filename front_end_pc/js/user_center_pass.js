
var vm = new Vue({
    el: '#app',
    data: {
        host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
        error_password: false,
        error_new_password: false,
        error_confirm_password: false,
        password:'',
        new_password:'',
        confirm_password:'',
    },
    mounted: function(){
        // 判断用户的登录状态
        if (this.user_id && this.token) {
            axios.get(this.host + '/user/', {
                    // 向后端传递JWT token的方法
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                })
                .then(response => {
                    // 加载用户数据
                    this.user_id = response.data.id;
                    this.username = response.data.username;
                })
                .catch(error => {
                    if (error.response.status==401 || error.response.status==403) {
                        location.href = '/login.html?next=/user_center_info.html';
                    }
                });
        } else {
            location.href = '/login.html?next=/user_center_info.html';
        }
    },
    methods: {
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        check_pwd: function (){
            var len = this.new_password.length;
            if(len<8||len>20){
                this.error_new_password = true;
            } else {
                this.error_new_password = false;
            }
        },
        check_cpwd: function (){
            if(this.new_password!==this.confirm_password) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },
        // 表单提交,修改密码方法
        on_submit: function(){
            // this.check_username();
            // this.check_ipwd();
            this.check_pwd();
            this.check_cpwd();
            if (this.error_new_password == false && this.error_confirm_password == false) {
                axios.put(this.host+'/user/password/',
                    // { user_id: this.user_id },
                    {
                        password: this.password,
                        new_password: this.new_password,
                        confirm_password: this.confirm_password,
                        user_id:this.user_id,},
                    {
                        // 向后端传递JWT token的方法
                        headers: {
                            'Authorization': 'JWT ' + this.token
                        },
                        responseType: 'json'
                    })
                    .then(response => {
                        // 弹出修改成功，跳转到登录页面
                        alert("修改成功!");
                        sessionStorage.clear()
                        localStorage.clear()
                        return_url = '/login.html';
                        location.href = return_url;
                    })
                    .catch(error => {
                        if (error.response.status == 400) {
                            this.error_pwd_message = '原始密码错误';
                        } else {
                            this.error_pwd_message = '服务器错误';
                        }
                        this.error_pwd = true;
                    })
            }
        },
 
    }
});