$(document).ready(function () {

    //hide individual service pages at startup, only show the services summary table
    $('[id^=service_]').hide();

    namespace = '/test';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('log_run_status', function (msg) {
        var service = msg.service;
        var status = msg.status;
        var status_service = $('#status_' + service);

        var status_service_btn = $('#status_btn_' + service);
        status_service.text(status);
        if (status == "STOPPED") {
            status_service_btn.text("START");
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-danger');
        }
        else if (status == "RUNNING") {
            status_service_btn.text("STOP");
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-success');
        }
        else if (status == "NOT AVAILABLE") {
            status_service_btn.text("PULL");
            status_service.removeClass(function (index, className) {
                return (className.match(/(^|\s)label-\S+/g) || []).join(' ');
            }).addClass('label-primary');
        }
    });

    namespace_build = '/build';
    var socket_build = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace_build);

    socket_build.on('log_build_status', function (msg) {
        // $('#log_build_status').append('<br>' + $('<div/>').text(msg.data).html());
        console.log(msg.data);
        $('#log_build_status').append(msg.data)
    });


    $('#init').click(function () {
        socket_build.emit('init')
    });
});

// for highlighting elements in left panel
$('#service-list').on('click', 'li', function () {
    $(this).addClass('active').siblings().removeClass('active');
});

// hide individual services, show services summary table
function goHome() {
    $('#service-list').children().removeClass('active');
    $('#home').show();
    $('[id^=service_]').hide();
}

//hide services summary table, show the individual service page
function showService(service) {
    $('#home').hide();
    $('[id^=service_]').hide();
    $('#service_' + service).show();
}

// start, stop a container or pull an image
function doAction(service, virtual_host, object) {
    namespace = '/test';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    if ($(object).text() == "START") {
        socket.emit('start', {service: service, virtual_host: virtual_host});
    }
    else if ($(object).text() == "STOP") {
        socket.emit('stop', {service: service});
    }
    else if ($(object).text() == "PULL") {
        socket.emit('pull', {service: service});
    }
    return false;
}

