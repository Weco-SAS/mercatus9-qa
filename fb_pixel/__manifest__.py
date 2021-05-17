# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Facebook Pixel Integration",
  "summary"              :  """Odoo Facebook Pixel Integration is an analytics tool that allows you to measure the effectiveness of your advertising by understanding the actions people take on your Odoo website.""",
  "category"             :  "Website",
  "version"              :  "1.1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Facebook-Pixel-Integration.html",
  "description"          :  """https://webkul.com/blog/odoo-facebook-pixel-integration/
Odoo Facebook Pixel Integration
Facebook Pixel Integration in Odoo
Analytics 
Analytics Tool
Analytics Tool in Odoo
Integration for analytics
Facebook Analytical Integration
Odoo
Odoo Facebook
Customer Behaviour analysis
Integration
Odoo integration
FB pixel
Odoo Fb Pixel Integration
Fb Pixel Integration
Pixel Integration
FB Analytical Integration
Facebook Pixel, FB Pixel, Facebook Ads, FB Ads, Facebook Ecommerce, FB Ecommerce, Facebook E-Commerce, FB E-Commerce, Facebook Analytics, FB Analytics, Facebook Shop, FB Shop, Facebook Marketplace, FB Marketplace""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=fb_pixel",
  "depends"              :  ['website_sale'],
  "data"                 :  [
                             'views/res_config_settings_views.xml',
                             'views/snippets_template.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "price"                :  35,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}