window.addEventListener('beforeunload', () => {
	sendAction('-')
})

document.addEventListener('DOMContentLoaded', () => {
    loadEvents()
})

var focus = false

function loadEvents() {
    setTimeout(() => {
        let videos = $('video')
        videos.each((i, video) => {
            video.addEventListener('play', () => {
                sendAction('v')
            })
            video.addEventListener('pause', () => {
                sendAction('-')
            })
            video.addEventListener('blur', () => {
                video.pause()
                sendAction('-')
            })
        })

        let arranca_ = $('.arranca')
        arranca_.each((i, arranca) => {
            arranca.addEventListener('click', () => {
                sendAction('v')
                $(arranca).hide()
            })
        })

        let inputs = $('input,textarea');
        inputs.each((i, input) => {
            input.addEventListener('focusin', () => {
                sendAction('t')
            })
            input.addEventListener('focusout', () => {
                sendAction('-')
            })
        })

        let checks = $('div[id^=Stage_checkbox]');
        checks.each((i, check) => {
            check.addEventListener('mouseenter', () => {
                sendAction('t')
            })
            check.addEventListener('mouseout', () => {
                sendAction('-')
            })
        })
        
        let controlsBtn = $('div[id^=Stage_bt_back], div[id^=Stage_bt_next], div[data-sg-id^=btn-page], div[id=item_buttons_back], div[id^=item_buttons_next], li[class^=tab], span[class^=buttons]')
        controlsBtn.each((i, btn) => {
            btn.addEventListener('click', () => {
                sendAction('-')
                let videos = $('video')
                videos.each((i, video) => {
                    video.pause()
                })
            })
        })
    }, 850)
}
