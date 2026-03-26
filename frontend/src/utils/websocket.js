import Stomp from 'stompjs'
import store from '../store'

let client = null;

export function connectWs() {
    return new Promise((resolve, reject) => {
        if (typeof WebSocket == 'undefined') {
            alert('不支持websocket,请联系管理员！')
            reject();
        }
        client = Stomp.client(window.socketURL);
        client.debug = null;
        // 连接RabbitMQ
        client.connect('用户名', '密码', () => {
            resolve();
        }, () => {
            reject()
        }, '/');
    })
}

export { client }
