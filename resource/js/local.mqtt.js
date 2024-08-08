var client = mqtt.connect('ws://0.0.0.0:8083')

client.on('connect', function () {
    console.log('Conexión MQTT establecida')
});

client.on('error', function (error) {
    console.error('Error de MQTT:', error)
});

function sendActionUser (message) {
    client.publish('action', `${message}`)
}

function sendAction(message) {
    client.publish('rea', `action,${message}`)
}

function sendPosition(message) {
    client.publish('rea', `position,${message}`)
}

function sendMedia(message) {
    client.publish('rea', `media,${message}`)
}
