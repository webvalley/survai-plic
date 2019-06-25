(function($) {
    $(document).ready(function() {
        var $el = $("#id_name");
        var $spans = $('.badge-pill');
            $spans.each(function(){
                $(this).text($el.val());
                $(this).attr("checked", "checked");
            });

        $el.on('input', function(e){
            var name = $(this).val();
            if (name === ""){
                name = "Resource Tag";
            }

            var $spans = $('.badge-pill');
            $spans.each(function(){
                $(this).text(name);

            });
    });

    });

})(django.jQuery);