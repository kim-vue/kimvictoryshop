$(function() {
    accordion(); //아코디언 메뉴
    resizeMenu(); //메뉴 리사이즈 버튼
    tab(); //탭메뉴
    removeText(); //텍스트제거
    tabSwiper(); //탭스와이퍼
})

//아코디언 메뉴
function accordion() {
    //클릭 시
    $(document).on("click", ".lnb .menu-depth01 > li", function(e) {
        $(this).children().next().slideToggle(200);
        $(this).siblings().children().next().slideUp(200);

        if (!$(this).hasClass("open")) {
            $(this).addClass("open");
        } else {
            $(this).removeClass("open");
        }
    })

    $(document).on("click", ".menu-depth02 > li > a", function(e) {
        e.stopPropagation();
    });

    //hover 시
    $(document).on("mouseenter mouseleave", ".lnb.minimized .menu-depth01 > li", function(e) {

        if ($(".lnb").hasClass("minimized")) {

            $(this).children().next().toggle();
            $(this).siblings().children().next().slideUp();

            if (!$(this).children().hasClass("on")) {
                $(this).children().addClass("on");
            } else {
                $(this).children().removeClass("on");
            }
        }
    })

    $(".menu-depth02 > li").click(function(event) {
        event.stopImmediatePropagation();
    });
}

//메뉴 리사이즈 버튼
function resizeMenu() {
    $(".btn-lnb").click(function() {

        if ($(".lnb").hasClass("minimized")) {
            $(".lnb").removeClass("minimized");
            $(".header > .logo").removeClass("mini");
            $(".header .logo > a > img.logo-big").css("display", "inline-block");
            $(".header .logo > a > img.logo-mini").css("display", "none");
            if ($(".menu-depth01 > li").hasClass("hide")) {
                $(".menu-depth01 > li.open").removeClass("hide");
                //토글 상태 초기화
                if ($(".menu-depth01 > li.open > .menu-depth02").css("display", "none")) {
                    $(".menu-depth01 > li.open > .menu-depth02").css("display", "block");
                } else {
                    $(".menu-depth01 > li.open > .menu-depth02").css("display", "none");
                }
                $(".menu-depth01 > li.open > .menu-depth02").css("display", "none");
                $(".menu-depth01 > li.open > .menu-depth02").toggle();
            }
        } else {
            $(".lnb").addClass("minimized");
            $(".header > .logo").addClass("mini");
            $(".header .logo > a > img.logo-big").css("display", "none");
            $(".header .logo > a > img.logo-mini").css("display", "inline-block");

            if ($(".menu-depth01 > li").hasClass("open")) {
                $(".menu-depth01 > li.open").addClass("hide");
                //토글 상태 초기화
                if ($(".menu-depth01 > li.open.hide > .menu-depth02").css("display", "block")) {
                    $(".menu-depth01 > li.open.hide > .menu-depth02").css("display", "none");
                } else {
                    $(".menu-depth01 > li.open.hide > .menu-depth02").css("display", "block")
                }
                $(".menu-depth01 > li.open.hide > .menu-depth02").css("display", "block");
                $(".menu-depth01 > li.open.hide > .menu-depth02").toggle();
            }
        }
    });
}

//탭메뉴
function tab() {
    $("body").on("click", ".tab-wrap .link-tab a", function() {
        var idx = $(".tab-wrap .link-tab a").index($(this));
        if ($('.tab-content').length > 1) {
            $(".tab-wrap .link-tab a").each(function(index) {
                if (idx == index) {
                    if (!$(this).hasClass("active")) {
                        $(this).addClass("active");
                        $(".tab-wrap .tab-content").eq(index).addClass("active");
                    }
                } else {
                    if (!$(this).hasClass("active")) {
                        $(this).removeClass("active");
                        $(".tab-wrap .tab-content").eq(index).removeClass("active");
                    }
                    $(this).removeClass("act" +
                        "ive");
                    $(".tab-wrap .tab-content").eq(index).removeClass("active");
                }
            });
        } else if ($('.tab-content').length == 1) {
            $('.tab-content').addClass('active');
            $(".tab-wrap .link-tab a").each(function(index) {
                if (idx == index) {
                    if (!$(this).hasClass("active")) {
                        $(this).addClass("active");
                    }
                } else {
                    if (!$(this).hasClass("active")) {
                        $(this).removeClass("active");
                    }
                    $(this).removeClass("active");
                }
            });
        }
    });
}

function tabSwiper() {
    var swiper = new Swiper('.swiper-container', {
        slidesPerView: 10,
        loop: true,
        loopFillGroupWithBlank: true,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
    });
}

function removeText() {
    $(".remove_text").click(function() {
        $(this).siblings().val('');
        $(this).siblings().children().val('');
    });
}

//모달 open
function openModal() {
    $(".modal").addClass("is-active");
}

//모달 close
function closeModal() {
    $(".modal").removeClass("is-active");
}