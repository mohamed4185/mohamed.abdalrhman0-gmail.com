from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
import logging
_logger = logging.getLogger(__name__)
class acc_move(models.Model):

    _inherit = 'account.move'

class move_lines(models.Model):

    _inherit = 'account.move.line'

    jebal_pay_id = fields.Integer(string="Jebal Payment",index=True)
    jebal_check_id = fields.Integer(string="Jebal Check",index=True)
    jebal_nrom_pay_id = fields.Integer(string="Jebal Check", index=True)
    jebal_con_pay_id = fields.Integer(string="Jebal Check", index=True)
    date_maturity = fields.Date(string='Due date', index=True, required=False,
                                help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    cheques=fields.Boolean('cheques')
    @api.model
    def create(self,vals):
        res = super(move_lines,self).create(vals)
        res.date_maturity = False
        return res


class create_moves(models.Model):
    _name = 'create.moves'

    @api.multi
    def create_move_lines(self, **kwargs):
        self.accounts_agg(**kwargs)
        self.adjust_move_percentage(**kwargs)
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        company_currency = self.env['res.users'].search([('id', '=', self._uid)]).company_id.currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=datetime.today())._compute_amount_fields(kwargs['amount'], kwargs['src_currency'],
                                                         company_currency)
        move_vals = {
            'name': kwargs['move']['name'],
            'journal_id': kwargs['move']['journal_id'],
            'date': datetime.today(),
            'ref': kwargs['move']['ref'],
            'company_id': kwargs['move']['company_id'],
            'cheques':True

        }

        move = self.env['account.move'].with_context(check_move_validity=False).create(move_vals)
        _logger.info('Move line')
        for index in kwargs['debit_account']:
            debit_line_vals = {
                'name': kwargs['move_line']['name'],
                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'debit': (index['percentage'] / 100) * kwargs['amount'],
                'credit': credit,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
                'cheque':True

            }
            if 'analyitc_id' in index:
                debit_line_vals['analytic_account_id'] = index['analyitc_id']
                print('hellloooo')
                print(str(index['analyitc_id']))
            if 'jebal_pay_id' in kwargs['move_line']:
                debit_line_vals['jebal_pay_id'] =  kwargs['move_line']['jebal_pay_id']
            if 'jebal_check_id' in  kwargs['move_line']:
                debit_line_vals['jebal_check_id'] = kwargs['move_line']['jebal_check_id']
            if 'jebal_nrom_pay_id' in  kwargs['move_line']:
                debit_line_vals['jebal_nrom_pay_id'] = kwargs['move_line']['jebal_nrom_pay_id']
            if 'jebal_con_pay_id' in  kwargs['move_line']:
                debit_line_vals['jebal_con_pay_id'] = kwargs['move_line']['jebal_con_pay_id']
            debit_line_vals['move_id'] = move.id
            debit_line_vals['cheques']=True

            _logger.info('Debit')
            aml_obj.create(debit_line_vals)

        for index in kwargs['credit_account']:
            credit_line_vals = {
                'name': kwargs['move_line']['name'],
                'account_id': index['account'],
                'partner_id': kwargs['move_line']['partner_id'],
                'debit': credit,
                'credit': (index['percentage'] / 100) * kwargs['amount'],
                'amount_currency': -1 * amount_currency,
                'currency_id': currency_id,
            }
            if 'analyitc_id' in index:
                credit_line_vals['analytic_account_id'] = index['analyitc_id']
                print('hellloooo')
                print(str(index['analyitc_id']))
            if 'jebal_pay_id' in kwargs['move_line']:
                credit_line_vals['jebal_pay_id'] =  kwargs['move_line']['jebal_pay_id']
            if 'jebal_check_id' in  kwargs['move_line']:
                credit_line_vals['jebal_check_id'] = kwargs['move_line']['jebal_check_id']
            if 'jebal_nrom_pay_id' in  kwargs['move_line']:
                credit_line_vals['jebal_nrom_pay_id'] = kwargs['move_line']['jebal_nrom_pay_id']
            credit_line_vals['move_id'] = move.id
            credit_line_vals['cheques']=True
            aml_obj.create(credit_line_vals)
        # move.post()

    def adjust_move_percentage(self,**kwargs):
        # Debit
        tot_dens = 0.0
        tot_crds = 0.0
        for debs in kwargs['debit_account']:
            tot_dens+=debs['percentage']
        for crds in kwargs['credit_account']:
            tot_crds+=crds['percentage']
        percent = 100.0
        if tot_crds < 99 or tot_crds > 101:
            percent = tot_crds
        for i in range(len(kwargs['debit_account'])):
            kwargs['debit_account'][i]['percentage'] = round(kwargs['debit_account'][i]['percentage'],8)
        for index in kwargs['debit_account']:
            percent -= index['percentage']
        diff = 0.0
        if percent !=0.0:
            diff = percent / len(kwargs['debit_account'])
            for i in range(len(kwargs['debit_account'])):
                kwargs['debit_account'][i]['percentage'] +=diff
        #Credit
        percent = 100.0
        if tot_crds < 99 or tot_crds > 101:
            percent = tot_crds
        for i in range(len(kwargs['credit_account'])):
            kwargs['credit_account'][i]['percentage'] = round(kwargs['credit_account'][i]['percentage'], 8)
        for index in kwargs['credit_account']:
            percent -= index['percentage']
        diff = 0.0
        if percent != 0.0:
            diff = percent / len(kwargs['credit_account'])
            for i in range(len(kwargs['credit_account'])):
                kwargs['credit_account'][i]['percentage'] += diff

    def accounts_agg(self,**kwargs):
        all_crd_accs = {}
        for crd_accs in kwargs['credit_account']:
            if all_crd_accs and crd_accs['account'] in all_crd_accs:
                all_crd_accs[crd_accs['account']] += crd_accs['percentage']
            else:
                all_crd_accs[crd_accs['account']] = crd_accs['percentage']
        credit_account = []
        for acc_key in all_crd_accs:
            credit_account.append({'account': acc_key, 'percentage': all_crd_accs[acc_key]})
        kwargs['credit_account'] = credit_account
        all_crd_accs = {}
        for crd_accs in kwargs['debit_account']:
            if all_crd_accs and crd_accs['account'] in all_crd_accs:
                all_crd_accs[crd_accs['account']] += crd_accs['percentage']
            else:
                all_crd_accs[crd_accs['account']] = crd_accs['percentage']
        debit_account = []
        for acc_key in all_crd_accs:
            debit_account.append({'account': acc_key, 'percentage': all_crd_accs[acc_key]})
        kwargs['debit_account'] = debit_account
