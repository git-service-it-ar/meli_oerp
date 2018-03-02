# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from odoo import fields, osv, models, api

_logger = logging.getLogger(__name__)

class MercadolibreCategory(models.Model):
    _name = "mercadolibre.category"
    _description = "Categories of MercadoLibre"

    name = fields.Char('Name')
    meli_category_id = fields.Char('Category Id')
    public_category_id = fields.Integer('Public Category Id')

    def import_category(self, category_id ):
        category_model = self.env['mercadolibre.category']
        meli_util_model = self.env['meli.util']
        meli = meli_util_model.get_new_instance()
        if (category_id):
            ml_cat_id = category_model.search([('meli_category_id','=',category_id)])
            if (ml_cat_id):
                print "category exists!" + str(ml_cat_id)
            else:
                print "Creating category: " + str(category_id)
                #https://api.mercadolibre.com/categories/MLA1743
                response_cat = meli.get("/categories/"+str(category_id), {'access_token':meli.access_token})
                rjson_cat = response_cat.json()
                print "category:" + str(rjson_cat)
                fullname = ""
                if ("path_from_root" in rjson_cat):
                    path_from_root = rjson_cat["path_from_root"]
                    for path in path_from_root:
                        fullname = fullname + "/" + path["name"]

                #fullname = fullname + "/" + rjson_cat['name']
                #print "category fullname:" + str(fullname)
                _logger.info(fullname)
                cat_fields = {
                    'name': fullname,
                    'meli_category_id': ''+str(category_id),
                    }
                ml_cat_id = category_model.create((cat_fields))


    def import_all_categories(self, category_root ):
        warning_model = self.env['warning']
        category_model = self.env['mercadolibre.category']
        meli_util_model = self.env['meli.util']
        company = self.env.user.company_id
        meli = meli_util_model.get_new_instance()
        RECURSIVE_IMPORT = company.mercadolibre_recursive_import
        if (category_root):
            response = meli.get("/categories/"+str(category_root), {'access_token':meli.access_token} )
            print "response.content:", response.content
            rjson = response.json()
            if ("name" in rjson):
                # en el html deberia ir el link  para chequear on line esa categoría corresponde a sus productos.
                warning_model.info( title='MELI WARNING', message="Preparando importación de todas las categorías en "+str(category_root), message_html=response )
                if ("children_categories" in rjson):
                    #empezamos a iterar categorias
                    for child in rjson["children_categories"]:
                        ml_cat_id = child["id"]
                        if (ml_cat_id):
                            category_model.import_category(category_id=ml_cat_id)
                            if (RECURSIVE_IMPORT):
                                category_model.import_all_categories(category_root=ml_cat_id)
