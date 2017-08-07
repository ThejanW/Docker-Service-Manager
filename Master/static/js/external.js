/**
 * Created by thejan on 8/7/17.
 */
// for highlighting elements
$('#service-list').on('click', 'li', function () {
    $(this).addClass('active').siblings().removeClass('active');
});

function goHome() {
    $('#service-list').children().removeClass('active');
    $('#home').show();
    $('[id^=service_service]').hide();
}

function showService(pattern) {
    $('#home').hide();
    $('[id^=service_service]').hide();
    $('#service_' + pattern).show();
}

$(document).ready(function () {
    $('[id^=service_service]').hide();
});
