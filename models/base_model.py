from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime


class SpotTVCompany(models.Model):
    _name= 'spot.tv.company'
    _description = 'Model for Spot TV Company'
#    _parent_store = True
 #   _parent_name = 'parent_id'

    name = fields.Char('Spot TV Company')
    description = fields.Html(sanitize=True, strip_style=False)
#    parent
  #  parent_path = fields.Char(index=True)
   # parent_id = fields.Many2one('spot.tv.company','Parent Media', ondelete='rtestrict', index=True)
   # child_ids = fields.One2many('spot.tv.company','parent_id', string='Child medias')

    media_seller = fields.Many2one('spot.media.seller', ondelete="set null")
    target_audience = fields.Many2one('spot.audience', ondelete='set null')
    prime_time_begin = fields.Float(string='Prime Time begin')
    prime_time_end = fields.Float(string='Prime Time end')
    vat = fields.Float(string='VAT')
    country = fields.Many2one('res.country',string='Country', ondelete='set null')
    own_media = fields.Boolean('Own Media')
    prime_time_factor = fields.Float(string='Prime Time Factor')

#    @api.constrains('parent_id')
 #   def _check_hierarchy(self):
  #      if not self._check_recursion():
   #         raise ValidationError('ERROR!You can not create recursion media group')

    def check_in_prime_time(self, date_time_start):
        fact_start = date_time_start.hour+ date_time_start.minute/100
        return (self.prime_time_begin<=fact_start<=self.prime_time_end)

    def get_budget_vat(self, budget_vat_less):
        return (1+self.vat/100)*budget_vat_less


class MapAdvertiserBrandProduct(models.Model):
    _name = 'spot.map.adv.brand.procat'
    _description = 'Model for mapping Advertiser Brand Product category'

    advertiser_raw_data = fields.Char('Represent Raw Advertiser')
    advertiser = fields.Many2one('spot.advertiser', string='Advertiser')
    brand_raw_data = fields.Char('Represent Raw Brand')
    brand = fields.Many2one('spot.brand', string='Brand')
    product_category_raw_data = fields.Char('Represent Raw Product Category')
    product_category = fields.Many2one('spot.product.category')
    is_zero_budget = fields.Boolean(string='Is zero budget?')

    @api.model
    def get_standart(self, adv_desc, brand_desc, procat_desc):
        search_model = self.env['spot.map.adv.brand.procat']
        search_domain = ['&']
        search_domain.append(('advertiser_raw_data', 'ilike', adv_desc))
        search_domain.append(('brand_raw_data', 'ilike', brand_desc))
        search_domain.append(('product_category_raw_data', 'ilike', procat_desc))
        return search_model.search(search_domain)
 

class AdvertiserMBAgency(models.Model):
    _name = 'spot.advertiser.mbage'
    _description = 'Model for Advertisers media buying agency'
    valid_from_date = fields.Date(string='Valid from date')
    advertiser = fields.Many2one('spot.advertiser')
    media_buying_agency = fields.Many2one('spot.media.buying.agency', string='Media Buying Agency')


class AdvertiserAdvertiseHolding(models.Model):
    _name = 'spot.advertiser.ahold'
    _description = 'Model for advertiser advertise holding'

    valid_from_date = fields.Date(string='Valid from date')
    advertiser = fields.Many2one('spot.advertiser')
    advertise_holding = fields.Many2one('spot.advertise.holding')


class SpotAudience(models.Model):
    _name = 'spot.audience'
    _description = 'Model for Audience'

    name = fields.Char(string='Audience')


class InnerBlockType(models.Model):
    _name = 'inner.block.type'
    _description = 'Model for inner block type'

    name = fields.Char(string='Inner Block Type')


class SpotAdvertiser(models.Model):
    _name = 'spot.advertiser'
    _description = 'model for advertiser'

    name = fields.Char(string='Advertiser')

    @api.model
    def _get_property(self, property_model_name, property_name, release_date, advertiser_id):
        property_model = self.env[property_model_name]
        search_domain = ['&']
        search_domain.append(('valid_from_date','<=',release_date))
        search_domain.append(('advertiser','=',advertiser_id))
        recs = property_model.search(search_domain, limit=1, order='valid_from_date desc')
        if recs:
            return recs[0][property_name].id
        else: return 0

    @api.model
    def _set_property(self, property_model_name, release_date, advertiser_id, property_name, property_value):
        property_model = self.env[property_model_name]
        rec_val = {'valid_from_date':release_date, 'advertiser':advertiser_id, property_name:property_value}
        new_rec = property_model.create(rec_val)
        return new_rec[0].id

    def get_advertise_holding(self, release_date, advertiser_id):
        return self._get_property('spot.advertiser.ahold', 'advertise_holding',release_date, advertiser_id) 

    def get_media_buying_agency(self, release_date, advertiser_id):
        return self._get_property('spot.advertiser.mbage', 'media_buying_agency', release_date, advertiser_id)

    def set_advertise_holding(self, release_date, advertiser, a_holding):
        return self._set_property('spot.advertiser.ahold', release_date, advertiser, 'advertise_holding', a_holding)

    def set_media_buying_agency(self, release_date, advertiser, mb_agency):
        return self._set_property('spot.advertiser.mbage', release_date, advertiser, 'media_buying_agency', mb_agency)


class SpotProductCategory(models.Model):
    _name = 'spot.product.category'
    _description = 'Model for product category'

    name = fields.Char('Product Category')


class SpotBrand(models.Model):
    _name = 'spot.brand'
    _description = 'Model for brand'

    name = fields.Char('Brand')


class SpotAdvertiseHolding(models.Model):
    _name = 'spot.advertise.holding'
    _description = 'Model for advertise holdings'

    name = fields.Char('Advertise holding')


class SpotMediaBuyingAgency(models.Model):
    _name = 'spot.media.buying.agency'
    _description = 'Model for media buying agency'

    name = fields.Char('Media buying agency')


class SpotMediaSeller(models.Model):
    _name = 'spot.media.seller'
    _description = 'Model for media seller'

    name = fields.Char('Media seller')


class SpotAdvertiseCategory(models.Model):
    _name = 'spot.advertise.category'
    _description = 'Model for advertise categories'

    name = fields.Char('Advertise category')


class SpotIndicator(models.Model):
    _name = 'spot.indicator'
    _description = 'Model for spot indicator'

    name = fields.Char('Name')


class PeriodYear(models.Model):
    _name = 'period.year'
    _description = 'Years'

    name = fields.Char('Year')
    begin_date = fields.Date(string='Begin at')
    end_date = fields.Date(string='End')


class PeriodMonth(models.Model):
    _name = 'period.month'
    _description = 'Month'

    name = fields.Char('Month')
    number_in_year = fields.Integer(string='Number in year')
