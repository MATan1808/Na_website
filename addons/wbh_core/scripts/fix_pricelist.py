import odoo
from odoo.modules.registry import Registry
from odoo import api, SUPERUSER_ID, Command

registry = Registry('web_ban_hang_dev')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Check pricelists
    pricelists = env['product.pricelist'].search([])
    print('Pricelists count:', len(pricelists))
    if not pricelists:
        pl = env['product.pricelist'].create({
            'name': 'Bảng Giá Tiêu Chuẩn (VND / USD)',
            'currency_id': env.company.currency_id.id,
            'sequence': 1,
            'selectable': True,
        })
        print('Created default pricelist:', pl.id, pl.name)
    else:
        pl = pricelists[0]

    # Assign pricelist to all websites
    websites = env['website'].search([])
    for w in websites:
        print(f"Website {w.id}: {w.name}, current pricelists: {[p.name for p in w.pricelist_ids]}")
        if pl not in w.pricelist_ids:
            w.write({'pricelist_ids': [Command.link(pl.id)]})
            print(f"  -> Linked pricelist {pl.name} to website {w.name}")
    cr.commit()

    # Check products published
    for w in websites:
        w_env = env['product.template'].with_context(website_id=w.id)
        prods = w_env.search([('is_published', '=', True), ('sale_ok', '=', True)])
        print(f"Website {w.id} ({w.name}) published products: {len(prods)}")
        for p in prods[:3]:
            print(f"   - [{p.id}] {p.name} ({p.list_price})")
