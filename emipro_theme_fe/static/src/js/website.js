odoo.define('module.DianBackend', function(require) {
    "use strict";
    var mainIntervalTime = 3500;
    var rpc = require('web.rpc');

    $(document).ready(function() {

        var mainInterval = setInterval(function() {
            var currency_selector=$("span[itemprop='priceCurrency']");
            var lang_btn_code=$("span.lang_btn_code");
            $("span.oe_currency_value").each(function(index)
                {
                        var oe_currency_value=$(this).text();
                        try
                        {                    
                            if(String(currency_selector.text()).includes("COP") && String(lang_btn_code.text()).includes("es_CO"))
                            {
                                var oe_currency_value_parts=String(oe_currency_value).split(',');
                                $(this).text(String(oe_currency_value_parts[0]));
                            }
                            if(String(currency_selector.text()).includes("COP") && String(lang_btn_code.text()).includes("zh_CN"))
                            {
                                var oe_currency_value_parts=String(oe_currency_value).split('.');
                                $(this).text(String(oe_currency_value_parts[0]));
                            }
                        }
                    catch(err)
                        {
                            console.log("ERROR");
                            console.log(err);
                        }
                });

            if ($("div.div_city").length > 1) {
                $("div.div_city").last().hide();
            }
            if ($("select#fe_tipo_documento").val() == '31') {
                $("button.go-rues").removeClass("invisible");
                $("input#fe_digito_verificacion").removeClass("invisible");
                $("button.go-rues").addClass("visible");
                $("input#fe_digito_verificacion").addClass("visible");
            } else {
                $("button.go-rues").removeClass("visible");
                $("input#fe_digito_verificacion").removeClass("visible");
                $("button.go-rues").addClass("invisible");
                $("input#fe_digito_verificacion").addClass("invisible");
            }


        }, 200);

        $(document).on("change", "select#fe_tipo_documento", function() {
            if ($("select#fe_tipo_documento").val() == '31') {
                $("button.go-rues").removeClass("invisible");
                $("input#fe_digito_verificacion").removeClass("invisible");
                $("button.go-rues").addClass("visible");
                $("input#fe_digito_verificacion").addClass("visible");
            } else {
                $("button.go-rues").removeClass("visible");
                $("input#fe_digito_verificacion").removeClass("visible");
                $("button.go-rues").addClass("invisible");
                $("input#fe_digito_verificacion").addClass("invisible");
            }
        });
    });
});
