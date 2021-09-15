var vm = new Vue({
    el: '#app',
    // 声明vue变量使用[[语法
    delimiters: ['[[', ']]'],
    data: {
        host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        cart_total_count: 0, // 购物车总数量
        cart: [], // 购物车数据,
        f1_tab: 1, // 1F 标签页控制
        f2_tab: 1, // 2F 标签页控制
        f3_tab: 1, // 3F 标签页控制
    },
    computed: {
        total_count: function () {
            var total = 0;
            for (var i = 0; i < this.cart.length; i++) {
                total += parseInt(this.cart[i].count);
                this.cart[i].amount = (parseFloat(this.cart[i].price) * parseFloat(this.cart[i].count)).toFixed(2);
            }
            return total;
        },
    },
    mounted: function () {
        this.get_cart();
    },
    methods: {
        // 退出
        logout: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 获取购物车数据
        get_cart: function () {
            // 获取购物车数据
            axios.get(this.host + '/cart/', {
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json',
                withCredentials: true
            })
                .then(response => {
                    this.cart = response.data;
                    for (var i = 0; i < this.cart.length; i++) {
                        this.cart[i].amount = (parseFloat(this.cart[i].price) * this.cart[i].count).toFixed(2);
                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        }
    }
});