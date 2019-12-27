$(document).ready(function () {

    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });

    $('#menu-toggle').on('click', function (e) {
        var save_state = !$('#sidebar, .side_container').hasClass('collapsed');
        localStorage.setItem('menu-closed', save_state);
        $('#sidebar, .side_container, .main, .header, .navbar-brand').toggleClass('collapsed');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

//    var state = localStorage.getItem('menu-closed');
//
//    if (state === null) {
//        $('#sidebar, .side_container, .main, .header, .header, .navbar-brand').removeClass('collapsed');
//    } else {
//        var closed = state === "true" ? true : false;
//        if (closed) {
//            $('#sidebar, .side_container, .main, .header, .header, .navbar-brand').addClass('collapsed');
//        }
//    }
});



