odoo.define('module.Payu', function(require) 
{
    "use strict";
    var rpc = require('web.rpc');

    $(document).ready(function() 
    {
        var default_button = $("form.o_payment_form").find("button#o_payment_form_pay");
        if ($("#payment_method").length > 0) {
            $("#o_payment_form_pay").after(function() {
                initPayuAcquirer();                
            });
        }

        $("#o_payment_form_pay").on("click",function()
        {
            event.preventDefault();
            var data_provider = $("input[name='pm_id']:checked").attr("data-provider");
            if(data_provider=="payu")
            {
                $("#payu-form").submit();
            }
            else
            {
                if(data_provider!="mercadopago")
                    $("form.o_payment_form").submit();                    
            }       
        });
        
        $("input[name='delivery_type']").on("change",function()
        {
            event.preventDefault();
            var data_provider = $("input[name='pm_id']:checked").attr("data-provider");
            var delivery_method = $(this).val();
            initPayuAcquirer();
            
        });
        
    });

    function initPayuAcquirer()
    {
        var data = { "params": {  } }
            $.ajax({
                type: "POST",
                url: '/payu/get_payu_acquirer',
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                async: false,
                success: function(response) {
                    console.log(response)
                    var acquirer = response.result.acquirer;
                    var form_bill = response.result.form_bill;
                    if(String(acquirer.state)==String("test") || String(acquirer.state)==String("enabled"))
                    {
                        if($("#quote_content").length>0)
                        { 
                            $("#quote_content").append(form_bill);
                        }
                        if($(".oe_cart").length>0)
                        { 
                            $(".oe_cart").append(form_bill);
                        }
                       fillBillForm(acquirer);
                    }                    
                }
            });
    }
    
    function fillBillForm(acquirer)
    {
        $("input[name='merchantId']").val(acquirer.payu_merchant_id);
        $("input[name='accountId']").val(acquirer.payu_account_id);
        var partner_id = $(".o_payment_form").attr("data-partner-id");
        var acquirer_id = $('input[name="pm_id"]:checked').attr("data-acquirer-id");

        var online_payment = "no";
        if($("#quote_content").length>0)
        {
            online_payment = "yes";
        }

        var data = { "params": { partner_id: partner_id, acquirer_id: acquirer_id, online_payment: online_payment } }
        $.ajax({
            type: "POST",
            url: '/payu/get_sale_order',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: "application/json",
            async: false,
            success: function(response) {
                var sale_order = response.result;
                var pay_form = $('#payu-form');
                
                pay_form.find("input[name='description']").val(sale_order.order_description);
                pay_form.find("input[name='referenceCode']").val(String(sale_order.order_name_odoo)+String(sale_order.order_name));
                pay_form.find("input[name='amount']").val((sale_order.amount));
                pay_form.find("input[name='tax']").val((sale_order.tax));
                pay_form.find("input[name='taxReturnBase']").val((sale_order.tax_return_base));
                pay_form.find("input[name='currency']").val((sale_order.currency_name));
                pay_form.find("input[name='signature']").val((sale_order.signature));
                pay_form.find("input[name='test']").val((sale_order.environment));
                pay_form.find("input[name='buyerEmail']").val(sale_order.email);
                
                pay_form.find("input[name='payerFullName']").val(sale_order.name);
                pay_form.find("input[name='payerDocument']").val(sale_order.payer_document);
                pay_form.find("input[name='mobilePhone']").val(sale_order.phone);
                pay_form.find("input[name='billingAddress']").val(sale_order.address);
                pay_form.find("input[name='shippingAddress']").val(sale_order.address);
                pay_form.find("input[name='zipCode']").val(sale_order.zip);
                pay_form.find("input[name='billingCountry']").val(sale_order.country_code);
                pay_form.find("input[name='shippingCountry']").val(sale_order.country_code);
                pay_form.find("input[name='buyerFullName']").val(sale_order.name);
                pay_form.find("input[name='payerEmail']").val(sale_order.email);
                pay_form.find("input[name='payerMobilePhone']").val(sale_order.phone);
                
                pay_form.find("input[name='responseUrl']").val(sale_order.response_url);
                pay_form.find("input[name='confirmationUrl']").val(sale_order.response_url);
                pay_form.attr("action",sale_order.end_point_url);
            }
        });
    }
});

