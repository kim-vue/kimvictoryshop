$(function () {
    mainMenu(); //메인 메뉴
    quickMenuEffect(); //퀵메뉴 마우스 효과
    blueBoxEffect(); //하단 박스 6개 마우스 효과
})

function mainMenu(){
    $(".wrap.type-main .header .logo > button").click(function(){
        if($(".menu-wrap").css("display") == "none"){
            $(".menu-wrap").slideDown(300);
        }else{
            $(".menu-wrap").slideUp(300);
        }
    });
}

function quickMenuEffect(){
    $(".quick-menu li").hover(function() {
        $(this).stop().animate({"border-color": "#0065b3"}, 250);
    },
    function() {
        $(this).stop().animate({"border-color": "#fff"}, 250);

    });
}

function blueBoxEffect(){
    $(".blue-box li.blue01").hover(function() {
        $(this).stop().animate({"border-color": "#0065b3"}, 250);
        console.log("hover");

    },
    function() {
        $(this).stop().animate({"border-color": "#d4e8fa"}, 250);
        console.log("out");

    });

    $(".blue-box li.blue02").hover(function() {
        $(this).stop().animate({"border-color": "#0065b3"}, 250);
    },
    function() {
        $(this).stop().animate({"border-color": "#c6e3fb"}, 250);
    });

    $(".blue-box li.blue03").hover(function() {
        $(this).stop().animate({"border-color": "#0065b3"}, 250);
    },
    function() {
        $(this).stop().animate({"border-color": "#a9d3f6"}, 250);
    });

    $(".blue-box li.blue04").hover(function() {
        $(this).stop().animate({"border-color": "#0065b3"}, 250);
    },
    function() {
        $(this).stop().animate({"border-color": "#8fc4f0"}, 250);
    });

    $(".blue-box li.blue05").hover(function() {
        $(this).stop().animate({"border-color": "#0065b3"}, 250);
    },
    function() {
        $(this).stop().animate({"border-color": "#6aaee9"}, 250);
    });

    $(".blue-box li.blue06").hover(function() {
        $(this).stop().animate({"border-color": "#0065b3"}, 250);
    },
    function() {
        $(this).stop().animate({"border-color": "#65a9e5"}, 250);
    });
}