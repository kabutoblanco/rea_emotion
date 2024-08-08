const queryString = window.location.search
const urlParams = new URLSearchParams(queryString)
let time = urlParams.get('time')

time = time * 1000 * 60

function delay(rate) {
    return new Promise(resolve => setTimeout(resolve, rate * 1000))
}

async function watch() {
    if (time <= 0) {
        sendActionUser('1,-')
        await delay(1)
        alert('Gracias por participar')
        window.location.href = '/home/daniel/Documents/tesis/test/index.html'
        clearInterval(timeInterval)
        return
    }

    time -= 1000
    minutes = Math.floor(time / 1000 / 60)
    seconds = Math.floor(time / 1000 % 60)

    if (minutes < 10) minutes = `0${minutes}`
    if (seconds < 10) seconds = `0${seconds}`

    document.getElementById('watch').textContent = `${minutes}:${seconds}`
}

let timeInterval = setInterval(watch, 1000)

function full() {
    if (document.documentElement.requestFullscreen)
        document.documentElement.requestFullscreen()
    else
        document.exitFullscreen()
}

document.addEventListener('DOMContentLoaded', function() {
    toggleLeftMenu(this)
    document.getElementById('sidebar').style.display = 'none'
    document.getElementById('menu').style.display = 'none'
})
