import numpy as np
import pandas as pd
from app.models import gordon_model, dcf_model, ddm_model, fcff_model, fcfe_model, relative_valuation, company_assets
from app.models.residual_income import calculate_residual_income


class Valuation:
    def __init__(self, financials, manual_input=None):
        """
        :param financials: DataFrame يحتوي على البيانات المالية التاريخية (مثل الدخل والميزانية والتدفقات النقدية)
        :param manual_input: dict بالقيم المدخلة يدويًا (أو من ملف Excel) لاستخدامها في النماذج التي تحتاج بيانات ثابتة
        """
        self.financials = financials
        self.manual_input = manual_input or {}

    def average_growth_rate(self, column, years=3):
        if column not in self.financials.columns or len(self.financials[column].dropna()) < years:
            return None
        data = self.financials[column].dropna().tail(years)
        try:
            cagr = (data.iloc[-1] / data.iloc[0]) ** (1 / (len(data)-1)) - 1
            return round(cagr, 4)
        except:
            return None

    def intrinsic_value_dcf(self):
        fcf_data = self.financials.get("Free Cash Flow", pd.Series(dtype=float)).dropna()
        if len(fcf_data) < 1:
            # جرب من القيم المدخلة يدويًا
            try:
                fcf = float(self.manual_input.get('FreeCashFlow'))
                growth = float(self.manual_input.get('GrowthRate', 0.03))
                discount = float(self.manual_input.get('DiscountRate', 0.1))
                terminal = float(self.manual_input.get('TerminalGrowth', 0.02))
                return dcf_model.discounted_cash_flow(fcf, growth, discount, terminal_growth=terminal)
            except:
                return None

        last_fcf = fcf_data.iloc[-1]
        growth = self.average_growth_rate("Free Cash Flow") or float(self.manual_input.get('GrowthRate', 0.03))
        discount = float(self.manual_input.get('DiscountRate', 0.1))
        terminal = float(self.manual_input.get('TerminalGrowth', 0.02))

        return dcf_model.discounted_cash_flow(last_fcf, growth, discount, terminal_growth=terminal)

    def intrinsic_value_gordon(self):
        try:
            dividend = float(self.manual_input.get('Dividend'))
            growth = float(self.manual_input.get('GrowthRate'))
            discount = float(self.manual_input.get('DiscountRate'))
            return gordon_model.gordon_growth(dividend, growth, discount)
        except:
            return None

    def intrinsic_value_ddm(self):
        try:
            dividend = float(self.manual_input.get('Dividend'))
            expected_return = float(self.manual_input.get('ExpectedReturn'))
            growth = float(self.manual_input.get('GrowthRate'))
            return ddm_model.dividend_discount_model(dividend, expected_return, growth)
        except:
            return None

    def intrinsic_value_fcff(self):
        try:
            fcff = float(self.manual_input.get('FCFF'))
            wacc = float(self.manual_input.get('WACC'))
            growth = float(self.manual_input.get('GrowthRate'))
            terminal = float(self.manual_input.get('TerminalGrowth', 0.02))
            return fcff_model.fcff_valuation(fcff, wacc, growth, terminal_growth=terminal)
        except:
            return None

    def intrinsic_value_fcfe(self):
        try:
            fcfe = float(self.manual_input.get('FCFE'))
            cost_equity = float(self.manual_input.get('CostOfEquity'))
            growth = float(self.manual_input.get('GrowthRate'))
            return fcfe_model.fcfe_valuation(fcfe, cost_equity, growth)
        except:
            return None

    def relative_valuations(self):
        try:
            return relative_valuation.relative_valuation(
                pe=float(self.manual_input.get('PE', 0)),
                eps=float(self.manual_input.get('EPS', 0)),
                pb=float(self.manual_input.get('PB', 0)),
                bvps=float(self.manual_input.get('BVPS', 0)),
                ev_ebitda=float(self.manual_input.get('EV_EBITDA', 0)),
                ebitda=float(self.manual_input.get('EBITDA', 0))
            )
        except:
            return {}

    def get_summary(self):
        return {
            "CAGR_Revenue": self.average_growth_rate("Revenue"),
            "CAGR_Earnings": self.average_growth_rate("Net Income"),
            "IntrinsicValue_DCF": self.intrinsic_value_dcf(),
            "IntrinsicValue_Gordon": self.intrinsic_value_gordon(),
            "IntrinsicValue_DDM": self.intrinsic_value_ddm(),
            "IntrinsicValue_FCFF": self.intrinsic_value_fcff(),
            "IntrinsicValue_FCFE": self.intrinsic_value_fcfe(),
            "Relative_Valuations": self.relative_valuations(),
        }
def calculate_residual_income(book_value_per_share, net_income, equity, required_return, shares_outstanding):
    capital_charge = equity * required_return
    residual_income = net_income - capital_charge
    fair_value = book_value_per_share + (residual_income / shares_outstanding)
    return round(fair_value, 2)

def run_residual_income(inputs):
    try:
        return calculate_residual_income(
            book_value_per_share=float(inputs['ri_book_value']),
            net_income=float(inputs['ri_net_income']),
            equity=float(inputs['ri_equity']),
            required_return=float(inputs['ri_required_return']) / 100,
            shares_outstanding=float(inputs['ri_shares_outstanding'])
        )
    except Exception as e:
        return f"خطأ: {str(e)}"
