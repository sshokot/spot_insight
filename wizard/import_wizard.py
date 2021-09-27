from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning
import xlrd
import base64
import datetime
import pytz
import pdb
from threading import Thread

class ImportRawDataWizard(models.TransientModel):
    """ This wizard is used to import from 
       xls file in new record raw data """
    _name = 'import.raw.data.wizard'
    _description = 'Wizard for import raw data from xls'

    import_file = fields.Binary(string='Import File (.xls)')
    res_id = fields.Integer(string='Resource ID', readonly=True,)
    state = fields.Selection([('choose','Choose'),('get','Get')],
        default='choose')
    data_sheets = fields.Char(string="Data sheets")
    budget_sheet = fields.Char(string="Sheet with budget data")
    read_time = fields.Char(string="Read data time")
    str_errors = fields.Char(string="Import errors")

    def action_read_file(self):
        self.ensure_one()
        if self.import_file:
            "Import file to read spot raw data"
            budget_pattern_list = ["дата выхода","release date"]
            spot_pattern_list = ["Spot TVCompany".lower()]
            decoded_data = base64.decodebytes(self.import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            str_data = ''
            budget_sheet = ''
            for sheet_name in wb.sheet_names():
                is_budget = False
                is_spot = False
                sheet = wb.sheet_by_name(sheet_name)
                rows = sheet.nrows
                cells = sheet.ncols
                str_data += ' '+sheet_name+': '+str(rows)+' rows;'
                if rows < 5 or cells < 5:
                    continue
                for cr_row in range(0,5):
                    for cr_cell in range(0,5):
                        cell_type = sheet.cell_type(cr_row, cr_cell)
                        cell_value = sheet.cell_value(cr_row, cr_cell)
                        if cell_type == 1:
                            if cell_value.lower() in budget_pattern_list:
                                is_budget = True
                                is_spot = False
                                budget_sheet = sheet_name
                                break
                            elif cell_value.lower() in spot_pattern_list:
                                is_budget = False
                                is_spot = True
                                break
                    if is_budget or is_spot:
                        break
            self.write({'data_sheets': str_data})
        else:
            raise ValidationError(_('Please select Excel file to import'))
        self.write({'state': 'get', 'budget_sheet':budget_sheet})
        return True

    def import_raw_data(self, act_model_name, act_sheet, date_mode, record_setting):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            act_model = self.env[act_model_name]
            sheet_name = act_sheet.name
            rows = act_sheet.nrows
            cells = act_sheet.ncols
            zero_date =  datetime.datetime(1899,12,31)
            str_errors = self.get_str_error()
            is_data = False
            print('START ROWS %s '%(sheet_name), str(rows), fields.Datetime.now().strftime("%d/%m/%Y,%H:%M:%S"))
            vals = []
            for cr_row in range(0, rows):
                search_domain = ['&']
                release_date = datetime.datetime(1900,1,1)
                fact_start_time = datetime.datetime(1900,1,1)
                record_val = {}
                for cr_cell in range(0, cells):
                    cell_type = act_sheet.cell_type(cr_row, cr_cell)
                    cell_value = act_sheet.cell_value(cr_row, cr_cell)
                    if not cell_value:
                        #str_errors += ' emty val ('+str(cr_row)+','+str(cr_cell)+')' 
                        continue
                    rec_value = cell_value
                    if cell_type == 3:
                        is_data = True
                        rec_value = xlrd.xldate.xldate_as_datetime(cell_value,date_mode)
                        if cell_value < 1:
                            time_delta = rec_value - zero_date
                            rec_value = release_date + time_delta
                            rec_value = self.convert_to_utc(rec_value)
                        elif cell_value < 2:
                            time_delta = rec_value - zero_date
                            rec_value = release_date + time_delta
                            rec_value = self.convert_to_utc(rec_value)
                        else:
                            release_date = rec_value
                    elif cell_type == 1:
                        rec_value = cell_value.encode('utf-8')
                    if cr_cell in record_setting:
                        record_val[record_setting[cr_cell]] = rec_value
                if is_data:
                    self.check_records(act_model, record_val, vals, str_errors)
                    # break
                #if cr_row >5:
                #    break
            if vals:
                act_model.create(vals)
            print('END ROWS ', str(rows), fields.Datetime.now().strftime("%d/%m/%Y,%H:%M:%S"))
            if str_errors:
                self.write({'str_errors':str_errors})
            new_cr.commit()
            new_cr.close()

    def convert_to_utc(self, tz_datetime):
        fmt = '%Y-%m-%d %H:%M:%S'
        utc_tz = pytz.timezone('UTC')
        user_tz = pytz.timezone(self.env.user.tz)
        result_utc = user_tz.localize(tz_datetime).astimezone(utc_tz)
        return result_utc.strftime(fmt)

    def import_budget_raw_data(self, sheet, date_mode):
        m_budget_raw_data = 'budget.raw.data'
        #budget.raw.data: release_date - 0 cell, spot_tv_company - 1 cell,
        #                 time_keeping - 2 cell, budget_vat_less - 3 cell, fact_start_time - 4 cell
        record_setting = {0:'release_date', 1:'spot_tv_company', 2:'time_keeping', 3:'budget_vat_less',
            4:'fact_start_time'}
        self.import_raw_data(m_budget_raw_data, sheet, date_mode, record_setting)

    def import_spot_raw_data(self, sheet, date_mode):
        m_spot_raw_data = 'spot.raw.data'
  # spot.raw.model: spot_tv_company - 0 cell, release_date - 1 cell, spot_start_time - 2 cell,
  #     spot_end_time - 3 cell, spot_duration - 4 cell, advertiser - 5 cell, brand - 6 cell,
  #     model_name - 7 cell, article_level - 8 cell, clip_description - 9 cell, program - 10 cell,
  #     spot_cost - 11 cell, break_title - 12 cell, spot_position - 13 cell, spots_count - 14 cell,
  #     total_ind - 15 cell, all_18 - 16 cell, all_6_54 - 17 cell
        record_setting = {0:'spot_tv_company', 1:'release_date', 2:'spot_start_time', 3:'spot_end_time',
            4:'spot_duration',5:'advertiser', 6:'brand', 7:'model_name', 8:'article_level', 9:'clip_description',
            10:'program', 11:'spot_cost', 12:'break_title', 13:'spot_position', 14:'spots_count', 15:'total_ind',
            16:'all_18', 17:'all_6_54'}
        self.import_raw_data(m_spot_raw_data, sheet, date_mode, record_setting)

    def import_open_invent_raw_data(self, act_sheet, date_mode):
        act_model = self.env['open.inventory.raw.data']
        record_setting = {0:'data_date', 1:'spot_tv_company', 2:'start_time', 3:'all_18', 4:'total_ind', 5:'all_6_54'}
        sheet_name = act_sheet.name; rows = act_sheet.nrows; cells = act_sheet.ncols
        ZERO_DATE =  datetime.datetime(1899,12,31)
        str_errors = self.get_str_error()
        date_cell = 'Date >>'.lower()
        is_data = False
        data_date = ZERO_DATE
        SPOT_TV = ''
        print('START ROWS %s '%(sheet_name), str(rows), fields.Datetime.now().strftime("%d/%m/%Y,%H:%M:%S"))
        vals = []
        for cr_row in range(0, rows):
        #    pdb.set_trace()
        #    search_domain = ['&']
            release_date = datetime.datetime(1900,1,1)
            fact_start_time = datetime.datetime(1900,1,1)
            record_val = {}
            for cr_cell in range(0, cells):
                 cell_type = act_sheet.cell_type(cr_row, cr_cell)
                 cell_value = act_sheet.cell_value(cr_row, cr_cell)
                 if not cell_value:
                     if cr_cell == 0 and data_date != ZERO_DATE:
                         record_val[record_setting[cr_cell]] = data_date
                     elif cr_cell == 1 and SPOT_TV:
                         record_val[record_setting[cr_cell]] = SPOT_TV
                       #str_errors += ' emty val ('+str(cr_row)+','+str(cr_cell)+')'
                     if cr_cell == 2 and is_data:
                         break
                     else:
                         continue
                 elif cr_cell == 1:
                     SPOT_TV = cell_value.encode('utf-8')
                     continue
                 elif cr_cell == 2:
                     if cell_value.lower() != 'start time':
                         is_data = True
                 if cell_type == 1 and  cell_value.lower() == date_cell:
         #   next cell is date str, for example 01.12.2021 - 31.12.2021, only get begin date
                     str_date = act_sheet.cell_value(cr_row, (cr_cell+1))[:10]
                     data_date = datetime.datetime.strptime(str_date,"%d.%m.%Y")
                     break
                 if cell_value and cr_cell >1:
                     rec_value = cell_value
                     if cr_cell in record_setting:
                         record_val[record_setting[cr_cell]] = rec_value
            if is_data and data_date != ZERO_DATE:
            #    print('RECORD ', record_val)
                self.check_records(act_model, record_val, vals, str_errors)
                # break
            #if cr_row >10:
            #    break
        if vals:
            act_model.create(vals)
        print('END ROWS ', str(rows), fields.Datetime.now().strftime("%d/%m/%Y,%H:%M:%S"))
        if str_errors:
            self.write({'str_errors':str_errors})

    def check_records(self, act_model, record_val, vals, str_errors):
        search_domain = ['&']
#        try:
        for k, v in record_val.items():
            search_domain.append((k,'=',v))
        act_recs = act_model.search(search_domain)
        if not act_recs:
            vals.append(record_val)
 #       except (ValueError, AssertionError) as e:
 #           str_errors += '  search error '+str(search_domain)
 #           print('ERRORS ',str_errors)


    def action_import_data(self):
        self.ensure_one()
        if self.import_file:
            decoded_data = base64.decodebytes(self.import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            date_mode = wb.datemode
            full_read_time = 'START '+fields.Datetime.now().strftime("%d/%m/%Y,%H:%M:%S")
            allThread = []
            for sheet_name in wb.sheet_names():
                act_sheet = wb.sheet_by_name(sheet_name)
                if sheet_name == self.budget_sheet:
                     thr = Thread(target=self.import_budget_raw_data, args=(act_sheet, date_mode))
                     thr.start()
                     allThread.append(thr)
               #     self.import_budget_raw_data(act_sheet, date_mode)
                else:
                     thr = Thread(target=self.import_spot_raw_data, args=(act_sheet, date_mode))
                     thr.start()
                     allThread.append(thr)
               #     self.import_spot_raw_data(act_sheet, date_mode)
                    #break
            if allThread:
                for thr in allThread:
                    thr.join()
            full_read_time += ' - END '+fields.Datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
            self.write({'read_time': full_read_time}) 
        else:
            raise ValidationError(_('Error read data'))
        return True

    def action_import_open_inventory_data(self):
        self.ensure_one()
        if self.import_file:
            decoded_data = base64.decodebytes(self.import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            date_mode = wb.datemode
            full_read_time = 'START ' + fields.Datetime.now().strftime("%d/%m/%Y,%H:%M:%S")
            for sheet_name in wb.sheet_names():
                act_sheet = wb.sheet_by_name(sheet_name)
                self.import_open_invent_raw_data(act_sheet, date_mode)
            full_read_time += ' - END '+fields.Datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        else:
            raise ValidationError(_('Error read data'))
        return True

    def action_import_audience_indicator_data(self):
        self.ensure_one()
        if self.import_file:
            decoded_data = base64.decodebytes(self.import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            date_mode = wb.datemode
            full_read_time = 'START ' + fields.Datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            for sheet_name in wb.sheet_names():
                act_sheet = wb.sheet_by_name(sheet_name)
                self.import_audience_raw_data(act_sheet, date_mode)
            full_read_time = '- END ' + fields.Datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    def get_str_error(self):
        return  self.str_errors if self.str_errors else ''

    def import_audience_raw_data(self, act_sheet, date_mode):
        act_model = self.env['audience.indicator.raw.data']
        record_setting = {1:'spot_tv_company', 2:'data_date', 3:'rtg6', 4:'rtg6_54', 5:'rtg18', 6:'share6', 7:'share6_54', 8:'share18'}
        sheet_name = act_sheet.name; nrows = act_sheet.nrows; ncols = act_sheet.ncols
        ZERO_DATE = datetime.datetime(1899,12,31)
        str_errors = self.get_str_error()
        is_data = False
        data_date = ZERO_DATE
        vals = []
        for cr_row in range(0, nrows):
            record_vals = {}
            for cr_cell in range(1, ncols):
                cell_type = act_sheet.cell_type(cr_row, cr_cell)
                cell_value = act_sheet.cell_value(cr_row, cr_cell)
                if cell_value:
                    if cell_type == 1:
                        if cell_value.lower() == 'channels':
                            is_data = True; break
                        if cr_cell == 2 and is_data:
                            str_date = cell_value[:10]
                            rec_value = datetime.datetime.strptime(str_date, '%d.%m.%Y')
                        else:
                            rec_value = cell_value.encode('utf-8')
                    else:
                        rec_value = cell_value
                    if is_data:
                        record_vals[record_setting[cr_cell]] = rec_value
            if is_data:
                self.check_records(act_model, record_vals, vals, str_errors)
            #if cr_row > 10:
            #    break
        if vals:
            act_model.create(vals)
        if str_errors:
            self.write({'str_errors':str_errors})

    def import_desc_standart(self):
        act_model = self.env['spot.map.adv.brand.procat']
        etl_model = self.env['etl.spot.raw.data']
        if self.import_file:
            decoded_data = base64.decodebytes(self.import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            for sheet_name in wb.sheet_names():
                act_sheet = wb.sheet_by_name(sheet_name)
                nrows = act_sheet.nrows; ncols = act_sheet.ncols
                recs = []; str_errors = ''
                for cr_row in range(0, nrows):
                    adv_desc = act_sheet.cell_value(cr_row, 0)
                    brand_desc = act_sheet.cell_value(cr_row, 1)
                    procat_desc = act_sheet.cell_value(cr_row, 2)
                    adv_stand = etl_model.get_model_record('spot.advertiser', act_sheet.cell_value(cr_row,3))
                    brand_stand = etl_model.get_model_record('spot.brand', act_sheet.cell_value(cr_row, 4))
                    procat_stand = etl_model.get_model_record('spot.product.category', act_sheet.cell_value(cr_row, 5))
                    rec_vals = {'advertiser_raw_data':adv_desc, 'brand_raw_data':brand_desc, 'product_category_raw_data':procat_desc,
                                'advertiser':adv_stand, 'brand': brand_stand, 'product_category': procat_stand}
                    self.check_records(act_model, rec_vals, recs, str_errors)
                if recs:
                    act_model.create(recs)

    def import_adv_mba_aholding(self):
        adv_model = self.env['spot.advertiser']
        etl_model = self.env['etl.spot.raw.data']
        if self.import_file:
            release_date = datetime.datetime(2019,1,1)
            decoded_data = base64.decodebytes(self.import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            act_sheet = wb.sheet_by_index(1)
            nrows = act_sheet.nrows
            for cr_row in range(0,nrows):
                adv_desc = act_sheet.cell_value(cr_row, 3)
                mb_agency_desc = act_sheet.cell_value(cr_row, 4)
                adv_holding_desc = act_sheet.cell_value(cr_row, 5)
                adv = etl_model.get_model_record('spot.advertiser', adv_desc)
                mb_agency = etl_model.get_model_record('spot.media.buying.agency', mb_agency_desc)
                adv_holding = etl_model.get_model_record('spot.advertise.holding', adv_holding_desc)
                adv_model.set_media_buying_agency(release_date, adv, mb_agency)
                adv_model.set_advertise_holding(release_date, adv, adv_holding)

    def import_historic_data(self):
        etl_model = self.env['etl.spot.raw.data']
        spot_tv_model = self.env['spot.tv.company']
        import_raw_m = self.env['import.raw.data.wizard']
        storage_model = self.env['spot.storage.data']
        grp_model = self.env['spot.overall.rating.grp']
        if self.import_file:
            decoded_data = base64.decodebytes(self.import_file)
            wb = xlrd.open_workbook(file_contents=decoded_data)
            act_sheet = wb.sheet_by_index(0)
            nrows = act_sheet.nrows; vals=[]; str_error = ''
            grp_data = {}
            for cr_row in range(1, nrows):
                rec_vals = {}
                tv_desc = act_sheet.cell_value(cr_row, 1)
                adv_desc = act_sheet.cell_value(cr_row, 2)
                brand_desc = act_sheet.cell_value(cr_row, 3)
                procat_desc = act_sheet.cell_value(cr_row, 4)
                aholding_desc = act_sheet.cell_value(cr_row, 5)
                mbagency_desc = act_sheet.cell_value(cr_row, 6)
                msel_desc = act_sheet.cell_value(cr_row, 7)
                year = act_sheet.cell_value(cr_row, 8)
                month = act_sheet.cell_value(cr_row, 9)
                budget_vale = act_sheet.cell_value(cr_row, 10)
                duration = act_sheet.cell_value(cr_row, 11)
                grp_6 = float(act_sheet.cell_value(cr_row, 12))
                grp_18 = float(act_sheet.cell_value(cr_row, 13))
                grp_6_54 = float(act_sheet.cell_value(cr_row, 14))
                rec_vals['release_date'] = datetime.datetime(int(year), int(month), 1)
                rec_vals['tv_company'] = etl_model.get_model_record('spot.tv.company', tv_desc)
                rec_vals['brand'] = etl_model.get_model_record('spot.brand', brand_desc)
                rec_vals['advertiser'] = etl_model.get_model_record('spot.advertiser', adv_desc)
                rec_vals['advertise_holding'] = etl_model.get_model_record('spot.advertise.holding', aholding_desc)
                rec_vals['media_buying_agency'] = etl_model.get_model_record('spot.media.buying.agency', mbagency_desc)
                rec_vals['product_category'] = etl_model.get_model_record('spot.product.category', procat_desc)
                rec_vals['media_seller'] = etl_model.get_model_record('spot.media.seller', msel_desc)
                rec_vals['duration'] = duration
                rec_vals['budget_vat_less'] = budget_vale
                rec_tv_company = spot_tv_model.browse(rec_vals['tv_company'])
                rec_vals['budget_vat'] = rec_tv_company.get_budget_vat(rec_vals['budget_vat_less'])
                self.check_records(storage_model, rec_vals, vals, str_error)
                key_grp = (rec_vals['release_date'],rec_vals['tv_company'], rec_vals['brand'], rec_vals['advertiser'], rec_vals['product_category'])
                if grp_6!=0 or grp_18!=0 or grp_6_54!=0:
                    grp_val={'grp_6':grp_6, 'grp_18':grp_18, 'grp_6_54':grp_6_54}
                    grp_data[key_grp] = grp_val
                if cr_row>10: break
            if vals:
                new_recs = storage_model.create(vals)
                for new_rec in new_recs:
                    storage_id = new_rec.id
                    key_grp = (new_rec.release_date, new_rec.tv_company, new_rec.brand, new_rec.advertiser, new_rec.product_category)
                    grp_val = grp_data.get(key_grp)
                    if grp_val:
                        grp_model.set_grp_rating(storage_id, audience_6, grp_val['grp_6'])
                        grp_model.set_grp_rating(storage_id, audience_18, grp_val['grp_18'])
                        grp_model.set_grp_rating(storage_id, audience_6_54, grp_val['grp_6_54'])



