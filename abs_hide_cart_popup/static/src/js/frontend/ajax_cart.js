odoo.define('abs_hide_cart_popup.extend_ajax_cart', function (require) {
    "use strict";
    var sAnimations = require('website.content.snippets.animation');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
     var ajax = require('web.ajax');
    var _t = core._t;
    var WebsiteSale = new sAnimations.registry.WebsiteSale();
    var QWeb = core.qweb;
    var xml_load = ajax.loadXML(
        '/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml',
        QWeb
    );
    /*var OptionalProductsModal = require('sale_product_configurator.OptionalProductsModal');*/
    var flag = 1;

    publicWidget.registry.ajax_cart = publicWidget.Widget.extend({
        selector: ".oe_website_sale",
        ajaxCartSucess: function(product_id){
            /** Success popup */
            /*ajax.jsonRpc('/ajax_cart_sucess_data', 'call',{'product_id':product_id}).then(function(data) {
                if($("#wrap").hasClass('js_sale')) {
                    $("#ajax_cart_model_shop .modal-body").html(data);
                    $("#ajax_cart_model_shop").modal({keyboard: true});
                } else {
                    $("#ajax_cart_model .modal-body").html(data);
                    $("#ajax_cart_model").modal({keyboard: true});
                }
                $('#ajax_cart_model, #ajax_cart_model_shop').removeClass('ajax-cart-item');
                $('#ajax_cart_model, #ajax_cart_model_shop').addClass('ajax-sucess');

            });*/
        }
    });
});
