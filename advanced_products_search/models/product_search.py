# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductSearch(models.Model):
    _name = "product.search"
    _description = 'Product Search Engine'

    so_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    name = fields.Char(string="Product Name")
    categ_id = fields.Many2one(comodel_name="product.category", string="Category")
    type = fields.Selection(selection=[('consu', 'Consumable'),
                                       ('service', 'Service'),
                                       ('product', 'Storable')], string="Type")
    default_code = fields.Char(string="Internal Reference")
    barcode = fields.Char(string="Barcode")
    lst_price_max = fields.Float(string="Max Sale price")
    lst_price_min = fields.Float(string="Min Sale price")
    product_ids = fields.Many2many(comodel_name="product.product", relation="product_search_product_product_rel")
    inserted_products = fields.One2many(comodel_name="inserted.product", inverse_name="wizard_id")
    prods_count = fields.Text(string='#of products found')


    @api.onchange('name', 'categ_id', 'type', 'default_code', 'barcode', 'lst_price_max', 'lst_price_min')
    def onchange_search_fields(self):
        q = """ SELECT pp.id  FROM product_product pp
                INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE pt.sale_ok = True  
            """

        if self.categ_id:
            q += " AND pt.categ_id = %s" % self.categ_id.id

        if self.type:
            q += " AND pt.type = '%s'" % self.type

        if self.default_code:
            default_code = self.default_code.replace("'", "''")
            q += " AND pp.default_code ilike  '%%%s%%' " % default_code

        if self.barcode:
            q += " AND pp.barcode ilike  '%%%s%%' " % self.barcode

        if self.name:
            name = self.name.replace("'", "''")
            if " " in self.name:
                words = name.split(" ")
                if words:
                    q += " AND ("
                    for w in words:
                        if words.index(w) == len(words) - 1:
                            q += " pt.name ilike '%%%s%%')" % w
                        else:
                            q += " pt.name ilike '%%%s%%' AND" % w
            else:
                q += " AND pt.name ilike '%%%s%%'" % name

        q_count = q.replace("SELECT pp.id", "SELECT count(pp.id)")
        self._cr.execute(q_count)
        count = int(self._cr.fetchall()[0][0])
        q += " ORDER BY pt.name"

        self.product_ids = None
        self.prods_count = None
        if count > 300:
            self.prods_count = '+300 products found! \n Please use more filters :)'
        elif count == 0:
            self.prods_count = 'No products found!'
        else:
            self._cr.execute(q)
            self.product_ids = [p[0] for p in self._cr.fetchall()]

        if self.lst_price_max:
            self.product_ids = self.product_ids.filtered(lambda p: p.lst_price <= self.lst_price_max)

        if self.lst_price_min:
            self.product_ids = self.product_ids.filtered(lambda p: p.lst_price >= self.lst_price_min)


    def reset(self):
        q = "DELETE FROM product_search_product_product_rel WHERE product_search_id=%s" % self.id
        self._cr.execute(q)
        reset_all_fields = """ UPDATE product_search SET default_code=null, type=null, categ_id=null,
                               name=null, barcode=null, lst_price_max=null, lst_price_min=null WHERE id = %s
                           """ % self.id
        self._cr.execute(reset_all_fields)
        return {'type': 'ir.actions.act_window',
                'name': "Products Search - %s" % self.so_id.name,
                'res_model': 'product.search',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
                }


    def close(self):
        q1 = "DELETE FROM product_search_product_product_rel WHERE product_search_id = %s " % self.id
        q2 = "DELETE FROM product_search WHERE id = %s " % self.id
        self._cr.execute(q1)
        self._cr.execute(q2)


    @api.model
    def do_insert_products(self, wizard_id, selected_prods_ids):
        wizard = self.env['product.search'].browse(wizard_id)
        so = wizard.so_id
        sol_obj = self.env['sale.order.line']
        for product in self.env['product.product'].browse(selected_prods_ids):
            price = product.lst_price
            next_sequence = so.order_line and max([l.sequence for l in so.order_line]) + 1 or 1
            vals = {'order_id': so.id,
                    'price_unit': price,
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': 1,
                    'sequence': next_sequence,
                    }
            sol_obj.create(vals)
        return selected_prods_ids


class InsertedProduct(models.Model):
    _name = "inserted.product"
    _description = 'Inserted Products through Search Engine'

    wizard_id = fields.Many2one(comodel_name="product.search", string="Search wizard")
    name = fields.Char(string='Product Name')
    default_code = fields.Char(string='Internal Reference')
    price_unit = fields.Char(string='Price Unit')
